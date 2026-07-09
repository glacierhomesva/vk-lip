import csv
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.assessment import Assessment  # noqa: F401
from app.models.parcel import Parcel

ROOT = Path(__file__).resolve().parents[3]
CSV_FILE = ROOT / "data/raw/Real_Estate_Residential.csv"


def empty_or_none(value: Optional[object]) -> Optional[str]:
    if value is None:
        return None
    stripped = str(value).strip()
    return stripped if stripped else None


def update_property_types_from_csv(path: str, db: Session) -> tuple[int, int]:
    updated = 0
    skipped = 0

    with Path(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            parcel_number = empty_or_none(row.get("ParcelNumber"))
            property_type = empty_or_none(row.get("UseCode"))

            if parcel_number is None or property_type is None:
                skipped += 1
                continue

            parcel = db.query(Parcel).filter(Parcel.parcel_number == parcel_number).first()
            if parcel is None:
                skipped += 1
                continue

            if parcel.property_type != property_type:
                parcel.property_type = property_type
                updated += 1

    db.commit()
    return updated, skipped


def main(csv_path: str = str(CSV_FILE)) -> None:
    db = SessionLocal()
    try:
        updated, skipped = update_property_types_from_csv(csv_path, db)
        print(f"Updated property_type for {updated} parcels")
        print(f"Skipped {skipped} rows")
    finally:
        db.close()


if __name__ == "__main__":
    main()