from src.used_car_optimizer.collect.browser_snapshot import BrowserSnapshotCollector
from src.used_car_optimizer.collect.models import DealerSource


def test_browser_snapshot_parser_extracts_rendered_listing(tmp_path):
    source = DealerSource(
        name="Maita Subaru",
        source_type="dealer_com",
        base_url="https://www.maitasubaru.com/used-inventory/index.htm",
        city="Sacramento, CA",
    )
    collector = BrowserSnapshotCollector(source, tmp_path)
    snapshot = """
    - heading "2016 Subaru Forester 2.5i Touring" [level=2]:
      - link "2016 Subaru Forester 2.5i Touring":
        - /url: /used/Subaru/2016-Subaru-Forester-Sacramento-ceff3e94ac1829d84b57f24701e2db43.htm
    - list:
      - listitem: Variable
      - listitem: Ice Silver Metallic Exterior
      - listitem: Gray Interior
      - listitem: Stock # S21582
      - listitem: VIN JF2SJAXC9GH405234
      - listitem: 4 Engine
      - listitem: 108,995 miles Odometer
    - term: Maita Value Price
    - definition: $15,788
    """

    rows = collector._parse_snapshot(snapshot, "maita_subaru_page_1.txt")

    assert len(rows) == 1
    assert rows[0].vin == "JF2SJAXC9GH405234"
    assert rows[0].price == "15,788"
    assert rows[0].mileage == "108,995"
    assert rows[0].model == "Forester"

