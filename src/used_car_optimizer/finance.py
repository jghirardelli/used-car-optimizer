from __future__ import annotations


def estimate_out_the_door_price(
    price: float,
    tax_rate: float,
    registration_and_dmv_fee: float,
    dealer_fee: float,
) -> float:
    return round(price * (1 + tax_rate) + registration_and_dmv_fee + dealer_fee, 2)


def estimate_apr(year: int, mileage: float, config: dict) -> float:
    apr = float(config["base_apr"])
    adjustments = config["apr_adjustments"]

    if year and year <= 2016:
        apr += float(adjustments["year_2016_or_older"])
    if mileage > 100000:
        apr += float(adjustments["mileage_over_100k"])
    if mileage > 120000:
        apr += float(adjustments["mileage_over_120k"])
    if mileage > 150000:
        apr += float(adjustments["mileage_over_150k"])

    return apr


def estimate_monthly_payment(principal: float, apr: float, months: int) -> float:
    if principal <= 0:
        return 0.0
    if months <= 0:
        raise ValueError("Loan term must be positive")

    monthly_rate = apr / 12.0
    if monthly_rate == 0:
        return round(principal / months, 2)

    payment = (
        principal
        * monthly_rate
        * (1 + monthly_rate) ** months
        / ((1 + monthly_rate) ** months - 1)
    )
    return round(payment, 2)
