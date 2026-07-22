from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.assessment import Assessment
from app.models.parcel import Parcel
from app.schemas.parcel import AssessmentResponse, ParcelResponse
from app.services.offers import estimate_offer_range
from app.services.seller import calculate_seller_probability
from app.services.zoning import estimate_units

router = APIRouter(prefix="/parcels", tags=["parcels"])


def as_float(value: object | None) -> float | None:
    return float(value) if value is not None else None


def parcel_to_dict(parcel: Parcel) -> Dict[str, Any]:
    return {
        "id": parcel.id,
        "parcel_number": parcel.parcel_number,
        "gpin": parcel.gpin,
        "street_number": parcel.street_number,
        "street_name": parcel.street_name,
        "unit": parcel.unit,
        "address": parcel.address,
        "city": parcel.city,
        "state": parcel.state,
        "zip_code": parcel.zip_code,
        "owner_name": parcel.owner_name,
        "mailing_address": parcel.mailing_address,
        "zoning": parcel.zoning,
        "lot_size": parcel.lot_size,
        "land_value": float(parcel.land_value) if parcel.land_value is not None else None,
        "improvement_value": float(parcel.improvement_value) if parcel.improvement_value is not None else None,
        "total_assessment": float(parcel.total_assessment) if parcel.total_assessment is not None else None,
        "latitude": parcel.latitude,
        "longitude": parcel.longitude,
        "created_at": parcel.created_at,
        "updated_at": parcel.updated_at,
    }


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[ParcelResponse])
def list_parcels(limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)) -> list[ParcelResponse]:
    parcels = db.query(Parcel).limit(limit).all()
    return parcels


@router.get("/search", response_model=list[ParcelResponse])
def search_parcels(
    street: str | None = None,
    zoning: str | None = None,
    min_acres: float | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[ParcelResponse]:
    query = db.query(Parcel)

    if street:
        query = query.filter(Parcel.address.ilike(f"%{street}%"))

    if zoning:
        query = query.filter(Parcel.zoning == zoning)

    if min_acres:
        query = query.filter(Parcel.lot_size >= min_acres)

    parcels = query.limit(limit).all()
    return parcels


@router.get("/{parcel_number}", response_model=ParcelResponse)
def get_parcel(parcel_number: str, db: Session = Depends(get_db)) -> ParcelResponse:

    parcel = (
        db.query(Parcel)
        .filter(Parcel.parcel_number == parcel_number)
        .first()
    )

    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    assessment = (
        db.query(Assessment)
        .filter(Assessment.parcel_number == parcel_number)
        .order_by(Assessment.tax_year.desc())
        .first()
    )

    absentee = False
    if parcel.owner_address and parcel.address:
        absentee = parcel.owner_address.upper() not in parcel.address.upper()

    estimated_units = estimate_units(parcel)
    seller_probability = calculate_seller_probability(parcel, absentee)
    assessed_value = None
    if assessment and assessment.total_value is not None:
        assessed_value = float(assessment.total_value)
    elif parcel.total_assessment is not None:
        assessed_value = float(parcel.total_assessment)

    offer_low, offer_high, suggested_offer = estimate_offer_range(
        parcel,
        assessed_value,
        seller_probability,
        estimated_units,
    )

    return ParcelResponse(
        parcel_number=parcel.parcel_number,
        gpin=parcel.gpin,
        address=parcel.address,
        city=parcel.city,
        state=parcel.state,
        zoning=parcel.zoning,
        property_type=parcel.property_type,
        neighborhood=parcel.neighborhood,
        lot_size=parcel.lot_size,
        owner_name=parcel.owner_name,
        owner_address=parcel.owner_address,
        owner_city_state=parcel.owner_city_state,
        owner_zip_code=parcel.owner_zip_code,
        tax_delinquent=parcel.tax_delinquent,
        tax_lien_amount=float(parcel.tax_lien_amount) if parcel.tax_lien_amount is not None else None,
        estimated_units=estimated_units,
        seller_probability=seller_probability,
        offer_low=offer_low,
        offer_high=offer_high,
        suggested_offer=suggested_offer,
        latest_assessment=AssessmentResponse(
            tax_year=assessment.tax_year,
            land_value=as_float(assessment.land_value),
            improvement_value=as_float(assessment.improvement_value),
            total_value=as_float(assessment.total_value),
        ) if assessment else None,
    )
