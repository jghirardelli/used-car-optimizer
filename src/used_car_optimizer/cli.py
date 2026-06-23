from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .loader import load_listings
from .reporting import write_markdown_report, write_ranked_csv
from .scoring import rank_listings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rank used car listings by affordability and fit.")
    parser.add_argument("--input", default="data/sample_cars.csv", help="Path to the input CSV file.")
    parser.add_argument("--config", default="config.json", help="Path to the config JSON file.")
    parser.add_argument("--output-dir", default="output", help="Directory for generated files.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = load_config(args.config)
    listings = load_listings(args.input)
    ranked = rank_listings(listings, config)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / f"{Path(args.input).stem}_ranked.csv"
    report_path = output_dir / f"{Path(args.input).stem}_report.md"

    write_ranked_csv(ranked, csv_path)
    write_markdown_report(ranked, report_path, config)

    print(f"Wrote ranked CSV to {csv_path}")
    print(f"Wrote markdown report to {report_path}")
    for item in ranked[:5]:
        print(
            f"{item.rank}. {item.listing.year} {item.listing.make} {item.listing.model} "
            f"- ${item.monthly_payment:.2f}/mo - score {item.total_score} - {item.recommendation}"
        )
    return 0
