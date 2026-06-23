from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urljoin

from .base import Collector
from .models import RawListing
from .time_utils import utc_timestamp


HEADING_LINK_PATTERN = re.compile(
    r'heading "(?P<title>\d{4} [^"]+)" \[level=2\]:(?:\r?\n)?\s*- link "(?P<link_title>[^"]+)":(?:\r?\n)?\s*- /url: (?P<url>.+)',
    re.IGNORECASE,
)
VIN_PATTERN = re.compile(r"\bVIN\s+([A-HJ-NPR-Z0-9]{11,17})\b", re.IGNORECASE)
MILEAGE_PATTERN = re.compile(r"\b([\d,]{2,})\s+miles\b", re.IGNORECASE)
PRICE_PATTERN = re.compile(r"\$([\d,]{3,})")
BODY_STYLE_PATTERN = re.compile(r"\b(SUV|Hatchback|Wagon|Sedan|Truck|Van|Coupe)\b", re.IGNORECASE)
TITLE_SPLIT_PATTERN = re.compile(r"^(?P<year>\d{4})\s+(?P<make>[A-Za-z]+)\s+(?P<rest>.+)$")


class BrowserSnapshotCollector(Collector):
    """
    Parses rendered DOM snapshots saved from a real browser session.

    This is the preferred fallback for dealer sites that block plain HTTP fetches.
    The browser does the rendering; the collector only turns that rendered output
    into normalized raw listings.
    """

    def collect(self) -> list[RawListing]:
        snapshot_dir = self.workspace_root / "data" / "incoming" / "browser_snapshots"
        if not snapshot_dir.exists():
            return []

        pattern = f"{self.source.name.lower().replace(' ', '_')}*.txt"
        rows: list[RawListing] = []
        for snapshot_path in sorted(snapshot_dir.glob(pattern)):
            snapshot_text = snapshot_path.read_text(encoding="utf-8")
            rows.extend(self._parse_snapshot(snapshot_text, snapshot_path.name))
        return rows

    def _parse_snapshot(self, snapshot_text: str, snapshot_name: str) -> list[RawListing]:
        rows: list[RawListing] = []
        matches = list(HEADING_LINK_PATTERN.finditer(snapshot_text))
        fetched_at = utc_timestamp()

        for index, match in enumerate(matches):
            title = _clean_text(match.group("title"))
            relative_url = match.group("url").strip().strip('"')
            full_url = urljoin(self.source.base_url, relative_url)

            next_start = matches[index + 1].start() if index + 1 < len(matches) else len(snapshot_text)
            context = _clean_text(snapshot_text[match.start() : next_start])

            year, make, model, trim = _split_title(title)
            vin_match = VIN_PATTERN.search(context)
            mileage_match = MILEAGE_PATTERN.search(context)
            price_match = PRICE_PATTERN.search(context)
            body_style_match = BODY_STYLE_PATTERN.search(title) or BODY_STYLE_PATTERN.search(context)

            listing_id = vin_match.group(1) if vin_match else full_url
            rows.append(
                RawListing(
                    source_name=self.source.name,
                    source_type="browser_snapshot",
                    listing_id=listing_id,
                    url=full_url,
                    fetched_at=fetched_at,
                    seller_name=self.source.name,
                    location=self.source.city,
                    vin=vin_match.group(1) if vin_match else "",
                    year=year,
                    make=make,
                    model=model,
                    trim=trim,
                    price=price_match.group(1) if price_match else "",
                    mileage=mileage_match.group(1) if mileage_match else "",
                    body_style=body_style_match.group(1) if body_style_match else "",
                    title_status="clean",
                    prior_use="",
                    owners="",
                    accidents="",
                    cargo_cuft="",
                    notes=f"Parsed rendered browser snapshot: {snapshot_name}",
                    raw_payload={"title": title, "context": context[:1500]},
                )
            )

        return rows


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _split_title(title: str) -> tuple[str, str, str, str]:
    match = TITLE_SPLIT_PATTERN.match(title)
    if not match:
        return "", "", title.strip(), ""

    year = match.group("year")
    make = match.group("make")
    rest = match.group("rest").strip()
    parts = rest.split(" ", 1)
    model = parts[0]
    trim = parts[1] if len(parts) > 1 else ""
    return year, make, model, trim
