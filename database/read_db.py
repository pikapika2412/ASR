#%%
import sqlite3
import pandas as pd

def read_data_book_db():
    db_path = "code_db/data_book.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get column names
    cursor.execute("PRAGMA table_info(books);")
    columns_info = cursor.fetchall()
    column_names = [col[1] for col in columns_info]
    num_columns = len(column_names)

    # Get number of rows
    cursor.execute("SELECT COUNT(*) FROM books;")
    num_rows = cursor.fetchone()[0]

    print(f"Number of rows: {num_rows}")
    print(f"Number of columns: {num_columns}")
    print(f"Column names: {column_names}")

    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)

    # Read 5 rows from books table into pandas DataFrame
    df = pd.read_sql_query("SELECT * FROM books LIMIT 1;", conn)
    print(df)

    conn.close()

if __name__ == "__main__":
    read_data_book_db()