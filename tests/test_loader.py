from pathlib import Path

from src.used_car_optimizer.loader import load_listings


def test_load_listings_supports_legacy_columns(tmp_path: Path):
    sample = tmp_path / "cars.csv"
    sample.write_text(
        "vin,year,make,model,trim,body_style,price,mileage,cargo_cuft,accidents,owners,short_second_owner,rental_fleet,title_issue,model_key,notes\n"
        "abc,2018,Mazda,CX-5,Sport,SUV,19000,86000,59.6,0,2,No,Yes,No,Mazda CX-5,Test row\n",
        encoding="utf-8",
    )

    listings = load_listings(sample)

    assert len(listings) == 1
    assert listings[0].prior_use == "rental"
    assert listings[0].title_status == "clean"
    assert listings[0].model_key == "Mazda CX-5"
