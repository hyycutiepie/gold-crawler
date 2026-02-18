import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Kết nối (Nhớ kiểm tra URL trên GitHub Secret phải có đuôi .supabase.co)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def clean_price(price_str):
    """Xử lý giá: '17.800.000' -> 17800000"""
    try:
        return float(price_str.replace('.', '').replace(',', '').strip())
    except:
        return 0.0

def save_gold(source_code, gold_type, buy, sell, web_url):
    """Lệnh upsert sẽ tự động ghi đè nếu trùng source_code và gold_type"""
    data = {
        "source_code": source_code,
        "gold_type": gold_type,
        "buy_price": buy,
        "sell_price": sell,
        "source_url": web_url,
        "updated_at": "now()" # Cập nhật lại thời gian mới nhất
    }
    try:
        supabase.table("gold_prices").upsert(data).execute()
        print(f"✅ [{source_code}] Đã cập nhật giá mới nhất cho: {gold_type}")
    except Exception as e:
        print(f"❌ Lỗi lưu dữ liệu: {e}")

def crawl_btmh():
    print("🚀 Đang lấy giá mới nhất từ Bảo Tín Mạnh Hải...")
    target_url = "https://baotinmanhhai.vn/gia-vang-hom-nay"
    try:
        res = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.select('table tr')
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                # Chỉ lấy các loại vàng bạn cần
                if any(x in name for x in ["SJC", "Kim Gia Bảo", "999.9"]):
                    buy = clean_price(cols[1].get_text(strip=True))
                    sell = clean_price(cols[2].get_text(strip=True))
                    if buy > 0:
                        save_gold("BTMH", name, buy, sell, target_url)
    except Exception as e:
        print(f"❌ Lỗi cào web BTMH: {e}")

if __name__ == "__main__":
    crawl_btmh()
