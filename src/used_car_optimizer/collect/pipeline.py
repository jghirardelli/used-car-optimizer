from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path

from .base import Collector
from .models import NormalizedListing, RawListing
from .normalize import normalize_listing, should_keep_listing


RAW_COLUMNS = [
    "source_name",
    "source_type",
    "listing_id",
    "url",
    "fetched_at",
    "seller_name",
    "location",
    "vin",
    "year",
    "make",
    "model",
    "trim",
    "price",
    "mileage",
    "body_style",
    "title_status",
    "prior_use",
    "owners",
    "accidents",
    "cargo_cuft",
    "notes",
]

NORMALIZED_COLUMNS = [
    "year",
    "make",
    "model",
    "trim",
    "price",
    "mileage",
    "body_style",
    "cargo_cuft",
    "vin",
    "accidents",
    "owners",
    "prior_use",
    "title_status",
    "source_name",
    "source_type",
    "source_url",
    "location",
    "notes",
    "confidence",
]

OPTIMIZER_EXPORT_COLUMNS = [
    "vin",
    "year",
    "make",
    "model",
    "trim",
    "body_style",
    "price",
    "mileage",
    "cargo_cuft",
    "accidents",
    "owners",
    "prior_use",
    "title_status",
    "notes",
]


def _dedupe(listings: list[NormalizedListing]) -> list[NormalizedListing]:
    best_by_key: dict[str, NormalizedListing] = {}
    confidence_order = {"high": 3, "medium": 2, "low": 1}

    for listing in listings:
        key = listing.vin or f"{listing.year}|{listing.make}|{listing.model}|{listing.trim}|{listing.mileage}|{listing.source_name}"
        existing = best_by_key.get(key)
        if not existing:
            best_by_key[key] = listing
            continue

        current_rank = confidence_order.get(listing.confidence, 0)
        existing_rank = confidence_order.get(existing.confidence, 0)
        if current_rank > existing_rank:
            best_by_key[key] = listing

    return list(best_by_key.values())


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run_collection_pipeline(
    collectors: list[Collector],
    workspace_root: Path,
    raw_output_path: str = "output/collection/raw_listings.csv",
    normalized_output_path: str = "output/collection/normalized_listings.csv",
    optimizer_output_path: str = "data/dealer_inventory.csv",
) -> dict[str, int]:
    raw_rows: list[RawListing] = []
    for collector in collectors:
        raw_rows.extend(collector.collect())

    normalized_rows = [normalize_listing(raw) for raw in raw_rows]
    filtered_rows = [row for row in normalized_rows if should_keep_listing(row)]
    deduped_rows = _dedupe(filtered_rows)

    _write_csv(
        workspace_root / raw_output_path,
        RAW_COLUMNS,
        [{key: value for key, value in asdict(row).items() if key in RAW_COLUMNS} for row in raw_rows],
    )
    _write_csv(
        workspace_root / normalized_output_path,
        NORMALIZED_COLUMNS,
        [{key: value for key, value in asdict(row).items() if key in NORMALIZED_COLUMNS} for row in deduped_rows],
    )
    _write_csv(
        workspace_root / optimizer_output_path,
        OPTIMIZER_EXPORT_COLUMNS,
        [
            {
                "vin": row.vin,
                "year": row.year,
                "make": row.make,
                "model": row.model,
                "trim": row.trim,
                "body_style": row.body_style,
                "price": row.price,
                "mileage": row.mileage,
                "cargo_cuft": row.cargo_cuft,
                "accidents": row.accidents,
                "owners": row.owners,
                "prior_use": row.prior_use,
                "title_status": row.title_status,
                "notes": f"{row.source_name} | confidence={row.confidence} | {row.notes}".strip(),
            }
            for row in deduped_rows
        ],
    )

    return {
        "raw_count": len(raw_rows),
        "normalized_count": len(normalized_rows),
        "deduped_count": len(deduped_rows),
    }
