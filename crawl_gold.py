import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Kết nối Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def clean_price(price_str):
    try:
        if not price_str: return 0.0
        # Xóa dấu chấm, dấu phẩy, khoảng trắng
        clean_str = str(price_str).replace('.', '').replace(',', '').strip()
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
    except Exception as e: print(f"Lỗi BTMH: {e}")

# 2. DOJI (Sửa đổi để bóc tách bảng kỹ hơn)
def crawl_doji():
    print("🚀 Đang cào DOJI...")
    target_url = "https://giavang.doji.vn/"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(target_url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Tìm các dòng td có chứa text SJC hoặc DOJI
        rows = soup.find_all('tr')
        count = 0
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                # Lấy SJC Hà Nội và các loại chính
                if "SJC" in name.upper() or "DOJI" in name.upper():
                    buy = clean_price(cols[1].get_text(strip=True))
                    sell = clean_price(cols[2].get_text(strip=True))
                    if buy > 1000000: # Lọc bỏ các dòng rác không phải giá tiền
                        save_gold("DOJI", name, buy, sell, target_url)
                        count += 1
        if count == 0: print("⚠️ DOJI: Không tìm thấy dữ liệu.")
    except Exception as e: print(f"❌ Lỗi DOJI: {e}")

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
    except Exception as e: print(f"Lỗi Phú Quý: {e}")

# 4. BẢO TÍN MINH CHÂU (Dùng API chính chủ)
def crawl_btmc():
    print("🚀 Đang gọi API Bảo Tín Minh Châu...")
    api_url = "http://api.btmc.vn/api/BTMCAPI/getpricebtmc?key=3kd8ub1llcg9t45hnoh8hmn7t5kc2v"
    try:
        res = requests.get(api_url, timeout=20)
        data = res.json() # API trả về JSON
        
        # Cấu trúc API BTMC thường nằm trong data hoặc list
        # Giả định cấu trúc dựa trên API chuẩn của họ:
        for item in data:
            name = item.get('row_name', '')
            buy = clean_price(item.get('buy', 0))
            sell = clean_price(item.get('sell', 0))
            
            if any(x in name for x in ["SJC", "Vàng Rồng Thăng Long"]):
                save_gold("BTMC", name, buy, sell, "https://btmc.vn")
                
    except Exception as e:
        print(f"❌ Lỗi API BTMC: {e}")

if __name__ == "__main__":
    crawl_btmh()
    crawl_doji()
    crawl_phuquy()
    crawl_btmc()
