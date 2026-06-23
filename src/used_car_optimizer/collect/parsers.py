from __future__ import annotations

import json
import re
from html import unescape


JSON_LD_PATTERN = re.compile(
    r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)


def extract_json_ld_blocks(html: str) -> list[dict[str, object]]:
    blocks: list[dict[str, object]] = []
    for match in JSON_LD_PATTERN.findall(html):
        candidate = unescape(match).strip()
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue

        if isinstance(parsed, list):
            blocks.extend(item for item in parsed if isinstance(item, dict))
        elif isinstance(parsed, dict):
            blocks.append(parsed)
    return blocks


def flatten_vehicle_items(blocks: list[dict[str, object]]) -> list[dict[str, object]]:
    vehicles: list[dict[str, object]] = []
    queue = list(blocks)

    while queue:
        item = queue.pop(0)
        item_type = str(item.get("@type", ""))
        normalized_type = item_type.lower()

        if normalized_type in {"car", "vehicle", "product"}:
            vehicles.append(item)

        for value in item.values():
            if isinstance(value, dict):
                queue.append(value)
            elif isinstance(value, list):
                queue.extend(entry for entry in value if isinstance(entry, dict))

    return vehicles


def first_text(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        for item in value:
            text = first_text(item)
            if text:
                return text
    if isinstance(value, dict):
        for key in ("name", "value", "@value"):
            text = first_text(value.get(key))
            if text:
                return text
    return ""
