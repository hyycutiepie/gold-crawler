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
        if price_val is None: return 0.0
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
    except: print("Lỗi BTMH")

# 2. DOJI (Sử dụng selector chính xác hơn cho DOJI Hà Nội)
def crawl_doji():
    print("🚀 Đang cào DOJI...")
    target_url = "https://giavang.doji.vn/"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(target_url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # DOJI thường bọc dữ liệu trong các hàng tr
        rows = soup.find_all('tr')
        count = 0
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 3:
                name = " ".join(cols[0].get_text().split())
                # Tập trung vào SJC và các loại vàng phổ biến của DOJI
                if any(x in name.upper() for x in ["SJC", "DOJI", "NỮ TRANG 99.9"]):
                    buy = clean_price(cols[1].get_text())
                    sell = clean_price(cols[2].get_text())
                    if buy > 1000000:
                        save_gold("DOJI", name, buy, sell, target_url)
                        count += 1
        if count == 0: print("⚠️ DOJI: Không tìm thấy dữ liệu.")
    except: print("Lỗi DOJI")

# 3. PHÚ QUÝ
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

# 4. BẢO TÍN MINH CHÂU (Sửa dùng html.parser để không cần cài thêm lxml)
def crawl_btmc():
    print("🚀 Đang gọi API Bảo Tín Minh Châu (XML)...")
    api_url = "http://api.btmc.vn/api/BTMCAPI/getpricebtmc?key=3kd8ub1llcg9t45hnoh8hmn7t5kc2v"
    try:
        res = requests.get(api_url, timeout=20)
        # Sử dụng 'html.parser' thay vì 'xml' để tránh lỗi thiếu thư viện lxml
        soup = BeautifulSoup(res.content, 'html.parser')
        data_tags = soup.find_all('data') # html.parser tự viết thường các tag
        
        count = 0
        for tag in data_tags:
            row_idx = tag.get('row')
            name = tag.get(f'n_{row_idx}')
            buy = tag.get(f'pb_{row_idx}')
            sell = tag.get(f'ps_{row_idx}')
            
            if name and any(x in name for x in ["SJC", "Vàng Rồng Thăng Long", "Nhẫn Tròn"]):
                save_gold("BTMC", name, clean_price(buy), clean_price(sell), "https://btmc.vn")
                count += 1
        if count == 0: print("⚠️ BTMC: Không tìm thấy dữ liệu phù hợp.")
    except Exception as e:
        print(f"❌ Lỗi API BTMC: {e}")

if __name__ == "__main__":
    crawl_btmh()
    crawl_doji()
    crawl_phuquy()
    crawl_btmc()
