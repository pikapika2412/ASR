import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import time
import re
import random
from urllib.parse import urljoin

class DuyTanLibraryScraper:
    def __init__(self):
        self.base_url = "https://elib.duytan.edu.vn"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def extract_book_info(self, book_url):
        """Extract detailed information from a book page"""
        try:
            print(f"Đang trích xuất thông tin từ: {book_url}")
            response = self.session.get(book_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            book_info = {}
              # Extract book title - Simple method using HTML structure
            title_element = soup.find('li', class_='title')
            if title_element:
                book_info['title'] = title_element.get_text().strip()
            
            # Extract all text content for other metadata parsing
            page_text = soup.get_text()
            
            # Extract book cover image
            img_element = soup.find('img', src=re.compile(r'sach_anh'))
            if img_element:
                book_info['cover_image'] = urljoin(self.base_url, img_element['src'])
            
            # Extract author - Tác giả
            author_match = re.search(r'Tác giả:\s*([^\n\r]+)', page_text)
            if author_match:
                book_info['author'] = author_match.group(1).strip()
            
            # Extract publisher - Nhà xuất bản
            publisher_match = re.search(r'Nhà xuất bản:\s*([^\n\r]+)', page_text)
            if publisher_match:
                book_info['publisher'] = publisher_match.group(1).strip()
            
            # Extract publication year - Năm xuất bản
            year_match = re.search(r'Năm xuất bản:\s*(\d{4})', page_text)
            if year_match:
                book_info['publication_year'] = int(year_match.group(1))
            
            # Extract number of pages - Số trang
            pages_match = re.search(r'Số trang:\s*([^\n\r]+)', page_text)
            if pages_match:
                book_info['pages'] = pages_match.group(1).strip()
            
            # Extract dimensions - Kích thước
            dimensions_match = re.search(r'Kích thước:\s*([^\n\r]+)', page_text)
            if dimensions_match:
                book_info['dimensions'] = dimensions_match.group(1).strip()
            
            # Extract registration number - Số đăng ký cá biệt
            reg_number_match = re.search(r'Số đăng ký cá biệt:\s*([^\n\r]+)', page_text)
            if reg_number_match:
                book_info['registration_number'] = reg_number_match.group(1).strip()
            
            # Extract ISBN
            isbn_match = re.search(r'ISBN:\s*([^\n\r]+)', page_text)
            if isbn_match:
                book_info['isbn'] = isbn_match.group(1).strip()
            
            # Extract Dewey code - Mã Dewey
            dewey_match = re.search(r'Mã Dewey:\s*([^\n\r]+)', page_text)
            if dewey_match:
                book_info['dewey_code'] = dewey_match.group(1).strip()
            
            # Extract price - Đơn giá
            price_match = re.search(r'Đơn giá:\s*([^\n\r]+)', page_text)
            if price_match:
                book_info['price'] = price_match.group(1).strip()
            
            # Extract storage location - Vị trí lưu trữ
            location_match = re.search(r'Vị trí lưu trữ:\s*([^\n\r]+)', page_text)
            if location_match:
                book_info['storage_location'] = location_match.group(1).strip()
            
            # Extract language - Ngôn ngữ
            language_match = re.search(r'Ngôn ngữ:\s*([^\n\r]+)', page_text)
            if language_match:
                book_info['language'] = language_match.group(1).strip()
            
            # Extract document type - Loại tài liệu
            doc_type_match = re.search(r'Loại tài liệu:\s*([^\n\r]+)', page_text)
            if doc_type_match:
                book_info['document_type'] = doc_type_match.group(1).strip()
            
            # Extract availability - Đang rỗi/ Tổng sách
            availability_match = re.search(r'Đang rỗi/ Tổng sách:\s*([^\n\r]+)', page_text)
            if availability_match:
                book_info['availability'] = availability_match.group(1).strip()
            
            # Extract keywords - Từ khóa
            keywords_match = re.search(r'Từ khóa:\s*([^\n\r]+)', page_text)
            if keywords_match:
                book_info['keywords'] = keywords_match.group(1).strip()
            
            # Extract subject - Chủ đề
            subject_match = re.search(r'Chủ đề:\s*([^\n\r]+)', page_text)
            if subject_match:
                book_info['subject'] = subject_match.group(1).strip()
            
            # Extract department - Chuyên ngành
            department_match = re.search(r'Chuyên ngành:\s*([^\n\r]+)', page_text)
            if department_match:
                book_info['department'] = department_match.group(1).strip()
              # Extract summary - Tóm tắt
            summary_match = re.search(r'Tóm tắt:\s*(.*?)(?=\n\s*\n|\n\s*[A-Z]|$)', page_text, re.DOTALL)
            if summary_match:
                summary = summary_match.group(1).strip()
                summary = re.sub(r'\s+', ' ', summary)
                summary = summary.split('Bạn phải đăng nhập')[0].strip()
                if summary:
                    book_info['summary'] = summary
            
            # Add URL for reference
            book_info['url'] = book_url
            
            print(f"✓ Đã trích xuất thành công: {book_info.get('title', 'Không có tiêu đề')}")
            return book_info
            
        except Exception as e:
            print(f"✗ Lỗi khi trích xuất thông tin từ {book_url}: {str(e)}")
            return {}

    def get_random_books(self, num_books=36):
        """Get random book URLs from random pages in the library"""
        book_urls = []
        attempts = 0
        max_attempts = num_books * 3  # Try 3 times more than needed
        
        print(f"🔍 Bắt đầu thu thập {num_books} quyển sách ngẫu nhiên...")
        
        while len(book_urls) < num_books and attempts < max_attempts:
            # Generate random page number (limit to first 200 pages for efficiency)
            random_page = random.randint(1, 200)
            
            try:
                print(f"📖 Đang lấy trang ngẫu nhiên {random_page}... (Đã tìm được {len(book_urls)}/{num_books} sách)")
                
                # URL format: /Sach/Index/0/0/0/[page_number]
                if random_page == 1:
                    page_url = f"{self.base_url}/Sach/Index"
                else:
                    page_url = f"{self.base_url}/Sach/Index/0/0/0/{random_page}"
                
                response = self.session.get(page_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find book links
                book_links = soup.find_all('a', href=re.compile(r'/Sach/Detail/\d+'))
                
                if book_links:
                    # Randomly select some books from this page
                    random.shuffle(book_links)
                    books_needed = num_books - len(book_urls)
                    books_to_take = min(len(book_links), books_needed, 3)  # Take max 3 books per page
                    
                    for i in range(books_to_take):
                        book_url = urljoin(self.base_url, book_links[i]['href'])
                        if book_url not in book_urls:
                            book_urls.append(book_url)
                
                # Add delay to be respectful to the server
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"⚠️ Lỗi khi lấy trang {random_page}: {str(e)}")
            
            attempts += 1
        
        print(f"✅ Đã thu thập {len(book_urls)} URL sách ngẫu nhiên")
        return book_urls[:num_books]  # Ensure we don't exceed the requested number

    def scrape_multiple_books(self, book_urls):
        """Scrape multiple books from a list of URLs"""
        books_data = []
        
        print(f"🚀 Bắt đầu craw {len(book_urls)} quyển sách...")
        
        for i, url in enumerate(book_urls):
            print(f"\n📚 Đang craw sách {i+1}/{len(book_urls)}: {url}")
            
            book_info = self.extract_book_info(url)
            if book_info:
                books_data.append(book_info)
            else:
                print(f"❌ Không thể craw được sách từ {url}")
            
            # Add delay to be respectful to the server
            time.sleep(random.uniform(2, 4))
        
        return books_data

    def save_to_json(self, books_data, file_path="duytan_books.json"):
        """Save book data to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(books_data, f, ensure_ascii=False, indent=2)
        print(f"✓ Đã lưu {len(books_data)} sách vào {file_path}")
    
    def save_to_sqlite(self, books_data, db_path="duytan_books.db"):
        """Save book data to SQLite database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                publisher TEXT,
                publication_year INTEGER,
                pages TEXT,
                dimensions TEXT,
                registration_number TEXT,
                isbn TEXT,
                dewey_code TEXT,
                price TEXT,
                storage_location TEXT,
                language TEXT,
                document_type TEXT,
                availability TEXT,
                keywords TEXT,
                subject TEXT,
                department TEXT,
                summary TEXT,
                cover_image TEXT,
                url TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert data
        for book in books_data:
            cursor.execute('''
                INSERT INTO books (
                    title, author, publisher, publication_year, pages, dimensions,
                    registration_number, isbn, dewey_code, price, storage_location,
                    language, document_type, availability, keywords, subject,
                    department, summary, cover_image, url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                book.get('title', ''),
                book.get('author', ''),
                book.get('publisher', ''),
                book.get('publication_year', 0),
                book.get('pages', ''),
                book.get('dimensions', ''),
                book.get('registration_number', ''),
                book.get('isbn', ''),
                book.get('dewey_code', ''),
                book.get('price', ''),
                book.get('storage_location', ''),
                book.get('language', ''),
                book.get('document_type', ''),
                book.get('availability', ''),
                book.get('keywords', ''),
                book.get('subject', ''),
                book.get('department', ''),
                book.get('summary', ''),
                book.get('cover_image', ''),
                book.get('url', '')
            ))
        
        conn.commit()
        conn.close()
        print(f"✓ Đã lưu {len(books_data)} sách vào {db_path}")

def main():
    """Main function to crawl 36 random books"""
    scraper = DuyTanLibraryScraper()
    
    print("=== Bắt đầu craw 36 cuốn sách ngẫu nhiên từ thư viện Duy Tân ===")
    
    # Get random books
    random_book_urls = scraper.get_random_books(36)
    
    if not random_book_urls:
        print("❌ Không thể tìm được sách ngẫu nhiên")
        return False
    
    print(f"📋 Danh sách {len(random_book_urls)} URL sách ngẫu nhiên:")
    for i, url in enumerate(random_book_urls[:5]):  # Show first 5 URLs
        print(f"  {i+1}. {url}")
    if len(random_book_urls) > 5:
        print(f"  ... và {len(random_book_urls) - 5} URL khác")
    
    # Scrape books data
    books_data = scraper.scrape_multiple_books(random_book_urls)
    
    if books_data:
        print(f"\n✅ Đã craw được {len(books_data)} cuốn sách thành công!")
        
        # Lưu vào file
        scraper.save_to_json(books_data, "random_36_books.json")
        scraper.save_to_sqlite(books_data, "random_36_books.db")
        
        # Hiển thị thống kê
        print(f"\n📊 Thống kê:")
        print(f"   - Tổng số sách: {len(books_data)}")
        
        # Count by language
        languages = {}
        for book in books_data:
            lang = book.get('language', 'Không rõ')
            languages[lang] = languages.get(lang, 0) + 1
        
        print("   - Phân bố ngôn ngữ:")
        for lang, count in languages.items():
            print(f"     • {lang}: {count} sách")
        
        # Show sample books
        print(f"\n📚 Mẫu sách (3 cuốn đầu):")
        for i, book in enumerate(books_data[:3]):
            print(f"   {i+1}. {book.get('title', 'Không có tiêu đề')}")
            print(f"      Tác giả: {book.get('author', 'N/A')}")
            print(f"      Năm: {book.get('publication_year', 'N/A')}")
            print(f"      Ngôn ngữ: {book.get('language', 'N/A')}")
        
        print(f"\n🎉 Hoàn thành! Dữ liệu đã được lưu vào:")
        print("   - random_36_books.json")
        print("   - random_36_books.db")
        
        return True
    else:
        print("❌ Không craw được sách nào")
        return False

if __name__ == "__main__":
    main()
