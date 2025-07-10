#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import os
from datetime import datetime

class CSVToDatabase:
    def __init__(self, db_path="duytan_books.db"):
        self.db_path = db_path
        
    def create_books_table(self):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
        
        conn.commit()
        conn.close()
        print(f"✓ Đã tạo bảng books trong {self.db_path}")
    
    def csv_to_db(self, csv_path):
        """Chuyển dữ liệu từ CSV sang SQLite database"""
        
        # Kiểm tra file CSV có tồn tại không
        if not os.path.exists(csv_path):
            print(f"❌ File CSV không tồn tại: {csv_path}")
            return False
        
        try:
            # Đọc file CSV
            print(f"📖 Đang đọc file CSV: {csv_path}")
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            print(f"✓ Đã đọc {len(df)} dòng dữ liệu từ CSV")
            print(f"✓ Các cột trong CSV: {list(df.columns)}")
            
            # Tạo bảng database
            self.create_books_table()
            
            # Kết nối database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Xóa dữ liệu cũ nếu có
            cursor.execute('DELETE FROM books')
            print("✓ Đã xóa dữ liệu cũ trong database")
            
            # Chèn dữ liệu mới
            success_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Xử lý publication_year - chuyển thành integer
                    pub_year = row.get('publication_year', 0)
                    if pd.isna(pub_year) or pub_year == '':
                        pub_year = 0
                    else:
                        try:
                            pub_year = int(float(pub_year))
                        except (ValueError, TypeError):
                            pub_year = 0
                    
                    # Chèn dữ liệu
                    cursor.execute('''
                        INSERT INTO books (
                            title, author, publisher, publication_year, pages, dimensions,
                            registration_number, isbn, dewey_code, price, storage_location,
                            language, document_type, availability, keywords, subject,
                            department, summary, cover_image, url
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        str(row.get('title', '')),
                        str(row.get('author', '')),
                        str(row.get('publisher', '')),
                        pub_year,
                        str(row.get('pages', '')),
                        str(row.get('dimensions', '')),
                        str(row.get('registration_number', '')),
                        str(row.get('isbn', '')),
                        str(row.get('dewey_code', '')),
                        str(row.get('price', '')),
                        str(row.get('storage_location', '')),
                        str(row.get('language', '')),
                        str(row.get('document_type', '')),
                        str(row.get('availability', '')),
                        str(row.get('keywords', '')),
                        str(row.get('subject', '')),
                        str(row.get('department', '')),
                        str(row.get('summary', '')),
                        str(row.get('cover_image', '')),
                        str(row.get('url', ''))
                    ))
                    success_count += 1
                    
                    # Hiển thị tiến độ
                    if (index + 1) % 10 == 0 or index + 1 == len(df):
                        print(f"⏳ Đã xử lý {index + 1}/{len(df)} dòng...")
                        
                except Exception as e:
                    error_count += 1
                    print(f"⚠️ Lỗi tại dòng {index + 1}: {str(e)}")
            
            # Lưu thay đổi
            conn.commit()
            conn.close()
            
            print(f"\n🎉 Hoàn thành chuyển đổi!")
            print(f"✓ Thành công: {success_count} dòng")
            print(f"❌ Lỗi: {error_count} dòng")
            print(f"💾 Dữ liệu đã được lưu vào: {self.db_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi chuyển đổi CSV sang DB: {str(e)}")
            return False
    
    def show_db_stats(self):
        """Hiển thị thống kê database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Đếm tổng số sách
            cursor.execute('SELECT COUNT(*) FROM books')
            total_books = cursor.fetchone()[0]
            
            print(f"\n📊 Thống kê database:")
            print(f"   - Tổng số sách: {total_books}")
            
            # Thống kê theo ngôn ngữ
            cursor.execute('SELECT language, COUNT(*) FROM books GROUP BY language ORDER BY COUNT(*) DESC')
            languages = cursor.fetchall()
            
            print("   - Phân bố ngôn ngữ:")
            for lang, count in languages:
                print(f"     • {lang}: {count} sách")
            
            # Thống kê theo khoa
            cursor.execute('SELECT department, COUNT(*) FROM books GROUP BY department ORDER BY COUNT(*) DESC LIMIT 5')
            departments = cursor.fetchall()
            
            print("   - Top 5 khoa có nhiều sách nhất:")
            for dept, count in departments:
                print(f"     • {dept}: {count} sách")
            
            # Hiển thị 3 sách mẫu
            cursor.execute('SELECT title, author, publication_year FROM books LIMIT 3')
            sample_books = cursor.fetchall()
            
            print(f"\n📚 Mẫu sách trong database:")
            for i, (title, author, year) in enumerate(sample_books, 1):
                print(f"   {i}. {title}")
                print(f"      Tác giả: {author}")
                print(f"      Năm: {year}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Lỗi khi hiển thị thống kê: {str(e)}")

def main():
    """Hàm main để chạy chuyển đổi"""
    print("=== CHUYỂN ĐỔI DỮ LIỆU TỪ CSV SANG DATABASE ===\n")
    
    # Tạo đối tượng converter
    converter = CSVToDatabase("duytan_books.db")
    
    # Tìm file CSV
    csv_files = []
    possible_files = [
        "duytan_books.csv",
        "random_36_books.csv", 
        "books_data.csv"
    ]
    
    for file in possible_files:
        if os.path.exists(file):
            csv_files.append(file)
    
    if not csv_files:
        print("❌ Không tìm thấy file CSV nào!")
        print("📝 Các file CSV được hỗ trợ:")
        for file in possible_files:
            print(f"   - {file}")
        return
    
    print("📋 Tìm thấy các file CSV:")
    for i, file in enumerate(csv_files, 1):
        size = os.path.getsize(file) / 1024  # KB
        print(f"   {i}. {file} ({size:.1f} KB)")
    
    # Nếu có nhiều file, cho user chọn
    if len(csv_files) > 1:
        try:
            choice = int(input(f"\nChọn file CSV (1-{len(csv_files)}): ")) - 1
            if 0 <= choice < len(csv_files):
                selected_file = csv_files[choice]
            else:
                print("❌ Lựa chọn không hợp lệ!")
                return
        except ValueError:
            print("❌ Vui lòng nhập số!")
            return
    else:
        selected_file = csv_files[0]
    
    print(f"\n🚀 Bắt đầu chuyển đổi file: {selected_file}")
    
    # Thực hiện chuyển đổi
    success = converter.csv_to_db(selected_file)
    
    if success:
        # Hiển thị thống kê
        converter.show_db_stats()
    else:
        print("❌ Chuyển đổi thất bại!")

if __name__ == "__main__":
    main()
