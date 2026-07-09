import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from shapely.geometry import shape
from shapely.strtree import STRtree
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.assessment import Assessment  # noqa: F401
from app.models.parcel import Parcel

ROOT = Path(__file__).resolve().parents[3]
SALES_CSV_FILE = ROOT / "data/raw/real_estate_sales.csv"
BOUNDARY_DETAILS_CSV_FILE = ROOT / "data/raw/parcel_boundary_details.csv"
BOUNDARIES_GEOJSON_FILE = ROOT / "data/raw/parcel_boundaries.geojson"

NEIGHBORHOOD_PATTERNS = [
    ("BELMONT", re.compile(r"\bBELMONT\b", re.IGNORECASE)),
    ("FIFEVILLE", re.compile(r"\bFIFEVILLE\b", re.IGNORECASE)),
]

DEVELOPER_OWNER_PATTERN = re.compile(
    r"\b(LLC|LP|L P|INC|CORP|CORPORATION|HOLDINGS|PROPERTIES|INVESTMENTS|VENTURES|DEVELOPMENT|DEVELOPERS|REALTY|GROUP|PARTNERS|ASSOCIATES|COMPANY|CO\b)\b",
    re.IGNORECASE,
)


def empty_or_none(value: Optional[object]) -> Optional[str]:
    if value is None:
        return None
    stripped = str(value).strip()
    return stripped if stripped else None


def parse_sale_date(value: Optional[str]) -> Optional[datetime]:
    normalized = empty_or_none(value)
    if normalized is None:
        return None
    try:
        return datetime.strptime(normalized, "%Y/%m/%d %H:%M:%S+00").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def infer_neighborhood(legal_description: Optional[str]) -> Optional[str]:
    normalized = empty_or_none(legal_description)
    if normalized is None:
        return None

    for name, pattern in NEIGHBORHOOD_PATTERNS:
        if pattern.search(normalized):
            return name.title()

    return None


def is_developer_owned(owner_name: Optional[str]) -> bool:
    normalized = empty_or_none(owner_name)
    if normalized is None:
        return False
    return bool(DEVELOPER_OWNER_PATTERN.search(normalized))


def update_years_owned_from_sales(path: str, db: Session) -> int:
    latest_sale_by_parcel: dict[str, datetime] = {}

    with Path(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            parcel_number = empty_or_none(row.get("ParcelNumber"))
            sale_date = parse_sale_date(row.get("SaleDate"))
            if parcel_number is None or sale_date is None:
                continue

            current = latest_sale_by_parcel.get(parcel_number)
            if current is None or sale_date > current:
                latest_sale_by_parcel[parcel_number] = sale_date

    now = datetime.now(timezone.utc)
    updated = 0

    for parcel_number, sale_date in latest_sale_by_parcel.items():
        parcel = db.query(Parcel).filter(Parcel.parcel_number == parcel_number).first()
        if parcel is None:
            continue

        years_owned = max(0, now.year - sale_date.year - ((now.month, now.day) < (sale_date.month, sale_date.day)))
        parcel.years_owned = years_owned
        updated += 1

    db.commit()
    return updated


def update_neighborhoods_from_boundary_details(path: str, db: Session) -> int:
    updated = 0

    with Path(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            parcel_number = empty_or_none(row.get("ParcelNumber"))
            neighborhood = infer_neighborhood(row.get("LegalDescription"))
            if parcel_number is None or neighborhood is None:
                continue

            parcel = db.query(Parcel).filter(Parcel.parcel_number == parcel_number).first()
            if parcel is None:
                continue

            if parcel.neighborhood != neighborhood:
                parcel.neighborhood = neighborhood
                updated += 1

    db.commit()
    return updated


def update_developer_owned_flags(db: Session) -> int:
    updated = 0
    parcels = db.query(Parcel).all()

    for parcel in parcels:
        developer_owned = is_developer_owned(parcel.owner_name)
        if parcel.developer_owned != developer_owned:
            parcel.developer_owned = developer_owned
            updated += 1

    db.commit()
    return updated


def update_adjacent_developer_owned_from_geojson(path: str, db: Session) -> int:
    developer_owned_map = {
        parcel.parcel_number: bool(parcel.developer_owned)
        for parcel in db.query(Parcel.parcel_number, Parcel.developer_owned).all()
    }

    parcels_by_number = {
        parcel.parcel_number: parcel
        for parcel in db.query(Parcel).all()
    }
    parcels_by_gpin = {
        parcel.gpin: parcel
        for parcel in parcels_by_number.values()
        if parcel.gpin
    }

    with Path(path).open(encoding="utf-8") as stream:
        data = json.load(stream)

    geometries: dict[str, object] = {}
    for feature in data.get("features", []):
        gpin = empty_or_none(feature.get("properties", {}).get("GPIN"))
        geometry = feature.get("geometry")
        if gpin is None or not geometry:
            continue
        parcel = parcels_by_gpin.get(gpin)
        if parcel is None:
            continue
        geometries[parcel.parcel_number] = shape(geometry)

    developer_items = [
        (parcel_number, geometry)
        for parcel_number, geometry in geometries.items()
        if developer_owned_map.get(parcel_number, False)
    ]

    developer_polygons = [geometry for _, geometry in developer_items]
    developer_numbers = [parcel_number for parcel_number, _ in developer_items]
    developer_tree = STRtree(developer_polygons) if developer_polygons else None

    updated = 0
    for parcel_number, geometry in geometries.items():
        parcel = parcels_by_number[parcel_number]
        adjacent = False

        if developer_tree is not None:
            for match_index in developer_tree.query(geometry):
                other_number = developer_numbers[match_index]
                other_geometry = developer_polygons[match_index]
                if other_number == parcel_number:
                    continue
                if geometry.touches(other_geometry):
                    adjacent = True
                    break

        if parcel.developer_owned:
            # Developer-owned parcels should still carry the adjacency signal
            # only when they touch another developer-owned parcel.
            pass

        if parcel.adjacent_developer_owned != adjacent:
            parcel.adjacent_developer_owned = adjacent
            updated += 1

    db.commit()
    return updated


def main(
    sales_csv_path: str = str(SALES_CSV_FILE),
    boundary_csv_path: str = str(BOUNDARY_DETAILS_CSV_FILE),
    boundaries_geojson_path: str = str(BOUNDARIES_GEOJSON_FILE),
) -> None:
    db = SessionLocal()
    try:
        years_owned_updated = update_years_owned_from_sales(sales_csv_path, db)
        neighborhood_updated = update_neighborhoods_from_boundary_details(boundary_csv_path, db)
        developer_owned_updated = update_developer_owned_flags(db)
        adjacent_updated = update_adjacent_developer_owned_from_geojson(boundaries_geojson_path, db)
        print(f"Updated years_owned for {years_owned_updated} parcels")
        print(f"Updated neighborhood for {neighborhood_updated} parcels")
        print(f"Updated developer_owned for {developer_owned_updated} parcels")
        print(f"Updated adjacent_developer_owned for {adjacent_updated} parcels")
    finally:
        db.close()


if __name__ == "__main__":
    main()
