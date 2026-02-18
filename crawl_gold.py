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
        # Lấy tất cả chữ số
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
        supabase.table("gold_prices").upsert(data, on_conflict="source_code,gold_type").execute()
        print(f"✅ [{source_code}] {gold_type}: {buy} - {sell}")
    except Exception as e:
        print(f"❌ Lỗi lưu {source_code}: {e}")

# HÀM TỔNG HỢP CÀO TỪ WEBGIA (Lấy DOJI, BTMC, SJC, PHÚ QUÝ)
def crawl_webgia():
    print("🚀 Đang cào dữ liệu tổng hợp từ WebGia...")
    # Trang này tổng hợp giá vàng rất sạch
    target_url = "https://webgia.com/gia-vang/sjc/" 
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(target_url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Tìm tất cả các bảng giá
        tables = soup.find_all('table', class_='table-price')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    name_raw = cols[0].get_text(strip=True)
                    buy = clean_price(cols[1].get_text(strip=True))
                    sell = clean_price(cols[2].get_text(strip=True))
                    
                    # Phân loại dữ liệu dựa trên tên hàng
                    # DOJI
                    if "DOJI" in name_raw.upper():
                        save_gold("DOJI", name_raw, buy, sell, target_url)
                    
                    # BẢO TÍN MINH CHÂU
                    elif "MINH CHÂU" in name_raw.upper() or "BTMC" in name_raw.upper():
                        save_gold("BTMC", name_raw, buy, sell, target_url)
                        
                    # PHÚ QUÝ
                    elif "PHÚ QUÝ" in name_raw.upper():
                        save_gold("PHUQUY", name_raw, buy, sell, target_url)
                        
    except Exception as e:
        print(f"❌ Lỗi crawl WebGia: {e}")

# 1. BẢO TÍN MẠNH HẢI (Trang này vẫn cào trực tiếp được vì cấu trúc ổn)
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

if __name__ == "__main__":
    # Ưu tiên cào WebGia để lấy DOJI, BTMC, PHUQUY
    crawl_webgia()
    # Mạnh Hải cào riêng
    crawl_btmh()
