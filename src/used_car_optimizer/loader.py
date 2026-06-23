from __future__ import annotations

import csv
from pathlib import Path

from .models import CarListing


def _to_float(value: object, default: float = 0.0) -> float:
    text = str(value or "").replace("$", "").replace(",", "").strip()
    if not text:
        return default
    return float(text)


def _to_int(value: object, default: int = 0) -> int:
    return int(round(_to_float(value, default)))


def _normalize_prior_use(row: dict[str, str]) -> str:
    prior_use = (row.get("prior_use") or "").strip()
    if prior_use:
        return prior_use
    if str(row.get("rental_fleet") or "").strip().lower() in {"yes", "true", "1"}:
        return "rental"
    if str(row.get("short_second_owner") or "").strip().lower() in {"yes", "true", "1"}:
        return "short-term resale"
    return ""


def _normalize_title_status(row: dict[str, str]) -> str:
    title_status = (row.get("title_status") or "").strip()
    if title_status:
        return title_status
    if str(row.get("title_issue") or "").strip().lower() in {"yes", "true", "1"}:
        return "title issue"
    return "clean"


def _model_key(row: dict[str, str]) -> str:
    existing = (row.get("model_key") or "").strip()
    if existing:
        return existing

    make = (row.get("make") or "").strip()
    model = (row.get("model") or "").strip()
    trim = (row.get("trim") or "").strip().lower()
    if "hatch" in trim and "hatch" not in model.lower():
        return f"{make} {model} Hatchback".strip()
    return f"{make} {model}".strip()


def load_listings(path: str | Path) -> list[CarListing]:
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        listings: list[CarListing] = []
        for row in reader:
            listings.append(
                CarListing(
                    vin=(row.get("vin") or "").strip(),
                    year=_to_int(row.get("year")),
                    make=(row.get("make") or "").strip(),
                    model=(row.get("model") or "").strip(),
                    trim=(row.get("trim") or "").strip(),
                    price=_to_float(row.get("price")),
                    mileage=_to_float(row.get("mileage")),
                    body_style=(row.get("body_style") or "").strip(),
                    cargo_cuft=_to_float(row.get("cargo_cuft")),
                    accidents=_to_int(row.get("accidents")),
                    owners=_to_int(row.get("owners"), 1),
                    prior_use=_normalize_prior_use(row),
                    title_status=_normalize_title_status(row),
                    model_key=_model_key(row),
                    notes=(row.get("notes") or "").strip(),
                )
            )
    return listings
