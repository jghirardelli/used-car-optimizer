from src.used_car_optimizer.collect.parsers import extract_json_ld_blocks, flatten_vehicle_items


def test_extract_json_ld_blocks_and_find_vehicle():
    html = """
    <html><head>
      <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Car",
          "brand": "Toyota",
          "model": "RAV4",
          "vehicleModelDate": "2020",
          "vehicleIdentificationNumber": "123VIN",
          "offers": {"price": "21995"}
        }
      </script>
    </head></html>
    """

    blocks = extract_json_ld_blocks(html)
    vehicles = flatten_vehicle_items(blocks)

    assert len(blocks) == 1
    assert len(vehicles) == 1
    assert vehicles[0]["model"] == "RAV4"

