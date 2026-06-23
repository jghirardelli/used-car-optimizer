from pathlib import Path

from src.used_car_optimizer.collect.cli import _build_collectors
from src.used_car_optimizer.collect.pipeline import run_collection_pipeline


def test_collection_pipeline_exports_optimizer_csv(tmp_path: Path):
    manual_dir = tmp_path / "data" / "incoming" / "manual"
    manual_dir.mkdir(parents=True)
    (manual_dir / "dealer.csv").write_text(
        "listing_id,url,seller_name,location,vin,year,make,model,trim,price,mileage,body_style,title_status,prior_use,owners,accidents,cargo_cuft\n"
        "abc,https://example.com/car,Example Dealer,Sacramento,1HGBH41JXMN109186,2019,Honda,CR-V,EX,21995,54000,SUV,clean,lease,1,0,75\n",
        encoding="utf-8",
    )

    collectors = _build_collectors(tmp_path, "manual dealer uploads")
    results = run_collection_pipeline(collectors, tmp_path)

    export_path = tmp_path / "data" / "dealer_inventory.csv"
    assert results["raw_count"] == 1
    assert export_path.exists()
    content = export_path.read_text(encoding="utf-8")
    assert "Honda,CR-V" in content
    assert "confidence=high" in content

