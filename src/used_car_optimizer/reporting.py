from __future__ import annotations

import csv
from pathlib import Path

from .models import ScoredCar


CSV_FIELDS = [
    "rank",
    "vin",
    "year",
    "make",
    "model",
    "trim",
    "body_style",
    "price",
    "mileage",
    "cargo_cuft",
    "accidents",
    "owners",
    "prior_use",
    "title_status",
    "estimated_apr",
    "out_the_door_est",
    "amount_financed",
    "monthly_payment",
    "payment_score",
    "apr_score",
    "age_score",
    "mileage_score",
    "reliability_score",
    "cargo_score",
    "risk_score",
    "total_score",
    "recommendation",
    "notes",
]


def write_ranked_csv(scored_cars: list[ScoredCar], path: str | Path) -> None:
    output_path = Path(path)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for item in scored_cars:
            writer.writerow(
                {
                    "rank": item.rank,
                    "vin": item.listing.vin,
                    "year": item.listing.year,
                    "make": item.listing.make,
                    "model": item.listing.model,
                    "trim": item.listing.trim,
                    "body_style": item.listing.body_style,
                    "price": item.listing.price,
                    "mileage": item.listing.mileage,
                    "cargo_cuft": item.listing.cargo_cuft,
                    "accidents": item.listing.accidents,
                    "owners": item.listing.owners,
                    "prior_use": item.listing.prior_use,
                    "title_status": item.listing.title_status,
                    "estimated_apr": item.estimated_apr,
                    "out_the_door_est": item.out_the_door_est,
                    "amount_financed": item.amount_financed,
                    "monthly_payment": item.monthly_payment,
                    "payment_score": item.payment_score,
                    "apr_score": item.apr_score,
                    "age_score": item.age_score,
                    "mileage_score": item.mileage_score,
                    "reliability_score": item.reliability_score,
                    "cargo_score": item.cargo_score,
                    "risk_score": item.risk_score,
                    "total_score": item.total_score,
                    "recommendation": item.recommendation,
                    "notes": item.listing.notes,
                }
            )


def write_markdown_report(scored_cars: list[ScoredCar], path: str | Path, config: dict) -> None:
    output_path = Path(path)
    lines = [
        "# Used Car Optimizer Report",
        "",
        f"- Location: {config['location']}",
        f"- Monthly payment target: under ${config['monthly_budget']:.0f}",
        f"- Down payment assumption: ${config['down_payment']:.0f}",
        f"- Loan term: {config['loan_term_months']} months",
        "",
        "## Top Picks",
        "",
    ]

    top_picks = scored_cars[:5]
    for item in top_picks:
        lines.extend(
            [
                f"### {item.rank}. {item.listing.year} {item.listing.make} {item.listing.model} {item.listing.trim}".strip(),
                f"- Recommendation: {item.recommendation}",
                f"- Total score: {item.total_score}",
                f"- Estimated monthly payment: ${item.monthly_payment:.2f}",
                f"- Estimated APR: {item.estimated_apr:.2f}%",
                f"- Out-the-door estimate: ${item.out_the_door_est:.2f}",
                f"- Cargo space: {item.listing.cargo_cuft:.1f} cu ft",
                f"- History summary: {', '.join(item.reasons[:3]) if item.reasons else 'No major risk flags in the input data'}",
                "",
            ]
        )

    lines.extend(["## Full Ranking", ""])
    for item in scored_cars:
        lines.append(
            f"- #{item.rank}: {item.listing.year} {item.listing.make} {item.listing.model} | "
            f"score {item.total_score} | ${item.monthly_payment:.2f}/mo | {item.recommendation}"
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
