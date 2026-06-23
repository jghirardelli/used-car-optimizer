from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urljoin

from .base import Collector
from .models import RawListing
from .time_utils import utc_timestamp


TITLE_SPLIT_PATTERN = re.compile(r"^(?P<year>\d{4})\s+(?P<make>[A-Za-z]+)\s+(?P<rest>.+)$")


class BrowserCaptureCollector(Collector):
    """
    Reads structured browser capture JSON files produced from a rendered page.

    This is more reliable than plain text snapshots because the browser-side
    extraction can preserve card-level fields directly.
    """

    def collect(self) -> list[RawListing]:
        capture_dir = self.capture_dir()
        if not capture_dir.exists():
            return []

        pattern = self.capture_pattern()
        rows: list[RawListing] = []
        for capture_path in sorted(capture_dir.glob(pattern)):
            entries = json.loads(capture_path.read_text(encoding="utf-8"))
            if not isinstance(entries, list):
                continue

            for entry in entries:
                if not isinstance(entry, dict):
                    continue

                title = _extract_title(entry)
                year, make, model, trim = _split_title(title)
                vin = _extract_vin(entry)
                url = _extract_url(entry)
                mileage, mileage_note = _extract_mileage(entry)
                notes = f"Parsed structured browser capture: {capture_path.name}"
                if mileage_note:
                    notes = f"{notes}; {mileage_note}"
                rows.append(
                    RawListing(
                        source_name=self.source.name,
                        source_type="browser_capture",
                        listing_id=vin or url or title,
                        url=urljoin(self.source.base_url, url) if url else self.source.base_url,
                        fetched_at=str(entry.get("captured_at") or utc_timestamp()),
                        seller_name=self.source.name,
                        location=str(entry.get("location") or self.source.city),
                        vin=vin,
                        year=year,
                        make=make,
                        model=model,
                        trim=trim,
                        price=_extract_price(entry),
                        mileage=mileage,
                        body_style=_extract_body_style(entry),
                        title_status=str(entry.get("title_status") or "clean"),
                        prior_use=str(entry.get("prior_use") or ""),
                        owners=str(entry.get("owners") or ""),
                        accidents=str(entry.get("accidents") or ""),
                        cargo_cuft=str(entry.get("cargo_cuft") or ""),
                        notes=notes,
                        raw_payload=entry,
                    )
                )
        return rows

    def capture_dir(self) -> Path:
        return self.workspace_root / "data" / "incoming" / "browser_captures"

    def capture_pattern(self) -> str:
        return f"{self.source.name.lower().replace(' ', '_')}*.json"

    def has_capture_files(self) -> bool:
        return any(self.capture_dir().glob(self.capture_pattern()))


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


def _extract_title(entry: dict) -> str:
    title = str(entry.get("title") or entry.get("name") or "").strip()
    return title.removeprefix("Used ").removeprefix("Certified ").strip()


def _extract_vin(entry: dict) -> str:
    return str(entry.get("vin") or entry.get("vehicleIdentificationNumber") or "").strip()


def _extract_url(entry: dict) -> str:
    return str(entry.get("url") or entry.get("offers", {}).get("url") or "").strip()


def _extract_price(entry: dict) -> str:
    direct_price = entry.get("price")
    if direct_price not in (None, ""):
        return str(direct_price).strip()
    return str(entry.get("offers", {}).get("price") or "").strip()


def _extract_mileage(entry: dict) -> tuple[str, str]:
    direct_mileage = entry.get("mileage")
    if direct_mileage not in (None, ""):
        return str(direct_mileage).strip(), ""

    odometer = entry.get("mileageFromOdometer")
    if not isinstance(odometer, dict):
        return "", ""

    value = odometer.get("value")
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "", ""

    # Dealer.com schema data often rounds used-car mileage down to whole thousands.
    if 0 < numeric < 1000:
        return str(int(numeric * 1000)), "Mileage estimated from rounded schema odometer value"

    return str(int(numeric)), ""


def _extract_body_style(entry: dict) -> str:
    body_style = str(entry.get("body_style") or entry.get("bodyType") or "").strip()
    if body_style:
        return body_style

    description = str(entry.get("description") or "").lower()
    if "suv" in description:
        return "SUV"
    if "wagon" in description:
        return "Wagon"
    if "hatchback" in description or "hatch" in description:
        return "Hatchback"
    if "sedan" in description:
        return "Sedan"
    return ""
