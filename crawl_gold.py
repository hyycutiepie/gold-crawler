import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Kết nối Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def crawl_bao_tin_manh_hai():
    print("🚀 Đang cào dữ liệu từ Bảo Tín Mạnh Hải...")
    try:
        url_web = "https://baotinmanhhai.vn/gia-vang-hom-nay"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        response = requests.get(url_web, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm tất cả các dòng trong bảng giá vàng
        # Thông thường web này để giá trong các thẻ <tr> của bảng
        rows = soup.find_all('tr')
        
        results = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                name = cols[0].text.strip()
                # Chỉ lấy những loại vàng phổ biến
                if "SJC" in name or "Kim Gia Bảo" in name or "999.9" in name:
                    # Chuyển đổi giá từ chuỗi "85.000" thành số 85.0
                    try:
                        buy = float(cols[1].text.strip().replace('.', '').replace(',', '')) / 1000000
                        sell = float(cols[2].text.strip().replace('.', '').replace(',', '')) / 1000000
                        
                        data = {
                            "gold_type": f"BTNH - {name}",
                            "buy_price": buy,
                            "sell_price": sell,
                            "source": "baotinmanhhai.vn"
                        }
                        results.append(data)
                    except:
                        continue

        if results:
            for item in results:
                supabase.table("gold_prices").upsert(item, on_conflict="gold_type").execute()
                print(f"✅ Cập nhật: {item['gold_type']}")
        else:
            print("⚠️ Không tìm thấy bảng giá phù hợp.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    crawl_bao_tin_manh_hai()
