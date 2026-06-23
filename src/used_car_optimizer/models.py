from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CarListing:
    vin: str
    year: int
    make: str
    model: str
    trim: str
    price: float
    mileage: float
    body_style: str
    cargo_cuft: float
    accidents: int
    owners: int
    prior_use: str
    title_status: str
    model_key: str
    notes: str


@dataclass
class ScoredCar:
    rank: int
    listing: CarListing
    age: int
    estimated_apr: float
    out_the_door_est: float
    amount_financed: float
    monthly_payment: float
    payment_score: float
    apr_score: float
    age_score: float
    mileage_score: float
    reliability_score: float
    cargo_score: float
    risk_score: float
    total_score: float
    recommendation: str
    reasons: list[str]
