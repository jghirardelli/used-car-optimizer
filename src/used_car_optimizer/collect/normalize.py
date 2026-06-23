from __future__ import annotations

import re

from .models import NormalizedListing, RawListing


BODY_STYLE_ALIASES = {
    "sport utility": "SUV",
    "suv": "SUV",
    "crossover": "SUV",
    "hatchback": "Hatchback",
    "wagon": "Wagon",
}


def _digits_only(value: str) -> str:
    return re.sub(r"[^\d]", "", value or "")


def _normalize_price(value: str) -> str:
    digits = _digits_only(value)
    return digits if digits else ""


def _normalize_mileage(value: str) -> str:
    digits = _digits_only(value)
    return digits if digits else ""


def _normalize_body_style(value: str) -> str:
    lowered = (value or "").strip().lower()
    if not lowered:
        return ""
    for key, normalized in BODY_STYLE_ALIASES.items():
        if key in lowered:
            return normalized
    return value.strip()


def _confidence_for(raw: RawListing) -> str:
    signals = 0
    if raw.vin:
        signals += 1
    if raw.price:
        signals += 1
    if raw.mileage:
        signals += 1
    if raw.year and raw.make and raw.model:
        signals += 1

    if signals >= 4:
        return "high"
    if signals >= 2:
        return "medium"
    return "low"


def normalize_listing(raw: RawListing) -> NormalizedListing:
    trim = raw.trim.strip()
    if trim and raw.model and trim.lower().startswith(raw.model.lower()):
        trim = trim[len(raw.model) :].strip(" -")

    return NormalizedListing(
        year=raw.year.strip(),
        make=raw.make.strip(),
        model=raw.model.strip(),
        trim=trim,
        price=_normalize_price(raw.price),
        mileage=_normalize_mileage(raw.mileage),
        body_style=_normalize_body_style(raw.body_style),
        cargo_cuft=raw.cargo_cuft.strip(),
        vin=raw.vin.strip(),
        accidents=raw.accidents.strip(),
        owners=raw.owners.strip(),
        prior_use=raw.prior_use.strip(),
        title_status=(raw.title_status or "clean").strip(),
        source_name=raw.source_name,
        source_type=raw.source_type,
        source_url=raw.url.strip(),
        location=raw.location.strip(),
        notes=raw.notes.strip(),
        confidence=_confidence_for(raw),
    )


def should_keep_listing(listing: NormalizedListing) -> bool:
    if not listing.price or not listing.year or not listing.make or not listing.model:
        return False
    if listing.title_status.lower() in {"salvage", "rebuilt"}:
        return True
    return True
