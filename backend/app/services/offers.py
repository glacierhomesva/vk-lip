from app.models.parcel import Parcel


def _round_thousand(value: float) -> float:
    return round(value / 1000) * 1000


def estimate_offer_range(
    parcel: Parcel,
    assessed_value: float | None,
    seller_probability: int,
    estimated_units: int | None,
) -> tuple[float | None, float | None, float | None]:
    if assessed_value is None or assessed_value <= 0:
        return None, None, None

    base_ratio = 0.70

    if seller_probability >= 80:
        base_ratio += 0.10
    elif seller_probability >= 60:
        base_ratio += 0.06
    elif seller_probability >= 40:
        base_ratio += 0.03

    if estimated_units and estimated_units >= 4:
        base_ratio += 0.07
    elif estimated_units and estimated_units >= 2:
        base_ratio += 0.03

    if parcel.adjacent_developer_owned:
        base_ratio += 0.03

    if parcel.developer_owned:
        base_ratio -= 0.08

    if parcel.tax_delinquent:
        base_ratio += 0.04

    low_ratio = max(0.55, min(base_ratio - 0.05, 0.92))
    high_ratio = max(low_ratio, min(base_ratio + 0.05, 0.98))

    low = _round_thousand(assessed_value * low_ratio)
    high = _round_thousand(assessed_value * high_ratio)
    suggested = _round_thousand((low + high) / 2)
    return low, high, suggested