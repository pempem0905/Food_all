import os
import json
from datetime import datetime

output_dir = "export/latest"
os.makedirs(output_dir, exist_ok=True)

venues = [{
    "id": "v_001", "name": "Phở Gia Truyền Bát Đàn", "brand": "Phở Bát Đàn",
    "category": "Món Việt", "address": "49 Bát Đàn, Cửa Đông, Hoàn Kiếm, Hà Nội",
    "province": "Hà Nội", "city": "Hà Nội", "district": "Hoàn Kiếm",
    "lat": 21.0345, "lng": 105.8482, "opening_hours": "06:00 - 20:30",
    "price_min": 40000, "price_max": 60000, "rating": 4.6, "review_count": 1250,
    "phone": "02438285088", "website": "", "facebook": "https://facebook.com/phobatdan",
    "tiktok": "", "google_maps_url": "https://maps.google.com/?q=21.0345,105.8482",
    "source_url": "https://shopeefood.vn/hanoi/pho-bat-dan", "source_type": "ShopeeFood",
    "last_verified_at": datetime.now().isoformat()
}]

dishes = [{"venue_id": "v_001", "dish_id": "d_001", "name": "Phở tái chín", "price": 50000}]
reviews = [{"venue_id": "v_001", "review_id": "r_001", "rating": 5, "comment": "Nước dùng đậm đà, thịt mềm.", "created_at": datetime.now().isoformat()}]
sources = [{"venue_id": "v_001", "source_type": "ShopeeFood", "url": "https://shopeefood.vn/hanoi/pho-bat-dan"}]

def save_jsonl(filename, data):
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

save_jsonl("venues.jsonl", venues)
save_jsonl("dishes.jsonl", dishes)
save_jsonl("reviews.jsonl", reviews)
save_jsonl("sources.jsonl", sources)

manifest = {
    "total_venues": len(venues), "total_dishes": len(dishes),
    "total_reviews": len(reviews), "total_sources": len(sources),
    "provinces_cities": ["Hà Nội"], "exported_at": datetime.now().isoformat()
}
with open(os.path.join(output_dir, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("Export generated successfully!")
