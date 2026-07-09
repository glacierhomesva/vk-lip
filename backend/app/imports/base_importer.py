from __future__ import annotations

import csv
from pathlib import Path
from typing import Callable, Generic, Iterable, Iterator, Optional, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseImporter(Generic[T]):
    """Base CSV importer with batching support."""

    def __init__(self, db: Session, batch_size: int = 1000):
        self.db = db
        self.batch_size = batch_size

        self.imported = 0
        self.updated = 0
        self.failed = 0

    def parse_row(self, row: dict[str, str]) -> T:
        """Convert a CSV row into a model object.

        Subclasses must override this method.
        """
        raise NotImplementedError("Subclasses must implement parse_row")

    def summary(self) -> None:
        print()
        print("========== IMPORT SUMMARY ==========")
        print(f"Imported : {self.imported:,}")
        print(f"Updated  : {self.updated:,}")
        print(f"Failed   : {self.failed:,}")

    def read_csv(self, path: str) -> Iterator[T]:
        file_path = Path(path)
        with file_path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            for row in reader:
                yield self.parse_row(row)

    def import_from_csv(self, path: str) -> int:
        inserted = 0
        batch: list[T] = []

        for item in self.read_csv(path):
            batch.append(item)
            if len(batch) >= self.batch_size:
                self._flush(batch)
                inserted += len(batch)
                batch = []

        if batch:
            self._flush(batch)
            inserted += len(batch)

        return inserted

    def _flush(self, batch: list[T]) -> None:
        """Persist a batch of items."""
        self.db.bulk_save_objects(batch)
        self.db.commit()


def nullable_float(value: Optional[str]) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None
