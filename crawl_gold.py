import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Kết nối Supabase bằng "Chìa khóa" đã tạo ở Bước 2
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def crawl_and_save(name, url_web, select_css, source_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url_web, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ở đây bạn sẽ cần tìm đúng thẻ HTML chứa giá
        # Ví dụ tạm thời để bạn thấy nó hoạt động:
        buy = 85.0  
        sell = 87.0
        
        data = {
            "gold_type": name,
            "buy_price": buy,
            "sell_price": sell,
            "source": source_name
        }
        # Lưu vào Supabase
        supabase.table("gold_prices").upsert(data, on_conflict="gold_type").execute()
        print(f"✅ Đã cập nhật {name}")
    except Exception as e:
        print(f"❌ Lỗi {name}: {e}")

if __name__ == "__main__":
    # Bạn muốn cào bao nhiêu trang thì cứ thêm dòng ở đây
    crawl_and_save("BTMH", "https://baotinmanhhai.vn/", "the-html", "BTMH")
    
