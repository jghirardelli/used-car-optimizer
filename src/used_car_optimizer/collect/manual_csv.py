from __future__ import annotations

import csv
from pathlib import Path

from .base import Collector
from .models import RawListing
from .time_utils import utc_timestamp


class ManualCsvCollector(Collector):
    """
    Reads dealer inventory exports that you manually save into `data/incoming/manual/`.

    This is the safest starting point because the dealer or marketplace already gave
    you the file, so collection is reproducible and easy to audit.
    """

    def collect(self) -> list[RawListing]:
        incoming_dir = self.workspace_root / "data" / "incoming" / "manual"
        if not incoming_dir.exists():
            return []

        rows: list[RawListing] = []
        for csv_path in sorted(incoming_dir.glob("*.csv")):
            with csv_path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                for index, row in enumerate(reader, start=1):
                    listing_id = str(row.get("listing_id") or row.get("vin") or f"{csv_path.stem}-{index}")
                    rows.append(
                        RawListing(
                            source_name=self.source.name,
                            source_type="manual_csv",
                            listing_id=listing_id,
                            url=str(row.get("url") or ""),
                            fetched_at=utc_timestamp(),
                            seller_name=str(row.get("seller_name") or self.source.name),
                            location=str(row.get("location") or self.source.city),
                            vin=str(row.get("vin") or ""),
                            year=str(row.get("year") or ""),
                            make=str(row.get("make") or ""),
                            model=str(row.get("model") or ""),
                            trim=str(row.get("trim") or ""),
                            price=str(row.get("price") or ""),
                            mileage=str(row.get("mileage") or ""),
                            body_style=str(row.get("body_style") or ""),
                            title_status=str(row.get("title_status") or ""),
                            prior_use=str(row.get("prior_use") or ""),
                            owners=str(row.get("owners") or ""),
                            accidents=str(row.get("accidents") or ""),
                            cargo_cuft=str(row.get("cargo_cuft") or ""),
                            notes=f"Imported from manual CSV: {csv_path.name}",
                            raw_payload=dict(row),
                        )
                    )
        return rows
