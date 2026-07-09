from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AssessmentResponse(BaseModel):
    tax_year: int
    land_value: float
    improvement_value: float
    total_value: float

    model_config = {
        "from_attributes": True,
    }


class ParcelResponse(BaseModel):
    parcel_number: str
    gpin: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zoning: str | None = None
    property_type: str | None = None
    neighborhood: str | None = None
    lot_size: float | None = None
    years_owned: int | None = None
    sia_flag: bool | None = None
    developer_owned: bool | None = None
    adjacent_developer_owned: bool | None = None
    tax_delinquent: bool | None = None
    tax_lien_amount: float | None = None
    owner_name: str | None = None
    owner_address: str | None = None
    owner_city_state: str | None = None
    owner_zip_code: str | None = None

    latest_assessment: AssessmentResponse | None = None
    estimated_units: int | None = None
    seller_probability: int | None = None
    offer_low: float | None = None
    offer_high: float | None = None
    suggested_offer: float | None = None

    model_config = {
        "from_attributes": True,
    }


class OpportunityResponse(BaseModel):
    parcel_number: str
    address: str | None = None
    owner: str | None = None
    owner_address: str | None = None
    owner_city_state: str | None = None
    owner_zip_code: str | None = None
    zoning: str | None = None
    property_type: str | None = None
    neighborhood: str | None = None
    acres: float | None = None
    years_owned: int | None = None
    sia_flag: bool | None = None
    adjacent_developer_owned: bool | None = None
    estimated_units: int | None = None
    seller_probability: int | None = None
    offer_low: float | None = None
    offer_high: float | None = None
    suggested_offer: float | None = None
    tax_delinquent: bool | None = None
    tax_lien_amount: float | None = None
    absentee_owner: bool
    vk_score: int
    latest_assessment: AssessmentResponse | None = None

    model_config = {
        "from_attributes": True,
    }
