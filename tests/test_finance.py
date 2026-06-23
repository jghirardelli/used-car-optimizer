from src.used_car_optimizer.finance import (
    estimate_apr,
    estimate_monthly_payment,
    estimate_out_the_door_price,
)


CONFIG = {
    "base_apr": 0.065,
    "apr_adjustments": {
        "year_2016_or_older": 0.015,
        "mileage_over_100k": 0.01,
        "mileage_over_120k": 0.02,
        "mileage_over_150k": 0.035,
    },
}


def test_estimate_out_the_door_price():
    result = estimate_out_the_door_price(19000, 0.0875, 425, 225)
    assert result == 21312.5


def test_estimate_monthly_payment():
    result = estimate_monthly_payment(16312.5, 0.065, 72)
    assert round(result, 2) == 274.21


def test_estimate_apr_penalties_stack():
    result = estimate_apr(2014, 125000, CONFIG)
    assert round(result, 4) == 0.11
