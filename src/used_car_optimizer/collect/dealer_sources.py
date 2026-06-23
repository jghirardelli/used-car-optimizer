from __future__ import annotations

from .models import DealerSource


SACRAMENTO_DEALER_SOURCES: list[DealerSource] = [
    DealerSource(
        name="Maita Subaru",
        source_type="dealer_com",
        base_url="https://www.maitasubaru.com/used-inventory/index.htm",
        city="Sacramento, CA",
        notes="Dealer.com inventory pages appear to expose stable detail links, VINs, mileage, and prices in rendered inventory pages.",
        page_size=24,
        max_pages=2,
    ),
    DealerSource(
        name="Elk Grove Honda",
        source_type="dealer_com",
        base_url="https://www.elkgrovehonda.com/used-inventory/index.htm",
        city="Elk Grove, CA",
        notes="Dealer.com inventory pages appear to expose stable detail links and visible listing metadata in rendered inventory pages.",
        page_size=24,
        max_pages=2,
    ),
]
