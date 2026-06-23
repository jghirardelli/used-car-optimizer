from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DealerSource:
    name: str
    source_type: str
    base_url: str
    city: str
    enabled: bool = True
    notes: str = ""
    page_size: int = 24
    max_pages: int = 2


@dataclass
class RawListing:
    source_name: str
    source_type: str
    listing_id: str
    url: str
    fetched_at: str
    seller_name: str
    location: str
    vin: str = ""
    year: str = ""
    make: str = ""
    model: str = ""
    trim: str = ""
    price: str = ""
    mileage: str = ""
    body_style: str = ""
    title_status: str = ""
    prior_use: str = ""
    owners: str = ""
    accidents: str = ""
    cargo_cuft: str = ""
    notes: str = ""
    raw_payload: dict[str, object] = field(default_factory=dict)


@dataclass
class NormalizedListing:
    year: str
    make: str
    model: str
    trim: str
    price: str
    mileage: str
    body_style: str
    cargo_cuft: str
    vin: str
    accidents: str
    owners: str
    prior_use: str
    title_status: str
    source_name: str
    source_type: str
    source_url: str
    location: str
    notes: str
    confidence: str
