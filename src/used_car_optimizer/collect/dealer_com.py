from __future__ import annotations

import re
from urllib.parse import urljoin

from .base import Collector
from .fetch import fetch_text, save_snapshot
from .models import RawListing
from .time_utils import utc_timestamp


LISTING_LINK_PATTERN = re.compile(
    r'href="(?P<path>/(?:used|certified)/[^"]+?\.htm)"[^>]*>(?P<title>[^<]+)</a>',
    re.IGNORECASE,
)
PRICE_PATTERN = re.compile(r"\$([\d,]{3,})")
VIN_PATTERN = re.compile(r"\bVIN\s+([A-HJ-NPR-Z0-9]{11,17})\b", re.IGNORECASE)
MILEAGE_PATTERN = re.compile(r"\b([\d,]{2,})\s+miles\b", re.IGNORECASE)
STOCK_PATTERN = re.compile(r"\bStock\s*#\s*([A-Z0-9-]+)\b", re.IGNORECASE)
BODY_STYLE_PATTERN = re.compile(r"\b(SUV|Hatchback|Wagon|Sedan|Truck|Van|Coupe)\b", re.IGNORECASE)
TITLE_SPLIT_PATTERN = re.compile(r"^(?P<year>\d{4})\s+(?P<make>[A-Za-z]+)\s+(?P<rest>.+)$")


class DealerComLiveCollector(Collector):
    """
    Fetches Dealer.com-style inventory pages directly.

    The design goal is auditability:
    - fetch a small number of pages
    - save the raw HTML snapshot
    - parse visible listing fields conservatively
    """

    def collect(self) -> list[RawListing]:
        rows: list[RawListing] = []
        fetched_at = utc_timestamp()

        for page_index in range(self.source.max_pages):
            start = page_index * self.source.page_size
            url = self.source.base_url if start == 0 else f"{self.source.base_url}?start={start}"
            html = fetch_text(url)

            snapshot_name = f"{self.source.name.lower().replace(' ', '_')}_page_{page_index + 1}.html"
            save_snapshot(
                self.workspace_root / "data" / "incoming" / "html_snapshots" / snapshot_name,
                html,
            )

            rows.extend(self._parse_inventory_page(html, fetched_at))

            if "Go to next page" not in html and "?start=" not in html:
                break

        return rows

    def _parse_inventory_page(self, html: str, fetched_at: str) -> list[RawListing]:
        listings: list[RawListing] = []
        seen_urls: set[str] = set()

        for match in LISTING_LINK_PATTERN.finditer(html):
            relative_path = match.group("path")
            title = _clean_text(match.group("title"))
            full_url = urljoin(self.source.base_url, relative_path)
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            window_start = max(0, match.start() - 2500)
            window_end = min(len(html), match.end() + 2500)
            context = _clean_text(html[window_start:window_end])

            year, make, model, trim = _split_title(title)
            vin_match = VIN_PATTERN.search(context)
            price_match = PRICE_PATTERN.search(context)
            mileage_match = MILEAGE_PATTERN.search(context)
            stock_match = STOCK_PATTERN.search(context)
            body_style_match = BODY_STYLE_PATTERN.search(title) or BODY_STYLE_PATTERN.search(context)

            listing_id = vin_match.group(1) if vin_match else stock_match.group(1) if stock_match else relative_path
            listings.append(
                RawListing(
                    source_name=self.source.name,
                    source_type="dealer_com_live",
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
                    notes=f"Fetched live from {self.source.name}",
                    raw_payload={"title": title, "context": context[:1000]},
                )
            )

        return listings


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
