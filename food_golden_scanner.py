import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
]

SOURCES = [
    {
        "name": "vnexpress_du_lich_rss",
        "url": "https://vnexpress.net/rss/du-lich.rss",
        "type": "rss",
    }
]

PROMO_KEYWORDS = (
    "giảm", "voucher", "deal", "freeship", "khuyến mãi", "ưu đãi", "sale",
    "mua 1 tặng 1", "tặng", "combo", "đồng giá"
)
FOOD_KEYWORDS = (
    "ăn", "quán", "nhà hàng", "cafe", "cà phê", "trà sữa", "buffet", "food",
    "bánh", "phở", "bún", "cơm", "lẩu", "nướng"
)

OUTPUT = Path("food_deals_live.json")
HEALTH = Path("food_scan_health.json")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def record_id(source_url: str, title: str) -> str:
    return hashlib.sha256(f"{source_url}|{title}".encode("utf-8")).hexdigest()[:20]


def fetch_rss(source):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.5",
    }
    response = requests.get(source["url"], headers=headers, timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "xml")
    records = []
    for item in soup.find_all("item")[:100]:
        title = item.title.text.strip() if item.title else ""
        link = item.link.text.strip() if item.link else ""
        lowered = title.lower()
        has_promo = any(k in lowered for k in PROMO_KEYWORDS)
        has_food = any(k in lowered for k in FOOD_KEYWORDS)
        if not (has_promo and has_food):
            continue
        records.append({
            "id": record_id(source["url"], title),
            "title": title,
            "source_name": source["name"],
            "source_link": link,
            "source_feed": source["url"],
            "evidence_type": "source_title",
            "verified": False,
            "voucher_code": None,
            "discount_text": None,
            "ordering_link": None,
            "discovered_at": utc_now(),
        })
    return records


def load_existing():
    try:
        data = json.loads(OUTPUT.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_records(new_records):
    existing = load_existing()
    by_id = {row.get("id"): row for row in existing if row.get("id")}
    for row in new_records:
        by_id[row["id"]] = row
    merged = sorted(by_id.values(), key=lambda r: r.get("discovered_at", ""), reverse=True)[:5000]
    OUTPUT.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(merged)


def main():
    discovered = []
    errors = []
    for source in SOURCES:
        try:
            discovered.extend(fetch_rss(source))
        except Exception as exc:
            errors.append({"source": source["name"], "error": str(exc)[:500]})

    total = save_records(discovered)
    health = {
        "ok": len(errors) == 0,
        "checked_at": utc_now(),
        "sources_total": len(SOURCES),
        "sources_failed": len(errors),
        "new_candidates_this_run": len(discovered),
        "stored_candidates_total": total,
        "errors": errors,
        "data_policy": "no_fabricated_voucher_or_discount_values",
    }
    HEALTH.write_text(json.dumps(health, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(health, ensure_ascii=False))
    if errors and not discovered:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
