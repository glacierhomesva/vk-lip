import re

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.assessment import Assessment
from app.models.parcel import Parcel
from app.schemas.parcel import AssessmentResponse, OpportunityResponse
from app.services.offers import estimate_offer_range
from app.services.scoring import calculate_vk_score
from app.services.seller import calculate_seller_probability
from app.services.zoning import RESIDENTIAL_ZONING_CODES, estimate_units

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def normalize_address(value: str | None) -> str:
    if not value:
        return ""
    normalized = re.sub(r"[^A-Z0-9 ]+", "", value.upper())
    return " ".join(normalized.split())


@router.get("", response_model=list[OpportunityResponse])
@router.get("/", response_model=list[OpportunityResponse])
def opportunities(
    parcel_number: str | None = None,
    zoning: str | None = None,
    neighborhood: str | None = None,
    min_sqft: float | None = None,
    years_owned_min: int | None = None,
    min_estimated_units: int | None = None,
    sia_only: bool = False,
    adjacent_developer_owned_only: bool = False,
    tax_delinquent_only: bool = False,
    min_tax_lien_amount: float | None = None,
    min_suggested_offer: float | None = None,
    max_suggested_offer: float | None = None,
    min_acres: float = 0.5,
    absentee_only: bool = False,
    sort_by: str = "vk_score",
    limit: int = 100,
    db: Session = Depends(get_db),
):

    query = db.query(Parcel)

    if parcel_number:
        query = query.filter(Parcel.parcel_number == parcel_number)
    else:
        query = query.filter(Parcel.zoning.in_(RESIDENTIAL_ZONING_CODES))

        if zoning:
            query = query.filter(Parcel.zoning == zoning)

        if neighborhood:
            query = query.filter(func.lower(Parcel.neighborhood) == neighborhood.strip().lower())

        if min_sqft is not None and min_sqft > 0:
            min_acres_needed = min_sqft / 43560.0
            query = query.filter(Parcel.lot_size >= min_acres_needed)
        else:
            query = query.filter(Parcel.lot_size >= min_acres)

        if years_owned_min is not None:
            query = query.filter(Parcel.years_owned >= years_owned_min)

        if sia_only:
            query = query.filter(Parcel.sia_flag.is_(True))

        if adjacent_developer_owned_only:
            query = query.filter(Parcel.adjacent_developer_owned.is_(True))

    if tax_delinquent_only:
        query = query.filter(Parcel.tax_delinquent.is_(True))

    if min_tax_lien_amount is not None:
        query = query.filter(Parcel.tax_lien_amount >= min_tax_lien_amount)

    parcels = query.limit(limit).all()

    results = []

    for p in parcels:
        absentee = False
        if p.owner_address and p.address:
            absentee = normalize_address(p.owner_address) != normalize_address(p.address)

        if absentee_only and not absentee:
            continue

        assessment = (
            db.query(Assessment)
            .filter(Assessment.parcel_number == p.parcel_number)
            .order_by(Assessment.tax_year.desc())
            .first()
        )

        latest_assessment = (
            AssessmentResponse(
                tax_year=assessment.tax_year,
                land_value=float(assessment.land_value),
                improvement_value=float(assessment.improvement_value),
                total_value=float(assessment.total_value),
            ) if assessment else None
        )

        estimated_units = estimate_units(p)
        if min_estimated_units is not None and (estimated_units or 0) < min_estimated_units:
            continue

        assessed_value = None
        if assessment and assessment.total_value is not None:
            assessed_value = float(assessment.total_value)
        elif p.total_assessment is not None:
            assessed_value = float(p.total_assessment)

        seller_probability = calculate_seller_probability(p, absentee)
        offer_low, offer_high, suggested_offer = estimate_offer_range(
            p,
            assessed_value,
            seller_probability,
            estimated_units,
        )

        if min_suggested_offer is not None and (suggested_offer is None or suggested_offer < min_suggested_offer):
            continue
        if max_suggested_offer is not None and (suggested_offer is None or suggested_offer > max_suggested_offer):
            continue

        vk_score = calculate_vk_score(p)

        results.append({
            "parcel_number": p.parcel_number,
            "address": p.address,
            "owner": p.owner_name,
            "owner_address": p.owner_address,
            "owner_city_state": p.owner_city_state,
            "owner_zip_code": p.owner_zip_code,
            "zoning": p.zoning,
            "property_type": p.property_type,
            "neighborhood": p.neighborhood,
            "acres": p.lot_size,
            "years_owned": p.years_owned,
            "sia_flag": p.sia_flag,
            "adjacent_developer_owned": p.adjacent_developer_owned,
            "estimated_units": estimated_units,
            "seller_probability": seller_probability,
            "offer_low": offer_low,
            "offer_high": offer_high,
            "suggested_offer": suggested_offer,
            "tax_delinquent": p.tax_delinquent,
            "tax_lien_amount": float(p.tax_lien_amount) if p.tax_lien_amount is not None else None,
            "absentee_owner": absentee,
            "vk_score": vk_score,
            "latest_assessment": latest_assessment,
        })

    sort_key = {
        "vk_score": lambda item: item["vk_score"],
        "seller_probability": lambda item: item["seller_probability"] or 0,
        "estimated_units": lambda item: item["estimated_units"] or 0,
        "suggested_offer": lambda item: item["suggested_offer"] or 0,
        "tax_lien_amount": lambda item: item["tax_lien_amount"] or 0,
    }.get(sort_by, lambda item: item["vk_score"])

    results.sort(key=sort_key, reverse=True)

    return results
