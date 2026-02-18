import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Kết nối Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def clean_price(price_str):
    """Chuyển đổi '85.200.000' -> 85.2"""
    try:
        # Xóa dấu chấm, dấu phẩy và khoảng trắng
        clean_str = price_str.replace('.', '').replace(',', '').strip()
        return float(clean_str) / 1000000
    except:
        return 0.0

def crawl_bao_tin_manh_hai():
    print("🚀 Đang cào dữ liệu từ Bảo Tín Mạnh Hải...")
    try:
        url_web = "https://baotinmanhhai.vn/gia-vang-hom-nay"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        response = requests.get(url_web, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm bảng giá - Thường nằm trong các thẻ tr của tbody
        rows = soup.select('table tr')
        print(f"🔍 Tìm thấy {len(rows)} dòng trong bảng.")

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                # Lọc lấy các loại vàng chính để tránh rác
                if any(x in name for x in ["SJC", "Kim Gia Bảo", "999.9"]):
                    buy = clean_price(cols[1].get_text(strip=True))
                    sell = clean_price(cols[2].get_text(strip=True))
                    
                    if buy > 0:
                        data = {
                            "gold_type": f"BTNH - {name}",
                            "buy_price": buy,
                            "sell_price": sell,
                            "source": "baotinmanhhai.vn"
                        }
                        
                        print(f"💾 Chuẩn bị gửi: {data}")
                        
                        # Gửi từng dòng để dễ bắt lỗi
                        result = supabase.table("gold_prices").upsert(data).execute()
                        print(f"✅ Thành công: {name}")

    except Exception as e:
        print(f"❌ Lỗi thực thi: {str(e)}")

if __name__ == "__main__":
    crawl_bao_tin_manh_hai()
