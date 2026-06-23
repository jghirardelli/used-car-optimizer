from src.used_car_optimizer.models import CarListing
from src.used_car_optimizer.scoring import rank_listings, score_listing


CONFIG = {
    "location": "Sacramento, CA",
    "monthly_budget": 300.0,
    "down_payment": 5000.0,
    "loan_term_months": 72,
    "tax_rate": 0.0875,
    "registration_and_dmv_fee": 425.0,
    "dealer_fee": 225.0,
    "base_apr": 0.065,
    "apr_adjustments": {
        "year_2016_or_older": 0.015,
        "mileage_over_100k": 0.01,
        "mileage_over_120k": 0.02,
        "mileage_over_150k": 0.035,
    },
    "preferred_body_styles": ["SUV", "Hatchback", "Wagon"],
    "preferred_vehicle_keywords": ["CR-V", "RAV4", "CX-5", "Fit"],
    "reliability_and_cargo_scores": {
        "Honda CR-V": {"reliability": 88, "cargo": 90},
        "Mazda CX-5": {"reliability": 84, "cargo": 82},
    },
}


def test_score_listing_flags_salvage_title():
    listing = CarListing(
        vin="1",
        year=2015,
        make="Honda",
        model="CR-V",
        trim="EX",
        price=16500,
        mileage=82000,
        body_style="SUV",
        cargo_cuft=70.9,
        accidents=0,
        owners=2,
        prior_use="",
        title_status="salvage",
        model_key="Honda CR-V",
        notes="",
    )

    scored = score_listing(listing, CONFIG, current_year=2026)

    assert scored.recommendation == "Pass"
    assert any("title" in reason.lower() for reason in scored.reasons)


def test_rank_listings_prefers_stronger_fit():
    strong = CarListing(
        vin="1",
        year=2018,
        make="Mazda",
        model="CX-5",
        trim="Sport",
        price=19000,
        mileage=86000,
        body_style="SUV",
        cargo_cuft=59.6,
        accidents=0,
        owners=2,
        prior_use="",
        title_status="clean",
        model_key="Mazda CX-5",
        notes="",
    )
    weak = CarListing(
        vin="2",
        year=2021,
        make="Mazda",
        model="CX-30",
        trim="AWD",
        price=21000,
        mileage=40000,
        body_style="SUV",
        cargo_cuft=45.2,
        accidents=0,
        owners=2,
        prior_use="short-term resale",
        title_status="clean",
        model_key="Mazda CX-30",
        notes="",
    )

    ranked = rank_listings([weak, strong], CONFIG, current_year=2026)

    assert ranked[0].listing.model == "CX-5"
    assert ranked[0].rank == 1
