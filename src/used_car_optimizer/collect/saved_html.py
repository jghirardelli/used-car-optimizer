from __future__ import annotations

from pathlib import Path

from .base import Collector
from .models import RawListing
from .parsers import extract_json_ld_blocks, first_text, flatten_vehicle_items
from .time_utils import utc_timestamp


class SavedHtmlCollector(Collector):
    """
    Parses dealer HTML pages saved into `data/incoming/html_snapshots/`.

    This is the first automation-friendly step toward live scraping: we practice
    extracting stable structured data without depending on real-time network runs.
    """

    def collect(self) -> list[RawListing]:
        snapshot_dir = self.workspace_root / "data" / "incoming" / "html_snapshots"
        if not snapshot_dir.exists():
            return []

        rows: list[RawListing] = []
        pattern = f"{self.source.name.lower().replace(' ', '_')}*.html"
        for html_path in sorted(snapshot_dir.glob(pattern)):
            html = html_path.read_text(encoding="utf-8")
            vehicle_items = flatten_vehicle_items(extract_json_ld_blocks(html))
            for index, item in enumerate(vehicle_items, start=1):
                offers = item.get("offers")
                if isinstance(offers, list):
                    offer = offers[0] if offers else {}
                elif isinstance(offers, dict):
                    offer = offers
                else:
                    offer = {}

                listing_id = first_text(item.get("vehicleIdentificationNumber")) or first_text(item.get("sku")) or f"{html_path.stem}-{index}"
                rows.append(
                    RawListing(
                        source_name=self.source.name,
                        source_type="saved_html",
                        listing_id=listing_id,
                        url=first_text(item.get("url")) or self.source.base_url,
                        fetched_at=utc_timestamp(),
                        seller_name=first_text(item.get("seller")) or self.source.name,
                        location=self.source.city,
                        vin=first_text(item.get("vehicleIdentificationNumber")),
                        year=first_text(item.get("vehicleModelDate")) or first_text(item.get("modelDate")),
                        make=first_text(item.get("brand")),
                        model=first_text(item.get("model")),
                        trim=first_text(item.get("name")),
                        price=first_text(offer.get("price")),
                        mileage=first_text(item.get("mileageFromOdometer")),
                        body_style=first_text(item.get("bodyType")),
                        title_status=first_text(item.get("vehicleTitle")) or "clean",
                        prior_use=first_text(item.get("vehicleHistory")),
                        owners="",
                        accidents="",
                        cargo_cuft="",
                        notes=f"Parsed structured data from saved HTML: {html_path.name}",
                        raw_payload=item,
                    )
                )
        return rows
