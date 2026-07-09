import csv
from pathlib import Path
from typing import Iterator, List, Optional

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.parcel import Parcel

ROOT = Path(__file__).resolve().parents[3]
CSV_FILE = ROOT / "data/raw/real_estate_base.csv"


def float_or_none(value: Optional[str]) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def build_address(row: dict[str, str]) -> Optional[str]:
    parts = []
    street_number = row.get("StreetNumber", "").strip()
    street_name = row.get("StreetName", "").strip()
    unit = row.get("Unit", "").strip()

    if street_number:
        parts.append(street_number)
    if street_name:
        parts.append(street_name)
    if unit:
        parts.append(unit)

    return " ".join(parts) if parts else None


def parcel_from_row(row: dict[str, str]) -> Parcel:
    return Parcel(
        parcel_number=row.get("ParcelNumber") or None,
        gpin=row.get("GPIN") or None,
        street_number=row.get("StreetNumber") or None,
        street_name=row.get("StreetName") or None,
        unit=row.get("Unit") or None,
        address=build_address(row),
        zoning=row.get("Zone") or None,
        lot_size=float_or_none(row.get("Acreage")),
    )


def read_parcels_csv(path: str) -> Iterator[Parcel]:
    file_path = Path(path)
    with file_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            yield parcel_from_row(row)


def _collect_existing_parcel_numbers(db: Session, parcel_numbers: List[str]) -> set[str]:
    if not parcel_numbers:
        return set()
    existing = (
        db.query(Parcel.parcel_number)
        .filter(Parcel.parcel_number.in_(parcel_numbers))
        .all()
    )
    return {row[0] for row in existing}


def import_parcels_from_csv(path: str, db: Session, batch_size: int = 1000) -> int:
    inserted = 0
    batch: List[Parcel] = []
    parcel_numbers: List[str] = []
    seen_parcel_numbers: set[str] = set()

    for parcel in read_parcels_csv(path):
        if parcel.parcel_number is None:
            continue

        if parcel.parcel_number in seen_parcel_numbers:
            continue

        seen_parcel_numbers.add(parcel.parcel_number)
        batch.append(parcel)
        parcel_numbers.append(parcel.parcel_number)

        if len(batch) >= batch_size:
            existing = _collect_existing_parcel_numbers(db, parcel_numbers)
            filtered = [p for p in batch if p.parcel_number not in existing]
            if filtered:
                db.bulk_save_objects(filtered)
                db.commit()
                inserted += len(filtered)
            batch = []
            parcel_numbers = []

    if batch:
        existing = _collect_existing_parcel_numbers(db, parcel_numbers)
        filtered = [p for p in batch if p.parcel_number not in existing]
        if filtered:
            db.bulk_save_objects(filtered)
            db.commit()
            inserted += len(filtered)

    return inserted


def main(csv_path: str = CSV_FILE) -> None:
    db = SessionLocal()
    try:
        count = import_parcels_from_csv(csv_path, db)
        print(f"Imported {count} parcels from {csv_path}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
