import csv
from pathlib import Path
from typing import Iterator, List, Optional

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.assessment import Assessment
from app.models.parcel import Parcel

ROOT = Path(__file__).resolve().parents[3]
CSV_FILE = ROOT / "data/raw/real_estate_assessments.csv"


def float_or_none(value: Optional[str]) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def assessment_from_row(row: dict[str, str]) -> Assessment:
    return Assessment(
        parcel_number=row.get("ParcelNumber") or None,
        tax_year=int(row["TaxYear"]) if row.get("TaxYear") else None,
        land_value=float_or_none(row.get("LandValue")),
        improvement_value=float_or_none(row.get("ImprovementValue")),
        total_value=float_or_none(row.get("TotalValue")),
    )


def read_assessments_csv(path: str) -> Iterator[Assessment]:
    file_path = Path(path)
    with file_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            yield assessment_from_row(row)


def _collect_existing_assessments(db: Session, keys: List[tuple[str, int]]) -> set[tuple[str, int]]:
    if not keys:
        return set()
    parcel_numbers = [parcel_number for parcel_number, _ in keys]
    tax_years = [tax_year for _, tax_year in keys]

    existing = (
        db.query(Assessment.parcel_number, Assessment.tax_year)
        .filter(
            Assessment.parcel_number.in_(parcel_numbers),
            Assessment.tax_year.in_(tax_years),
        )
        .all()
    )
    return {(row[0], row[1]) for row in existing}


def _collect_existing_parcels(db: Session, parcel_numbers: List[str]) -> set[str]:
    if not parcel_numbers:
        return set()
    existing = (
        db.query(Parcel.parcel_number)
        .filter(Parcel.parcel_number.in_(parcel_numbers))
        .all()
    )
    return {row[0] for row in existing}


def import_assessments_from_csv(path: str, db: Session, batch_size: int = 1000) -> int:
    inserted = 0
    batch: List[Assessment] = []
    assessment_keys: List[tuple[str, int]] = []
    seen_keys: set[tuple[str, int]] = set()

    for assessment in read_assessments_csv(path):
        if assessment.parcel_number is None or assessment.tax_year is None:
            continue

        key = (assessment.parcel_number, assessment.tax_year)
        if key in seen_keys:
            continue

        seen_keys.add(key)
        batch.append(assessment)
        assessment_keys.append(key)

        if len(batch) >= batch_size:
            existing_parcels = _collect_existing_parcels(db, [a.parcel_number for a in batch])
            batch = [a for a in batch if a.parcel_number in existing_parcels]
            assessment_keys = [k for k in assessment_keys if k[0] in existing_parcels]

            existing = _collect_existing_assessments(db, assessment_keys)
            filtered = [a for a in batch if (a.parcel_number, a.tax_year) not in existing]
            if filtered:
                db.bulk_save_objects(filtered)
                db.commit()
                inserted += len(filtered)
            batch = []
            assessment_keys = []

    if batch:
        existing_parcels = _collect_existing_parcels(db, [a.parcel_number for a in batch])
        batch = [a for a in batch if a.parcel_number in existing_parcels]
        assessment_keys = [k for k in assessment_keys if k[0] in existing_parcels]

        existing = _collect_existing_assessments(db, assessment_keys)
        filtered = [a for a in batch if (a.parcel_number, a.tax_year) not in existing]
        if filtered:
            db.bulk_save_objects(filtered)
            db.commit()
            inserted += len(filtered)

    return inserted


def main(csv_path: str = CSV_FILE) -> None:
    db = SessionLocal()
    try:
        count = import_assessments_from_csv(csv_path, db)
        print(f"Imported {count} assessments from {csv_path}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
