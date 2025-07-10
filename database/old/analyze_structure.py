import requests
from bs4 import BeautifulSoup
import re

def analyze_page_structure():
    url = "https://elib.duytan.edu.vn/Sach/Detail/92799"  # Elon Musk book
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tìm title chính xác bằng cách phân tích structure
        print("=== ANALYZING PAGE STRUCTURE ===")
        
        # Method: Tìm text đầu tiên sau ảnh và trước "Tác giả:"
        page_text = soup.get_text()
        
        # Tìm pattern: sau ".jpg" và trước "Tác giả:"
        pattern = r'\.jpg.*?\n\s*([^\n]+?)(?=\s*Tác giả:)'
        match = re.search(pattern, page_text, re.DOTALL)
        
        if match:
            title = match.group(1).strip()
            # Loại bỏ các ký tự không cần thiết
            title = re.sub(r'^\s*\n*', '', title)
            title = re.sub(r'\n.*$', '', title)  # Chỉ lấy dòng đầu
            title = title.strip()
            
            print(f"FOUND TITLE: '{title}'")
            
            # Kiểm tra xem có phải là title thật không
            if (title and len(title) > 3 and 
                not title.startswith('Tác giả:') and
                not title.startswith('Nhà xuất bản:') and
                'Trang chủ' not in title and
                'Trở về' not in title):
                print("✓ This looks like a valid title!")
                return title
            else:
                print("✗ This doesn't look like a valid title")
        else:
            print("No title found with this pattern")
            
        # Backup method: Tìm trong specific div
        content_area = soup.find('div', class_='row')
        if content_area:
            # Tìm text đầu tiên không phải metadata
            text_lines = content_area.get_text().split('\n')
            for i, line in enumerate(text_lines):
                line = line.strip()
                if (line and len(line) > 10 and 
                    not line.startswith('Tác giả:') and
                    not line.startswith('Nhà xuất bản:') and
                    not line.startswith('CSDL SÁCH') and
                    not line.startswith('Trở về') and
                    not line.startswith('Hiển thị') and
                    'upload/sach_anh' not in line and
                    'jpg' not in line):
                    print(f"Potential title from div: '{line}'")
                    return line
                    
        return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    title = analyze_page_structure()
    if title:
        print(f"\nFINAL EXTRACTED TITLE: {title}")
    else:
        print("\nFailed to extract title")
