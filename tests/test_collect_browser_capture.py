import json

from src.used_car_optimizer.collect.browser_capture import BrowserCaptureCollector
from src.used_car_optimizer.collect.models import DealerSource


def test_browser_capture_collector_reads_structured_json(tmp_path):
    capture_dir = tmp_path / "data" / "incoming" / "browser_captures"
    capture_dir.mkdir(parents=True)
    payload = [
        {
            "title": "2016 Subaru Forester 2.5i Touring",
            "url": "/used/Subaru/2016-Subaru-Forester-Sacramento-ceff3e94ac1829d84b57f24701e2db43.htm",
            "vin": "JF2SJAXC9GH405234",
            "mileage": "108995",
            "price": "15788",
            "body_style": "SUV",
            "location": "Sacramento, CA",
            "captured_at": "2026-06-23T19:00:00+00:00",
        }
    ]
    (capture_dir / "maita_subaru_page_1.json").write_text(json.dumps(payload), encoding="utf-8")

    source = DealerSource(
        name="Maita Subaru",
        source_type="dealer_com",
        base_url="https://www.maitasubaru.com/used-inventory/index.htm",
        city="Sacramento, CA",
    )
    collector = BrowserCaptureCollector(source, tmp_path)

    rows = collector.collect()

    assert len(rows) == 1
    assert rows[0].vin == "JF2SJAXC9GH405234"
    assert rows[0].price == "15788"
    assert rows[0].body_style == "SUV"


def test_browser_capture_collector_reads_schema_style_json(tmp_path):
    capture_dir = tmp_path / "data" / "incoming" / "browser_captures"
    capture_dir.mkdir(parents=True)
    payload = [
        {
            "name": "Used 2019 Subaru Crosstrek Hybrid Hybrid",
            "url": "https://www.maitasubaru.com/used/Subaru/2019-Subaru-Crosstrek-Hybrid-Sacramento-b540dc10ac18401abea45d0a0d651072.htm",
            "vehicleIdentificationNumber": "JF2GTDNCXKH348975",
            "offers": {"price": "17325"},
            "mileageFromOdometer": {"value": 128, "unitCode": "SMI"},
            "description": "Hybrid SUV available now.",
        }
    ]
    (capture_dir / "maita_subaru_structured_page_1.json").write_text(json.dumps(payload), encoding="utf-8")

    source = DealerSource(
        name="Maita Subaru",
        source_type="dealer_com",
        base_url="https://www.maitasubaru.com/used-inventory/index.htm",
        city="Sacramento, CA",
    )
    collector = BrowserCaptureCollector(source, tmp_path)

    rows = collector.collect()

    assert len(rows) == 1
    assert rows[0].model == "Crosstrek"
    assert rows[0].trim == "Hybrid Hybrid"
    assert rows[0].vin == "JF2GTDNCXKH348975"
    assert rows[0].price == "17325"
    assert rows[0].mileage == "128000"
    assert rows[0].body_style == "SUV"
    assert "rounded schema odometer" in rows[0].notes


def test_browser_capture_collector_detects_existing_capture_files(tmp_path):
    capture_dir = tmp_path / "data" / "incoming" / "browser_captures"
    capture_dir.mkdir(parents=True)
    (capture_dir / "maita_subaru_page_1.json").write_text("[]", encoding="utf-8")

    source = DealerSource(
        name="Maita Subaru",
        source_type="dealer_com",
        base_url="https://www.maitasubaru.com/used-inventory/index.htm",
        city="Sacramento, CA",
    )
    collector = BrowserCaptureCollector(source, tmp_path)

    assert collector.has_capture_files() is True
