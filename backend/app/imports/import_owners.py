import csv
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.assessment import Assessment  # noqa: F401
from app.models.parcel import Parcel

ROOT = Path(__file__).resolve().parents[3]
CSV_FILE = ROOT / "data/raw/Parcel_Owner_Points.csv"


def empty_or_none(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped != "" else None


def update_owners_from_csv(path: str, db: Session, batch_size: int = 500) -> tuple[int, int, int]:
    updated = 0
    skipped = 0
    failed = 0
    batch = 0

    file_path = Path(path)
    with file_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            parcel_number = empty_or_none(row.get("ParcelNumber"))
            if not parcel_number:
                skipped += 1
                continue

            parcel = db.query(Parcel).filter(Parcel.parcel_number == parcel_number).first()
            if parcel is None:
                skipped += 1
                continue

            parcel.owner_name = empty_or_none(row.get("OwnerName"))
            parcel.owner_address = empty_or_none(row.get("OwnerAddress"))
            parcel.owner_city_state = empty_or_none(row.get("OwnerCityState"))
            parcel.owner_zip_code = empty_or_none(row.get("OwnerZipCode"))

            updated += 1
            batch += 1

            if batch >= batch_size:
                db.commit()
                batch = 0

    if batch > 0:
        db.commit()

    return updated, skipped, failed


def main(csv_path: str = CSV_FILE) -> None:
    db = SessionLocal()
    try:
        updated, skipped, failed = update_owners_from_csv(str(csv_path), db)
        print(f"Updated {updated} parcels")
        print(f"Skipped {skipped} rows")
        print(f"Failed {failed} rows")
    finally:
        db.close()


if __name__ == "__main__":
    main()
