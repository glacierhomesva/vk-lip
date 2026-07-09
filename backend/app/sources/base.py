from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping


SourceRecord = Mapping[str, Any]


class SourceClient(ABC):
    @abstractmethod
    def available_datasets(self) -> dict[str, bool]:
        raise NotImplementedError

    @abstractmethod
    def fetch(self, dataset_name: str) -> Iterable[SourceRecord]:
        raise NotImplementedError

    def fetch_parcels(self) -> Iterable[SourceRecord]:
        return self.fetch("parcels")

    def fetch_owners(self) -> Iterable[SourceRecord]:
        return self.fetch("owners")

    def fetch_assessments(self) -> Iterable[SourceRecord]:
        return self.fetch("assessments")

    def fetch_property_types(self) -> Iterable[SourceRecord]:
        return self.fetch("property_types")

    def fetch_sales(self) -> Iterable[SourceRecord]:
        return self.fetch("sales")

    def fetch_boundary_details(self) -> Iterable[SourceRecord]:
        return self.fetch("boundary_details")

    def fetch_tax_delinquency(self) -> Iterable[SourceRecord]:
        return self.fetch("tax_delinquency")