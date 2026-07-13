from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Iterable, Mapping

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.parcel import Parcel
from app.sources.base import SourceClient


def _clean(value: object | None) -> str | None:
    if value is None:
        return None
    stripped = str(value).strip()
    return stripped or None


def _float(value: object | None) -> float | None:
    normalized = _clean(value)
    if normalized is None:
        return None
    try:
        return float(normalized.replace(",", ""))
    except ValueError:
        return None


def _int(value: object | None) -> int | None:
    normalized = _clean(value)
    if normalized is None:
        return None
    try:
        return int(float(normalized))
    except ValueError:
        return None


def _address(record: Mapping[str, Any]) -> str | None:
    parts = [
        _clean(record.get("street_number") or record.get("StreetNumber")),
        _clean(record.get("street_name") or record.get("StreetName")),
        _clean(record.get("unit") or record.get("Unit")),
    ]
    joined = " ".join(part for part in parts if part)
    return joined or _clean(record.get("address") or record.get("FullAddress"))


NEIGHBORHOOD_PATTERNS = [
    ("Belmont", re.compile(r"\bBELMONT\b", re.IGNORECASE)),
    ("Fifeville", re.compile(r"\bFIFEVILLE\b", re.IGNORECASE)),
]


def _infer_neighborhood(value: str | None) -> str | None:
    if value is None:
        return None
    for name, pattern in NEIGHBORHOOD_PATTERNS:
        if pattern.search(value):
            return name
    return None


