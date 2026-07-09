import re

from app.models.parcel import Parcel


TRUST_OR_ESTATE_PATTERN = re.compile(r"\b(TRUST|TRUSTEES|ESTATE)\b", re.IGNORECASE)
LLC_PATTERN = re.compile(r"\b(LLC|LP|INC|CORP|CO\b|COMPANY|HOLDINGS|PROPERTIES|INVESTMENTS)\b", re.IGNORECASE)


def calculate_seller_probability(parcel: Parcel, absentee_owner: bool) -> int:
    score = 5

    if absentee_owner:
        score += 25

    if parcel.years_owned and parcel.years_owned >= 25:
        score += 30
    elif parcel.years_owned and parcel.years_owned >= 15:
        score += 20
    elif parcel.years_owned and parcel.years_owned >= 10:
        score += 10

    owner_name = parcel.owner_name or ""
    if TRUST_OR_ESTATE_PATTERN.search(owner_name):
        score += 15
    elif LLC_PATTERN.search(owner_name) and not parcel.developer_owned:
        score += 5

    if parcel.adjacent_developer_owned:
        score += 10

    if parcel.tax_delinquent:
        score += 20

    if parcel.developer_owned:
        score -= 35

    return max(0, min(score, 100))