from __future__ import annotations

from datetime import datetime

from .finance import estimate_apr, estimate_monthly_payment, estimate_out_the_door_price
from .models import CarListing, ScoredCar


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def _age_score(age: int) -> float:
    if age <= 3:
        return 95.0
    if age <= 5:
        return 88.0
    if age <= 8:
        return 78.0
    if age <= 10:
        return 68.0
    if age <= 12:
        return 52.0
    return 35.0


def _mileage_score(mileage: float) -> float:
    if mileage <= 30000:
        return 95.0
    if mileage <= 60000:
        return 88.0
    if mileage <= 90000:
        return 75.0
    if mileage <= 110000:
        return 60.0
    if mileage <= 130000:
        return 45.0
    if mileage <= 150000:
        return 30.0
    return 15.0


def _payment_score(payment: float, budget: float) -> float:
    if payment <= budget:
        cushion = budget - payment
        return _clamp(92.0 + min(cushion / 3.0, 8.0))
    return _clamp(92.0 - (payment - budget) * 0.45)


def _apr_score(apr: float) -> float:
    apr_percent = apr * 100
    if apr_percent <= 6.5:
        return 92.0
    if apr_percent <= 8.0:
        return 82.0
    if apr_percent <= 9.5:
        return 68.0
    if apr_percent <= 11.0:
        return 52.0
    return 32.0


def _cargo_score(listing: CarListing, config: dict) -> float:
    model_scores = config["reliability_and_cargo_scores"]
    if listing.model_key in model_scores:
        return float(model_scores[listing.model_key]["cargo"])

    score = 50.0
    if listing.body_style in config["preferred_body_styles"]:
        score += 12.0
    if listing.cargo_cuft >= 70:
        score += 20.0
    elif listing.cargo_cuft >= 55:
        score += 12.0
    elif listing.cargo_cuft >= 45:
        score += 6.0
    return _clamp(score)


def _reliability_score(listing: CarListing, config: dict) -> float:
    model_scores = config["reliability_and_cargo_scores"]
    if listing.model_key in model_scores:
        return float(model_scores[listing.model_key]["reliability"])

    score = 68.0
    haystack = f"{listing.make} {listing.model} {listing.trim}".lower()
    for keyword in config["preferred_vehicle_keywords"]:
        if keyword.lower() in haystack:
            score += 10.0
            break
    return _clamp(score)


def _risk_score(listing: CarListing) -> tuple[float, list[str]]:
    score = 90.0
    reasons: list[str] = []

    if listing.accidents > 0:
        penalty = min(30.0, listing.accidents * 14.0)
        score -= penalty
        reasons.append(f"{listing.accidents} reported accident(s)")

    if listing.owners >= 4:
        score -= 18.0
        reasons.append("many prior owners")
    elif listing.owners == 3:
        score -= 10.0
        reasons.append("three prior owners")
    elif listing.owners == 2:
        score -= 4.0

    prior_use = listing.prior_use.lower()
    if "rental" in prior_use or "fleet" in prior_use:
        score -= 16.0
        reasons.append("rental or fleet history")
    elif "lease" in prior_use:
        score -= 5.0
        reasons.append("lease history")
    elif "short-term" in prior_use:
        score -= 7.0
        reasons.append("short ownership history")

    title_status = listing.title_status.lower()
    if "salvage" in title_status or "rebuilt" in title_status:
        score -= 45.0
        reasons.append("salvage or rebuilt title")
    elif "title issue" in title_status or "lemon" in title_status:
        score -= 35.0
        reasons.append("title history concern")

    return _clamp(score), reasons


def score_listing(listing: CarListing, config: dict, current_year: int | None = None) -> ScoredCar:
    current_year = current_year or datetime.now().year
    age = current_year - listing.year if listing.year else 99

    estimated_apr = estimate_apr(listing.year, listing.mileage, config)
    out_the_door = estimate_out_the_door_price(
        price=listing.price,
        tax_rate=float(config["tax_rate"]),
        registration_and_dmv_fee=float(config["registration_and_dmv_fee"]),
        dealer_fee=float(config["dealer_fee"]),
    )
    amount_financed = max(0.0, round(out_the_door - float(config["down_payment"]), 2))
    monthly_payment = estimate_monthly_payment(
        principal=amount_financed,
        apr=estimated_apr,
        months=int(config["loan_term_months"]),
    )

    payment_score = _payment_score(monthly_payment, float(config["monthly_budget"]))
    apr_score = _apr_score(estimated_apr)
    age_score = _age_score(age)
    mileage_score = _mileage_score(listing.mileage)
    reliability_score = _reliability_score(listing, config)
    cargo_score = _cargo_score(listing, config)
    risk_score, reasons = _risk_score(listing)

    total_score = round(
        payment_score * 0.23
        + apr_score * 0.12
        + age_score * 0.11
        + mileage_score * 0.11
        + reliability_score * 0.18
        + cargo_score * 0.13
        + risk_score * 0.12,
        1,
    )

    if monthly_payment > float(config["monthly_budget"]) + 40:
        recommendation = "Pass"
        reasons.insert(0, "monthly payment is well above target")
    elif "salvage" in listing.title_status.lower() or "rebuilt" in listing.title_status.lower():
        recommendation = "Pass"
        reasons.insert(0, "title status is too risky")
    elif total_score >= 84:
        recommendation = "Strong fit"
    elif total_score >= 70:
        recommendation = "Borderline"
    else:
        recommendation = "Pass"

    if listing.body_style not in config["preferred_body_styles"]:
        reasons.append("body style is outside the preferred list")
    if listing.cargo_cuft and listing.cargo_cuft < 40:
        reasons.append("cargo space looks small")
    if not reasons and recommendation == "Strong fit":
        reasons.append("well balanced for budget, cargo, and risk")

    return ScoredCar(
        rank=0,
        listing=listing,
        age=age,
        estimated_apr=round(estimated_apr * 100, 2),
        out_the_door_est=out_the_door,
        amount_financed=amount_financed,
        monthly_payment=monthly_payment,
        payment_score=round(payment_score, 1),
        apr_score=round(apr_score, 1),
        age_score=round(age_score, 1),
        mileage_score=round(mileage_score, 1),
        reliability_score=round(reliability_score, 1),
        cargo_score=round(cargo_score, 1),
        risk_score=round(risk_score, 1),
        total_score=total_score,
        recommendation=recommendation,
        reasons=reasons,
    )


def rank_listings(listings: list[CarListing], config: dict, current_year: int | None = None) -> list[ScoredCar]:
    scored = [score_listing(listing, config, current_year=current_year) for listing in listings]
    scored.sort(key=lambda item: (item.total_score, -item.monthly_payment), reverse=True)
    for index, item in enumerate(scored, start=1):
        item.rank = index
    return scored
