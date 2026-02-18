import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Kết nối Supabase bằng biến môi trường
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def clean_price(price_str):
    """Chuyển đổi '17.800.000' -> 17800000.0 (Giữ nguyên con số)"""
    try:
        # Xóa dấu chấm, dấu phẩy và khoảng trắng
        clean_str = price_str.replace('.', '').replace(',', '').strip()
        return float(clean_str)
    except:
        return 0.0

def crawl_bao_tin_manh_hai():
    print("🚀 Đang cào dữ liệu từ Bảo Tín Mạnh Hải...")
    try:
        url_web = "https://baotinmanhhai.vn/gia-vang-hom-nay"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url_web, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm các dòng trong bảng giá
        rows = soup.select('table tr')
        print(f"🔍 Tìm thấy {len(rows)} dòng trong bảng.")

        count = 0
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                
                # Lọc lấy các loại vàng chính
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
                        
                        # Gửi dữ liệu lên Supabase
                        supabase.table("gold_prices").upsert(data).execute()
                        print(f"✅ Đã lưu: {name} | Mua: {buy} - Bán: {sell}")
                        count += 1
        
        if count == 0:
            print("⚠️ Không tìm thấy loại vàng nào phù hợp để lưu.")

    except Exception as e:
        print(f"❌ Lỗi thực thi: {str(e)}")

if __name__ == "__main__":
    crawl_bao_tin_manh_hai()
