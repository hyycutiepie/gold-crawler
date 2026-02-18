import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Kết nối
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def clean_price(price_str):
    """Biến '17.800.000' thành 17800000"""
    try:
        return float(price_str.replace('.', '').replace(',', '').strip())
    except:
        return 0.0

def crawl_bao_tin_manh_hai():
    print("🚀 Đang cào dữ liệu từ Bảo Tín Mạnh Hải...")
    try:
        url_web = "https://baotinmanhhai.vn/gia-vang-hom-nay"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url_web, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rows = soup.select('table tr')
        print(f"🔍 Tìm thấy {len(rows)} dòng.")

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
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
                        # Gửi và bắt lỗi chi tiết từng dòng
                        try:
                            supabase.table("gold_prices").upsert(data).execute()
                            print(f"✅ Đã lưu: {name} ({buy})")
                        except Exception as e_inner:
                            print(f"❌ Lỗi khi gửi dòng {name}: {e_inner}")

    except Exception as e:
        print(f"❌ Lỗi thực thi: {str(e)}")

if __name__ == "__main__":
    crawl_bao_tin_manh_hai()
