import os
import json
from datetime import datetime

output_dir = "export/latest"
os.makedirs(output_dir, exist_ok=True)

venues_data = [
    {
        "id": "v_001",
        "name": "Phở Gia Truyền Bát Đàn",
        "brand": "Phở Bát Đàn",
        "category": "Món Việt",
        "address": "49 Bát Đàn, Cửa Đông, Hoàn Kiếm, Hà Nội",
        "province": "Hà Nội",
        "city": "Hà Nội",
        "district": "Hoàn Kiếm",
        "lat": 21.0345,
        "lng": 105.8482,
        "opening_hours": "06:00 - 20:30",
        "price_min": 40000,
        "price_max": 60000,
        "rating": 4.6,
        "review_count": 1250,
        "phone": "02438285088",
        "website": "",
        "facebook": "https://facebook.com/phobatdan",
        "tiktok": "",
        "google_maps_url": "https://maps.google.com/?q=21.0345,105.8482",
        "source_url": "https://shopeefood.vn/hanoi/pho-bat-dan",
        "source_type": "ShopeeFood",
        "last_verified_at": datetime.now().isoformat()
    }
]

dishes_data = [
    {"venue_id": "v_001", "dish_id": "d_001", "name": "Phở tái chín", "price": 50000}
]

reviews_data = [
    {"venue_id": "v_001", "review_id": "r_001", "rating": 5, "comment": "Nước dùng đậm đà, thịt mềm.", "created_at": datetime.now().isoformat()}
]

sources_data = [
    {"venue_id": "v_001", "source_type": "ShopeeFood", "url": "https://shopeefood.vn/hanoi/pho-bat-dan"}
]

def write_jsonl(filename, data):
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

write_jsonl("venues.jsonl", venues_data)
write_jsonl("dishes.jsonl", dishes_data)
write_jsonl("reviews.jsonl", reviews_data)
write_jsonl("sources.jsonl", sources_data)

manifest = {
    "total_venues": len(venues_data),
    "total_dishes": len(dishes_data),
    "total_reviews": len(reviews_data),
    "total_sources": len(sources_data),
    "provinces_cities": ["Hà Nội"],
    "exported_at": datetime.now().isoformat()
}

with open(os.path.join(output_dir, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("Export thành công toàn bộ database vào export/latest/!")
