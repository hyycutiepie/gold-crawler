import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Kết nối Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def clean_price(price_val):
    try:
        if not price_val: return 0.0
        # Chỉ giữ lại các con số
        clean_str = "".join(filter(str.isdigit, str(price_val)))
        return float(clean_str) if clean_str else 0.0
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
        # Sử dụng on_conflict để ghi đè dữ liệu cũ, tránh lỗi Duplicate Key
        supabase.table("gold_prices").upsert(data, on_conflict="source_code,gold_type").execute()
        print(f"✅ [{source_code}] {gold_type}: {buy} - {sell}")
    except Exception as e:
        print(f"❌ Lỗi lưu {source_code}: {e}")

# Hàm dùng chung để cào từ WebGia
def crawl_from_webgia(source_code, target_url):
    print(f"🚀 Đang cào {source_code} từ WebGia...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(target_url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Tìm bảng giá
        table = soup.find('table', class_='table-price')
        if not table:
            # Nếu không thấy class table-price, thử tìm bảng bất kỳ
            table = soup.find('table')
            
        rows = table.find_all('tr')
        count = 0
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                # Chỉ lấy các loại vàng chính (SJC, Nhẫn, Rồng Thăng Long...)
                if any(x in name.upper() for x in ["SJC", "NHẪN", "RỒNG THĂNG LONG", "DOJI", "PNJ"]):
                    buy = clean_price(cols[1].get_text(strip=True))
                    sell = clean_price(cols[2].get_text(strip=True))
                    if buy > 100000:
                        save_gold(source_code, name, buy, sell, target_url)
                        count += 1
        if count == 0: print(f"⚠️ {source_code}: Không tìm thấy dữ liệu.")
    except Exception as e:
        print(f"❌ Lỗi {source_code}: {e}")

# 1. BẢO TÍN MẠNH HẢI (Vẫn cào trực tiếp vì web này rất nhanh và dễ)
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
    except: print("Lỗi BTMH")

# 2. PHÚ QUÝ (Vẫn cào trực tiếp được)
def crawl_phuquy():
    print("🚀 Đang cào Phú Quý...")
    target_url = "https://phuquygroup.vn/"
    try:
        res = requests.get(target_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.select('table tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                if any(x in name for x in ["SJC", "Phú Quý"]):
                    save_gold("PHUQUY", name, clean_price(cols[1].text), clean_price(cols[2].text), target_url)
    except: print("Lỗi Phú Quý")

if __name__ == "__main__":
    # Cào DOJI từ WebGia
    crawl_from_webgia("DOJI", "https://webgia.com/gia-vang/doji/")
    
    # Cào Bảo Tín Minh Châu từ WebGia
    crawl_from_webgia("BTMC", "https://webgia.com/gia-vang/bao-tin-minh-chau/")
    
    # Cào 2 nguồn còn lại trực tiếp
    crawl_btmh()
    crawl_phuquy()
