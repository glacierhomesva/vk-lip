from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _load_environment() -> None:
    # Support running from repo root and backend/ while always preferring backend/.env.
    current = Path(__file__).resolve()
    backend_root = current.parents[2]
    repo_root = current.parents[4]

    backend_env = backend_root / ".env"
    repo_env = repo_root / ".env"

    if backend_env.exists():
        load_dotenv(backend_env, override=False)
    if repo_env.exists():
        load_dotenv(repo_env, override=False)


_load_environment()


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


@dataclass(frozen=True)
class SourceDatasetConfig:
    name: str
    url: str | None
    root_key: str | None = None

    @property
    def enabled(self) -> bool:
        return self.url is not None


@dataclass(frozen=True)
class SourceSyncSettings:
    base_url: str | None
    api_key: str | None
    bearer_token: str | None
    timeout_seconds: int
    parcels: SourceDatasetConfig
    owners: SourceDatasetConfig
    assessments: SourceDatasetConfig
    property_types: SourceDatasetConfig
    sales: SourceDatasetConfig
    boundary_details: SourceDatasetConfig
    tax_delinquency: SourceDatasetConfig

    @classmethod
    def from_env(cls) -> "SourceSyncSettings":
        base_url = _clean(os.getenv("SOURCE_BASE_URL"))

        def dataset(name: str) -> SourceDatasetConfig:
            prefix = f"SOURCE_{name.upper()}"
            url = _clean(os.getenv(f"{prefix}_URL"))
            root_key = _clean(os.getenv(f"{prefix}_ROOT_KEY"))
            if url and base_url and not url.startswith(("http://", "https://")):
                joined = f"{base_url.rstrip('/')}/{url.lstrip('/')}"
            else:
                joined = url
            return SourceDatasetConfig(name=name, url=joined, root_key=root_key)

        timeout_raw = _clean(os.getenv("SOURCE_TIMEOUT_SECONDS"))
        timeout_seconds = int(timeout_raw) if timeout_raw else 60

        return cls(
            base_url=base_url,
            api_key=_clean(os.getenv("SOURCE_API_KEY")),
            bearer_token=_clean(os.getenv("SOURCE_BEARER_TOKEN")),
            timeout_seconds=timeout_seconds,
            parcels=dataset("parcels"),
            owners=dataset("owners"),
            assessments=dataset("assessments"),
            property_types=dataset("property_types"),
            sales=dataset("sales"),
            boundary_details=dataset("boundary_details"),
            tax_delinquency=dataset("tax_delinquency"),
        )

    def dataset_map(self) -> dict[str, SourceDatasetConfig]:
        return {
            "parcels": self.parcels,
            "owners": self.owners,
            "assessments": self.assessments,
            "property_types": self.property_types,
            "sales": self.sales,
            "boundary_details": self.boundary_details,
            "tax_delinquency": self.tax_delinquency,
        }