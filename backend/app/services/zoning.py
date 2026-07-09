from app.models.parcel import Parcel


RESIDENTIAL_ZONING_CODES = {
    "R-A",
    "R-B",
    "R-C",
    "RN-A",
    "RX-3",
    "RX-5",
}


UNITS_PER_SQFT_BY_ZONE = {
    "R-A": 1 / 10000,
    "R-B": 1 / 5000,
    "R-C": 1 / 3500,
    "RN-A": 1 / 3000,
    "RX-3": 1 / 1800,
    "RX-5": 1 / 1200,
}


def estimate_units(parcel: Parcel) -> int | None:
    if parcel.zoning not in RESIDENTIAL_ZONING_CODES:
        return None
    if parcel.lot_size is None or parcel.lot_size <= 0:
        return None

    ratio = UNITS_PER_SQFT_BY_ZONE.get(parcel.zoning)
    if ratio is None:
        return None

    lot_sqft = parcel.lot_size * 43560
    units = int(lot_sqft * ratio)
    return max(1, units)