def _parse_sale_date(value: object | None) -> datetime | None:
    normalized = _clean(value)
    if normalized is None:
        return None
    for fmt in ("%Y/%m/%d %H:%M:%S+00", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(normalized, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


@dataclass
class DatasetSyncResult:
    processed: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0


@dataclass
class SyncSummary:
    datasets: dict[str, DatasetSyncResult] = field(default_factory=dict)


class SourceSyncService:
    def __init__(
        self,
        db: Session,
        chunk_size: int = 1000,
        progress_every: int = 5000,
        progress_hook: Callable[[str], None] | None = None,
    ):
        self.db = db
        self.chunk_size = max(1, chunk_size)
        self.progress_every = max(1, progress_every)
        self.progress_hook = progress_hook or print

    def _emit_progress(self, dataset: str, result: DatasetSyncResult, completed: bool = False) -> None:
        status = "completed" if completed else "in-progress"
        self.progress_hook(
            f"[{dataset}] {status}: processed={result.processed} created={result.created} "
            f"updated={result.updated} skipped={result.skipped}",
        )

    @staticmethod
    def _chunked(records: Iterable[Mapping[str, Any]], size: int) -> Iterable[list[Mapping[str, Any]]]:
        chunk: list[Mapping[str, Any]] = []
        for record in records:
            chunk.append(record)
            if len(chunk) >= size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk

    def _should_log_progress(self, result: DatasetSyncResult, next_checkpoint: int) -> bool:
        return result.processed >= next_checkpoint

    def sync(self, client: SourceClient, datasets: list[str] | None = None) -> SyncSummary:
        requested = set(datasets or client.available_datasets().keys())
        summary = SyncSummary()

        if "parcels" in requested:
            summary.datasets["parcels"] = self.sync_parcels(client.fetch_parcels())
        if "owners" in requested:
            summary.datasets["owners"] = self.sync_owners(client.fetch_owners())
        if "assessments" in requested:
            summary.datasets["assessments"] = self.sync_assessments(client.fetch_assessments())
        if "property_types" in requested:
            summary.datasets["property_types"] = self.sync_property_types(client.fetch_property_types())
        if "sales" in requested:
            summary.datasets["sales"] = self.sync_sales(client.fetch_sales())
        if "boundary_details" in requested:
            summary.datasets["boundary_details"] = self.sync_boundary_details(client.fetch_boundary_details())
        if "tax_delinquency" in requested:
            summary.datasets["tax_delinquency"] = self.sync_tax_delinquency(client.fetch_tax_delinquency())

        return summary

    def sync_parcels(self, records: Iterable[Mapping[str, Any]]) -> DatasetSyncResult:
        result = DatasetSyncResult()
        next_log = self.progress_every
        for chunk in self._chunked(records, self.chunk_size):
            parcel_numbers = {
                parcel_number
                for parcel_number in (
                    _clean(record.get("parcel_number") or record.get("ParcelNumber"))
                    for record in chunk
                )
                if parcel_number
            }
            existing = {
                parcel.parcel_number: parcel
                for parcel in self.db.query(Parcel).filter(Parcel.parcel_number.in_(parcel_numbers)).all()
            }

            for record in chunk:
                result.processed += 1
                parcel_number = _clean(record.get("parcel_number") or record.get("ParcelNumber"))
                if parcel_number is None:
                    result.skipped += 1
                    continue

                parcel = existing.get(parcel_number)
                created = False
                if parcel is None:
                    parcel = Parcel(parcel_number=parcel_number)
                    self.db.add(parcel)
                    existing[parcel_number] = parcel
                    created = True

                parcel.gpin = _clean(record.get("gpin") or record.get("GPIN")) or parcel.gpin
                parcel.street_number = _clean(record.get("street_number") or record.get("StreetNumber"))
                parcel.street_name = _clean(record.get("street_name") or record.get("StreetName"))
                parcel.unit = _clean(record.get("unit") or record.get("Unit"))
                parcel.address = _address(record)
                parcel.city = _clean(record.get("city") or record.get("City"))
                parcel.state = _clean(record.get("state") or record.get("State"))
                parcel.zip_code = _clean(record.get("zip_code") or record.get("ZipCode"))
                parcel.zoning = _clean(record.get("zoning") or record.get("Zone"))
                parcel.lot_size = _float(record.get("acres") or record.get("Acreage") or record.get("lot_size"))

                if created:
                    result.created += 1
                else:
                    result.updated += 1

            self.db.commit()
            if self._should_log_progress(result, next_log):
                self._emit_progress("parcels", result)
                next_log += self.progress_every

        self._emit_progress("parcels", result, completed=True)
        return result

    def sync_owners(self, records: Iterable[Mapping[str, Any]]) -> DatasetSyncResult:
        result = DatasetSyncResult()
        next_log = self.progress_every
        for chunk in self._chunked(records, self.chunk_size):
            parcel_numbers = {
                parcel_number
                for parcel_number in (
                    _clean(record.get("parcel_number") or record.get("ParcelNumber"))
                    for record in chunk
                )
                if parcel_number
            }
            existing = {
                parcel.parcel_number: parcel
                for parcel in self.db.query(Parcel).filter(Parcel.parcel_number.in_(parcel_numbers)).all()
            }

            for record in chunk:
                result.processed += 1
                parcel_number = _clean(record.get("parcel_number") or record.get("ParcelNumber"))
                if parcel_number is None:
                    result.skipped += 1
                    continue

                parcel = existing.get(parcel_number)
                if parcel is None:
                    result.skipped += 1
                    continue

                parcel.owner_name = _clean(record.get("owner_name") or record.get("OwnerName"))
                parcel.owner_address = _clean(record.get("owner_address") or record.get("OwnerAddress"))
                parcel.owner_city_state = _clean(record.get("owner_city_state") or record.get("OwnerCityState"))
                parcel.owner_zip_code = _clean(record.get("owner_zip_code") or record.get("OwnerZipCode"))
                result.updated += 1

            self.db.commit()
            if self._should_log_progress(result, next_log):
                self._emit_progress("owners", result)
                next_log += self.progress_every

        self._emit_progress("owners", result, completed=True)
        return result

    def sync_assessments(self, records: Iterable[Mapping[str, Any]]) -> DatasetSyncResult:
        result = DatasetSyncResult()
        next_log = self.progress_every
        for chunk in self._chunked(records, self.chunk_size):
            parcel_numbers: set[str] = set()
            for record in chunk:
                parcel_number = _clean(record.get("parcel_number") or record.get("ParcelNumber"))
                tax_year = _int(record.get("tax_year") or record.get("TaxYear"))
                if parcel_number and tax_year is not None:
                    parcel_numbers.add(parcel_number)

            existing_parcels = {
                parcel.parcel_number
                for parcel in self.db.query(Parcel.parcel_number).filter(Parcel.parcel_number.in_(parcel_numbers)).all()
            }

            existing = {
                (assessment.parcel_number, assessment.tax_year): assessment
                for assessment in self.db.query(Assessment).filter(Assessment.parcel_number.in_(parcel_numbers)).all()
            }

            for record in chunk:
                result.processed += 1
                parcel_number = _clean(record.get("parcel_number") or record.get("ParcelNumber"))
                tax_year = _int(record.get("tax_year") or record.get("TaxYear"))
                if parcel_number is None or tax_year is None:
                    result.skipped += 1
                    continue
                if parcel_number not in existing_parcels:
                    result.skipped += 1
                    continue

                assessment = existing.get((parcel_number, tax_year))
                created = False
                if assessment is None:
                    assessment = Assessment(parcel_number=parcel_number, tax_year=tax_year)
                    self.db.add(assessment)
                    existing[(parcel_number, tax_year)] = assessment
                    created = True

                assessment.land_value = _float(record.get("land_value") or record.get("LandValue"))
                assessment.improvement_value = _float(record.get("improvement_value") or record.get("ImprovementValue"))
                assessment.total_value = _float(record.get("total_value") or record.get("TotalValue") or record.get("AssessedValue"))

                if created:
                    result.created += 1
                else:
                    result.updated += 1

            self.db.commit()
            if self._should_log_progress(result, next_log):
                self._emit_progress("assessments", result)
                next_log += self.progress_every

        self._emit_progress("assessments", result, completed=True)
        return result

    def sync_property_types(self, records: Iterable[Mapping[str, Any]]) -> DatasetSyncResult:
        result = DatasetSyncResult()
        next_log = self.progress_every
        for chunk in self._chunked(records, self.chunk_size):
            parcel_numbers = {
                parcel_number
                for parcel_number in (
                    _clean(record.get("parcel_number") or record.get("ParcelNumber"))
                    for record in chunk
                )
                if parcel_number
            }
            existing = {
                parcel.parcel_number: parcel
                for parcel in self.db.query(Parcel).filter(Parcel.parcel_number.in_(parcel_numbers)).all()
            }

            for record in chunk:
                result.processed += 1
                parcel_number = _clean(record.get("parcel_number") or record.get("ParcelNumber"))
                property_type = _clean(record.get("property_type") or record.get("UseCode"))
                if parcel_number is None or property_type is None:
                    result.skipped += 1
                    continue

                parcel = existing.get(parcel_number)
                if parcel is None:
                    result.skipped += 1
                    continue

                parcel.property_type = property_type
                result.updated += 1

            self.db.commit()
            if self._should_log_progress(result, next_log):
                self._emit_progress("property_types", result)
                next_log += self.progress_every

        self._emit_progress("property_types", result, completed=True)
        return result

    def sync_sales(self, records: Iterable[Mapping[str, Any]]) -> DatasetSyncResult:
        result = DatasetSyncResult()
        latest_sale_by_parcel: dict[str, datetime] = {}

        for record in records:
            result.processed += 1
            parcel_number = _clean(record.get("parcel_number") or record.get("ParcelNumber"))
            sale_date = _parse_sale_date(record.get("sale_date") or record.get("SaleDate"))
            if parcel_number is None or sale_date is None:
                result.skipped += 1
                continue
            current = latest_sale_by_parcel.get(parcel_number)
            if current is None or sale_date > current:
                latest_sale_by_parcel[parcel_number] = sale_date

        now = datetime.now(timezone.utc)
        parcel_numbers = set(latest_sale_by_parcel)
        parcels = {
            parcel.parcel_number: parcel
            for parcel in self.db.query(Parcel).filter(Parcel.parcel_number.in_(parcel_numbers)).all()
        }
        for parcel_number, sale_date in latest_sale_by_parcel.items():
            parcel = parcels.get(parcel_number)
            if parcel is None:
                result.skipped += 1
                continue
            parcel.years_owned = max(0, now.year - sale_date.year - ((now.month, now.day) < (sale_date.month, sale_date.day)))
            result.updated += 1

        self.db.commit()
        self._emit_progress("sales", result, completed=True)
        return result

    def sync_boundary_details(self, records: Iterable[Mapping[str, Any]]) -> DatasetSyncResult:
        result = DatasetSyncResult()
        next_log = self.progress_every
        for chunk in self._chunked(records, self.chunk_size):
            parcel_numbers = {
                parcel_number
                for parcel_number in (
                    _clean(record.get("parcel_number") or record.get("ParcelNumber"))
                    for record in chunk
                )
                if parcel_number
            }
            existing = {
                parcel.parcel_number: parcel
                for parcel in self.db.query(Parcel).filter(Parcel.parcel_number.in_(parcel_numbers)).all()
            }

            for record in chunk:
                result.processed += 1
                parcel_number = _clean(record.get("parcel_number") or record.get("ParcelNumber"))
                legal_description = _clean(record.get("legal_description") or record.get("LegalDescription"))
                neighborhood = _infer_neighborhood(legal_description)
                if parcel_number is None or neighborhood is None:
                    result.skipped += 1
                    continue
                parcel = existing.get(parcel_number)
                if parcel is None:
                    result.skipped += 1
                    continue
                parcel.neighborhood = neighborhood
                result.updated += 1

            self.db.commit()
            if self._should_log_progress(result, next_log):
                self._emit_progress("boundary_details", result)
                next_log += self.progress_every

        self._emit_progress("boundary_details", result, completed=True)
        return result

    def sync_tax_delinquency(self, records: Iterable[Mapping[str, Any]]) -> DatasetSyncResult:
        result = DatasetSyncResult()
        next_log = self.progress_every

        # Treat delinquency imports as a full snapshot: clear previous flags first.
        self.db.query(Parcel).filter(Parcel.tax_delinquent.is_(True)).update(
            {
                Parcel.tax_delinquent: False,
                Parcel.tax_lien_amount: None,
            },
            synchronize_session=False,
        )
        self.db.commit()

        for chunk in self._chunked(records, self.chunk_size):
            parcel_numbers = {
                parcel_number
                for parcel_number in (
                    _clean(record.get("parcel_number") or record.get("ParcelNumber"))
                    for record in chunk
                )
                if parcel_number
            }
            existing = {
                parcel.parcel_number: parcel
                for parcel in self.db.query(Parcel).filter(Parcel.parcel_number.in_(parcel_numbers)).all()
            }

            for record in chunk:
                result.processed += 1
                parcel_number = _clean(record.get("parcel_number") or record.get("ParcelNumber"))
                if parcel_number is None:
                    result.skipped += 1
                    continue
                parcel = existing.get(parcel_number)
                if parcel is None:
                    result.skipped += 1
                    continue

                parcel.tax_delinquent = True
                parcel.tax_lien_amount = _float(record.get("lien_amount") or record.get("LienAmount") or record.get("amount"))
                result.updated += 1

            self.db.commit()
            if self._should_log_progress(result, next_log):
                self._emit_progress("tax_delinquency", result)
                next_log += self.progress_every

        self._emit_progress("tax_delinquency", result, completed=True)
        return result