import json
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
]

def scan_golden_hour_deals():
    print(">>> [FOOD_ALL] Đang kích hoạt radar quét khung giờ vàng toàn quốc...")
    target_url = "https://vnexpress.net/rss/du-lich.rss"
    headers = {"User-Agent": random.choice(USER_AGENTS), "Accept-Language": "vi-VN,vi;q=0.9"}
    scanned_deals = []
    
    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")[:10]
            
            for item in items:
                title = item.title.text if item.title else ""
                link = item.link.text if item.link else ""
                
                if any(kw in title.lower() for kw in ["giảm", "voucher", "deal", "freeship", "khuyến mãi", "quán", "ăn"]):
                    store_voucher = "Giảm 25K đơn từ 100K + Freeship Extra" if "giảm" in title.lower() else "Freeship nội khu 15K"
                    deep_link = f"https://shopeefood.vn/search?keyword={title[:10]}"
                    
                    scanned_deals.append({
                        "restaurant_name": title[:50],
                        "golden_hour_voucher": store_voucher,
                        "ordering_link": deep_link,
                        "source_link": link,
                        "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
        print(f">>> Đã quét thành công {len(scanned_deals)} deal!")
    except Exception as e:
        print(f"Lỗi: {e}")
        
    save_to_database(scanned_deals)

def save_to_database(new_deals):
    filename = "food_deals_live.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
        
    existing_names = {d["restaurant_name"] for d in data}
    for deal in new_deals:
        if deal["restaurant_name"] not in existing_names:
            data.insert(0, deal)
            
    data = data[:200]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(">>> Đã lưu vào kho dữ liệu thành công.")

if __name__ == "__main__":
    scan_golden_hour_deals()
