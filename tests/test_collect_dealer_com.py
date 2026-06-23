from src.used_car_optimizer.collect.dealer_com import DealerComLiveCollector
from src.used_car_optimizer.collect.models import DealerSource


def test_dealer_com_parser_extracts_basic_listing_fields(tmp_path):
    source = DealerSource(
        name="Test Dealer",
        source_type="dealer_com",
        base_url="https://example.com/used-inventory/index.htm",
        city="Sacramento, CA",
    )
    collector = DealerComLiveCollector(source, tmp_path)
    html = """
    <html><body>
      <a href="/used/Subaru/2016-Subaru-Forester-Sacramento-abc123.htm">2016 Subaru Forester 2.5i Touring</a>
      <div>VIN JF2SJAXC9GH405234</div>
      <div>108,995 miles Odometer</div>
      <div>Maita Value Price</div>
      <div>$15,788</div>
      <div>SUV</div>
      <div>Stock # S21582</div>
    </body></html>
    """

    rows = collector._parse_inventory_page(html, "2026-06-23T00:00:00+00:00")

    assert len(rows) == 1
    assert rows[0].vin == "JF2SJAXC9GH405234"
    assert rows[0].price == "15,788"
    assert rows[0].mileage == "108,995"
    assert rows[0].year == "2016"
    assert rows[0].make == "Subaru"
    assert rows[0].model == "Forester"

