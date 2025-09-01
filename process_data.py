import pandas as pd
import psycopg2
from psycopg2 import sql
import glob

# --- PENGATURAN KONEKSI DATABASE ---
DB_NAME = "mydatabase"
DB_USER = "myuser"
DB_PASS = "mypassword"
DB_HOST = "localhost"
DB_PORT = "5432"

def create_table(conn):
    """
    Fungsi untuk membuat tabel 'products' dengan skema kolom yang baru dan lengkap.
    """
    print("Ensuring 'products' table exists with the correct schema...")
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS products;")
        cur.execute("""
            CREATE TABLE products (
                id INT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                price INT,
                original_price VARCHAR(50),
                discount_percentage VARCHAR(50),
                detail VARCHAR(100),
                platform VARCHAR(50),
                product_master_id INT,
                created_at TIMESTAMPTZ
            );
        """)
    print("Table 'products' created successfully with the new schema.")

def insert_data(conn, df):
    """
    Fungsi untuk memasukkan data dari DataFrame ke tabel products yang baru.
    """
    print(f"Inserting {len(df)} rows into the database...")
    with conn.cursor() as cur:
        for index, row in df.iterrows():
            columns = [sql.Identifier(col) for col in row.index]
            values = [row[col] if pd.notna(row[col]) else None for col in row.index]
            
            insert_query = sql.SQL("INSERT INTO products ({}) VALUES ({})").format(
                sql.SQL(', ').join(columns),
                sql.SQL(', ').join(sql.Placeholder() * len(values))
            )
            
            cur.execute(insert_query, values)
            
    print("Insertion complete.")

def main():
    """Fungsi utama untuk menjalankan seluruh proses."""
    conn = None
    try:
        # Menggunakan nama file yang lebih spesifik
        processed_files = glob.glob('*_cleaned.csv') 
        if not processed_files:
            print("Error: Tidak ada file '*_cleaned.csv' yang ditemukan.")
            return

        print(f"Ditemukan {len(processed_files)} file yang sudah diproses: {', '.join(processed_files)}")
        
        df_combined = pd.concat(
            [pd.read_csv(f) for f in processed_files], 
            ignore_index=True
        )
        print(f"Data gabungan dari semua file. Total baris: {len(df_combined)}")

        # --- PERBAIKAN DI SINI ---
        # 1. Hapus kolom 'id' yang lama (yang menyebabkan duplikasi)
        if 'id' in df_combined.columns:
            df_combined = df_combined.drop('id', axis=1)
        
        # 2. Buat kolom 'id' baru yang berurutan untuk seluruh data gabungan
        df_combined.insert(0, 'id', range(1, len(df_combined) + 1))
        print("Kolom 'id' lama dihapus dan dibuat ulang agar unik dan berurutan.")
        # -------------------------

        # Ganti nama kolom lain agar cocok dengan skema database
        df_combined.rename(columns={'productmasterid': 'product_master_id', 'createdat': 'created_at'}, inplace=True)

        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        print("Successfully connected to the database.")

        create_table(conn)
        insert_data(conn, df_combined)

        conn.commit()
        print("Transactions committed to the database.")

    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()