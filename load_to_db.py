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

def create_tables(conn):
    """
    Membuat 3 tabel (product_master, product, price_recommendation)
    sesuai dengan skema yang diminta.
    """
    print("Creating the 3-table schema...")
    with conn.cursor() as cur:
        # Hapus tabel lama dengan urutan yang benar untuk menghindari error foreign key
        cur.execute("DROP TABLE IF EXISTS price_recommendation;")
        cur.execute("DROP TABLE IF EXISTS product;")
        cur.execute("DROP TABLE IF EXISTS product_master;")

        # 1. Membuat tabel product_master
        cur.execute("""
            CREATE TABLE product_master (
                id INT PRIMARY KEY,
                type VARCHAR(100),
                name VARCHAR(255),
                detail TEXT
            );
        """)
        
        # 2. Membuat tabel product
        cur.execute("""
            CREATE TABLE product (
                id INT PRIMARY KEY,
                name VARCHAR(255),
                price INT,
                original_price VARCHAR(50),
                discount_percentage VARCHAR(50),
                detail VARCHAR(100),
                platform VARCHAR(50),
                product_master_id INT,
                created_at TIMESTAMPTZ,
                FOREIGN KEY (product_master_id) REFERENCES product_master (id)
            );
        """)

        # 3. Membuat tabel price_recommendation
        cur.execute("""
            CREATE TABLE price_recommendation (
                product_master_id INT,
                price INT,
                date DATE,
                PRIMARY KEY (product_master_id, date),
                FOREIGN KEY (product_master_id) REFERENCES product_master (id)
            );
        """)
    print("Schema created successfully: product_master, product, price_recommendation.")

def insert_product_master_data(conn, df):
    """Mengisi tabel product_master dengan data unik."""
    print("Inserting data into 'product_master' table...")
    # Ambil baris unik berdasarkan productmasterid
    df_master = df.drop_duplicates(subset=['productmasterid']).copy()
    
    with conn.cursor() as cur:
        for _, row in df_master.iterrows():
            cur.execute(
                """
                INSERT INTO product_master (id, type, name, detail)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    row['productmasterid'],
                    'Consumer Goods', # Contoh tipe statis
                    row['name'],      # Ambil nama representatif
                    f"Master data for product group {row['productmasterid']}" # Contoh detail statis
                )
            )
    print(f"Inserted {len(df_master)} rows into product_master.")

def insert_product_data(conn, df):
    """Mengisi tabel product dengan semua data individual."""
    print("Inserting data into 'product' table...")
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO product (id, name, price, original_price, discount_percentage, detail, platform, product_master_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    row['id'], row['name'], row['price'], row['original_price'],
                    row['discount_percentage'], row['detail'], row['platform'],
                    row['productmasterid'], row['createdat']
                )
            )
    print(f"Inserted {len(df)} rows into product.")

def main():
    """Fungsi utama untuk menjalankan seluruh proses."""
    conn = None
    try:
        # Cari dan gabungkan semua file yang sudah diproses
        processed_files = glob.glob('*_cleaned.csv')
        if not processed_files:
            print("Error: Tidak ada file '*_cleaned.csv' yang ditemukan.")
            return

        print(f"Menggabungkan file: {', '.join(processed_files)}")
        df_combined = pd.concat([pd.read_csv(f) for f in processed_files], ignore_index=True)
        # Membuat ulang ID unik untuk data gabungan
        df_combined['id'] = range(1, len(df_combined) + 1)
        print(f"Data gabungan dari semua file. Total baris: {len(df_combined)}")

        # Hubungkan ke DB
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        print("Successfully connected to the database.")

        # Jalankan semua fungsi
        create_tables(conn)
        insert_product_master_data(conn, df_combined)
        insert_product_data(conn, df_combined)

        conn.commit()
        print("Transactions committed to the database.")

    except Exception as e:
        print(f"An error occurred: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close(); print("Database connection closed.")

if __name__ == "__main__":
    main()