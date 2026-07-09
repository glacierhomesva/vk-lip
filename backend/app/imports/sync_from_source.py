from __future__ import annotations

import argparse
import hashlib
from typing import Any

from sqlalchemy import text

from app.core.source_config import SourceSyncSettings
from app.db.database import SessionLocal
from app.services.source_sync import SourceSyncService
from app.sources.http_json import HttpJsonSourceClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sync parcel data directly from configured upstream JSON endpoints.",
    )
    parser.add_argument(
        "--datasets",
        nargs="*",
        default=None,
        choices=[
            "parcels",
            "owners",
            "assessments",
            "property_types",
            "sales",
            "boundary_details",
            "tax_delinquency",
        ],
        help="Limit the sync to specific datasets.",
    )
    parser.add_argument(
        "--list-configured",
        action="store_true",
        help="Show which source datasets are configured and exit.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Number of source records to process per database batch (default: 1000).",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=5000,
        help="Emit progress logs every N processed records (default: 5000).",
    )
    parser.add_argument(
        "--job-name",
        default=None,
        help="Optional logical job name used for advisory lock coordination.",
    )
    parser.add_argument(
        "--no-lock",
        action="store_true",
        help="Disable Postgres advisory lock protection for overlapping runs.",
    )
    return parser


def _lock_key(value: str) -> int:
    digest = hashlib.blake2b(value.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, byteorder="big", signed=True)


def _acquire_lock(db: Any, lock_name: str) -> tuple[bool, int] | tuple[None, None]:
    bind = db.get_bind()
    if bind is None or bind.dialect.name != "postgresql":
        print("[sync] advisory lock skipped (non-PostgreSQL database)")
        return None, None

    key = _lock_key(lock_name)
    acquired = bool(db.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": key}).scalar())
    if acquired:
        print(f"[sync] acquired advisory lock: {lock_name}")
    return acquired, key


def _release_lock(db: Any, lock_name: str, key: int | None) -> None:
    if key is None:
        return
    db.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": key})
    print(f"[sync] released advisory lock: {lock_name}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    settings = SourceSyncSettings.from_env()
    client = HttpJsonSourceClient(settings)
    available = client.available_datasets()

    if args.list_configured:
        for name, enabled in available.items():
            print(f"{name}: {'configured' if enabled else 'missing'}")
        return

    datasets = args.datasets or [name for name, enabled in available.items() if enabled]
    if not datasets:
        parser.error(
            "No source datasets are configured. Set SOURCE_<DATASET>_URL env vars such as SOURCE_PARCELS_URL.",
        )

    db = SessionLocal()
    lock_name = args.job_name or f"source-sync:{','.join(sorted(datasets))}"
    lock_key: int | None = None
    try:
        if not args.no_lock:
            acquired, lock_key = _acquire_lock(db, lock_name)
            if acquired is False:
                print(f"[sync] skipped: another run already holds lock '{lock_name}'")
                raise SystemExit(2)

        service = SourceSyncService(
            db,
            chunk_size=args.chunk_size,
            progress_every=args.progress_every,
        )
        summary = service.sync(client, datasets=datasets)
    finally:
        if not args.no_lock:
            _release_lock(db, lock_name, lock_key)
        db.close()

    print("Direct source sync summary")
    print("==========================")
    for dataset, result in summary.datasets.items():
        print(
            f"{dataset}: processed={result.processed} created={result.created} "
            f"updated={result.updated} skipped={result.skipped}"
        )


if __name__ == "__main__":
    main()