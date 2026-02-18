import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Kết nối Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def clean_price(price_str):
    """Chuyển đổi các định dạng giá về con số nguyên"""
    try:
        if not price_str: return 0.0
        clean_str = price_str.replace('.', '').replace(',', '').strip()
        return float(clean_str)
    except:
        return 0.0

def save_gold(source_code, gold_type, buy, sell, web_url):
    """Ghi đè dữ liệu nếu trùng nguồn và loại vàng"""
    data = {
        "source_code": source_code,
        "gold_type": gold_type,
        "buy_price": buy,
        "sell_price": sell,
        "source_url": web_url,
        "updated_at": "now()"
    }
    try:
        # on_conflict giúp xử lý lỗi duplicate key bằng cách ghi đè (update)
        supabase.table("gold_prices").upsert(data, on_conflict="source_code,gold_type").execute()
        print(f"✅ [{source_code}] {gold_type}: {buy} - {sell}")
    except Exception as e:
        print(f"❌ Lỗi lưu {source_code} ({gold_type}): {e}")

# 1. BẢO TÍN MẠNH HẢI
def crawl_btmh():
    print("🚀 Đang cào Bảo Tín Mạnh Hải...")
    target_url = "https://baotinmanhhai.vn/gia-vang-hom-nay"
    try:
        res = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.select('table tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                if any(x in name for x in ["SJC", "Kim Gia Bảo", "Nhẫn Tròn"]):
                    save_gold("BTMH", name, clean_price(cols[1].text), clean_price(cols[2].text), target_url)
    except Exception as e: print(f"Lỗi BTMH: {e}")

# 2. DOJI
def crawl_doji():
    print("🚀 Đang cào DOJI...")
    target_url = "https://giavang.doji.vn/"
    try:
        res = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.select('.table-price tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                if "SJC" in name or "AVPL" in name:
                    save_gold("DOJI", name, clean_price(cols[1].text), clean_price(cols[2].text), target_url)
    except Exception as e: print(f"Lỗi DOJI: {e}")

# 3. PHÚ QUÝ
def crawl_phuquy():
    print("🚀 Đang cào Phú Quý...")
    target_url = "https://phuquygroup.vn/"
    try:
        res = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Phú Quý thường dùng bảng có class table
        rows = soup.select('table tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                if any(x in name for x in ["SJC", "Phú Quý"]):
                    save_gold("PHUQUY", name, clean_price(cols[1].text), clean_price(cols[2].text), target_url)
    except Exception as e: print(f"Lỗi Phú Quý: {e}")

# 4. BẢO TÍN MINH CHÂU
def crawl_btmc():
    print("🚀 Đang cào Bảo Tín Minh Châu...")
    target_url = "https://btmc.vn/gia-vang-hom-nay"
    try:
        res = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        # BTMC dùng các hàng có class cụ thể hoặc trong bảng giá
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                if any(x in name for x in ["SJC", "Vàng Rồng Thăng Long", "BTMC"]):
                    # BTMC đôi khi để giá trong thẻ span hoặc b
                    buy = clean_price(cols[1].get_text(strip=True))
                    sell = clean_price(cols[2].get_text(strip=True))
                    if buy > 0:
                        save_gold("BTMC", name, buy, sell, target_url)
    except Exception as e: print(f"Lỗi BTMC: {e}")

if __name__ == "__main__":
    crawl_btmh()
    crawl_doji()
    crawl_phuquy()
    crawl_btmc()
