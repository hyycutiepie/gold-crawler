import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Kết nối Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def clean_price(price_str):
    """Biến các định dạng '17.800.000' hoặc '17,800' thành 17800000"""
    try:
        clean_str = price_str.replace('.', '').replace(',', '').strip()
        return float(clean_str)
    except:
        return 0.0

def save_gold(source_code, gold_type, buy, sell, web_url):
    data = {
        "source_code": source_code,
        "gold_type": gold_type,
        "buy_price": buy,
        "sell_price": sell,
        "source_url": web_url,
        "updated_at": "now()"
    }
    try:
        supabase.table("gold_prices").upsert(data).execute()
        print(f"✅ [{source_code}] {gold_type}: {buy} - {sell}")
    except Exception as e:
        print(f"❌ Lỗi lưu {source_code}: {e}")

# 1. BẢO TÍN MẠNH HẢI
def crawl_btmh():
    target_url = "https://baotinmanhhai.vn/gia-vang-hom-nay"
    try:
        res = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.select('table tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                if any(x in name for x in ["SJC", "Kim Gia Bảo"]):
                    buy = clean_price(cols[1].get_text(strip=True))
                    sell = clean_price(cols[2].get_text(strip=True))
                    if buy > 0: save_gold("BTMH", name, buy, sell, target_url)
    except Exception as e: print(f"Lỗi BTMH: {e}")

# 2. BẢO TÍN MINH CHÂU (Dùng API nội bộ của họ)
def crawl_btmc():
    target_url = "https://btmc.vn/gia-vang-hom-nay"
    try:
        # BTMC thường chặn bot, ta dùng headers giả lập sâu hơn
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://btmc.vn/api/get-gold-price", headers=headers, timeout=20)
        # Nếu API trả về JSON, ta xử lý JSON, nếu không ta cào HTML
        # Ở đây tôi viết dạng cào bảng phổ biến của BTMC:
        res = requests.get(target_url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.select('.table-price tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                if "Vàng Rồng Thăng Long" in name or "SJC" in name:
                    buy = clean_price(cols[1].get_text(strip=True))
                    sell = clean_price(cols[2].get_text(strip=True))
                    save_gold("BTMC", name, buy, sell, target_url)
    except Exception as e: print(f"Lỗi BTMC: {e}")

# 3. PHÚ QUÝ
def crawl_phu_quy():
    target_url = "https://phuquygroup.vn/"
    try:
        res = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Phú Quý thường để giá ngay trang chủ trong bảng
        rows = soup.select('.table-bordered tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                if "SJC" in name or "Phú Quý" in name:
                    buy = clean_price(cols[1].get_text(strip=True))
                    sell = clean_price(cols[2].get_text(strip=True))
                    save_gold("PHUQUY", name, buy, sell, target_url)
    except Exception as e: print(f"Lỗi Phú Quý: {e}")

# 4. DOJI
def crawl_doji():
    target_url = "https://giavang.doji.vn/"
    try:
        res = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        # DOJI có cấu trúc bảng giá theo khu vực
        rows = soup.select('.table-price tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                if "SJC" in name:
                    buy = clean_price(cols[1].get_text(strip=True))
                    sell = clean_price(cols[2].get_text(strip=True))
                    save_gold("DOJI", name, buy, sell, target_url)
    except Exception as e: print(f"Lỗi DOJI: {e}")

if __name__ == "__main__":
    crawl_btmh()
    crawl_btmc()
    crawl_phu_quy()
    crawl_doji()
