import csv
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.assessment import Assessment  # noqa: F401
from app.models.parcel import Parcel

ROOT = Path(__file__).resolve().parents[3]
CSV_FILE = ROOT / "data/raw/tax_delinquency.csv"


def empty_or_none(value: Optional[object]) -> Optional[str]:
    if value is None:
        return None
    stripped = str(value).strip()
    return stripped if stripped else None


def float_or_none(value: Optional[object]) -> Optional[float]:
    normalized = empty_or_none(value)
    if normalized is None:
        return None
    try:
        return float(normalized.replace(",", ""))
    except ValueError:
        return None


def import_tax_delinquency_from_csv(path: str, db: Session) -> tuple[int, int]:
    updated = 0
    skipped = 0

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Tax delinquency source not found at {file_path}. Add a CSV with parcel_number and optional lien_amount columns."
        )

    with file_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            parcel_number = empty_or_none(row.get("parcel_number") or row.get("ParcelNumber"))
            if parcel_number is None:
                skipped += 1
                continue

            parcel = db.query(Parcel).filter(Parcel.parcel_number == parcel_number).first()
            if parcel is None:
                skipped += 1
                continue

            parcel.tax_delinquent = True
            lien_amount = float_or_none(row.get("lien_amount") or row.get("LienAmount") or row.get("amount"))
            parcel.tax_lien_amount = lien_amount
            updated += 1

    db.commit()
    return updated, skipped


def main(csv_path: str = str(CSV_FILE)) -> None:
    db = SessionLocal()
    try:
        updated, skipped = import_tax_delinquency_from_csv(csv_path, db)
        print(f"Updated tax delinquency for {updated} parcels")
        print(f"Skipped {skipped} rows")
    finally:
        db.close()


if __name__ == "__main__":
    main()