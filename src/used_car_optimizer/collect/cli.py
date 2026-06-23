from __future__ import annotations

import argparse
from pathlib import Path

from .browser_capture import BrowserCaptureCollector
from .browser_snapshot import BrowserSnapshotCollector
from .dealer_com import DealerComLiveCollector
from .dealer_sources import SACRAMENTO_DEALER_SOURCES
from .manual_csv import ManualCsvCollector
from .pipeline import run_collection_pipeline
from .saved_html import SavedHtmlCollector


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect dealer inventory into the optimizer CSV format.")
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="Project root that contains data/, output/, and src/.",
    )
    parser.add_argument(
        "--dealer",
        default="all",
        help="Dealer source name to collect, or 'all'.",
    )
    parser.add_argument(
        "--mode",
        choices=["offline", "live", "browser", "all"],
        default="offline",
        help="Use offline files only, live dealer fetches only, browser snapshots only, or combine them.",
    )
    return parser


def _build_collectors(workspace_root: Path, dealer_filter: str, mode: str = "offline") -> list[object]:
    collectors: list[object] = []
    for source in SACRAMENTO_DEALER_SOURCES:
        if dealer_filter != "all" and source.name.lower() != dealer_filter.lower():
            continue
        if mode in {"offline", "all"}:
            collectors.append(SavedHtmlCollector(source, workspace_root))
        if mode in {"browser", "all"}:
            capture_collector = BrowserCaptureCollector(source, workspace_root)
            collectors.append(capture_collector)
            if not capture_collector.has_capture_files():
                collectors.append(BrowserSnapshotCollector(source, workspace_root))
        if mode in {"live", "all"} and source.source_type == "dealer_com":
            collectors.append(DealerComLiveCollector(source, workspace_root))

    manual_source_name = "Manual Dealer Uploads"
    if mode in {"offline", "all"} and dealer_filter in {"all", manual_source_name.lower()}:
        from .models import DealerSource

        manual_source = DealerSource(
            name=manual_source_name,
            source_type="manual_csv",
            base_url="local://manual",
            city="Sacramento, CA",
            notes="Local CSV drop folder for manual or exported dealer inventory files.",
        )
        collectors.append(ManualCsvCollector(manual_source, workspace_root))

    return collectors


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    workspace_root = Path(args.workspace_root).resolve()

    collectors = _build_collectors(workspace_root, args.dealer, args.mode)
    results = run_collection_pipeline(collectors, workspace_root)

    print(f"Collected {results['raw_count']} raw listings")
    print(f"Normalized {results['normalized_count']} listings")
    print(f"Exported {results['deduped_count']} deduped listings to data/dealer_inventory.csv")
    return 0
