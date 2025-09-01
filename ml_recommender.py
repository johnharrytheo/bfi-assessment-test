import pandas as pd
import psycopg2
from datetime import date

# --- PENGATURAN KONEKSI DATABASE ---
DB_NAME = "mydatabase"
DB_USER = "myuser"
DB_PASS = "mypassword"
DB_HOST = "localhost"
DB_PORT = "5432"

def fetch_product_data(conn):
    """Mengambil data harga dari tabel product dan mengagregasinya."""
    print("Fetching data from 'product' table...")
    query = """
        SELECT
            product_master_id,
            AVG(price) AS avg_price,
            MAX(
                CASE
                    WHEN original_price ~ '^[0-9]+$' THEN CAST(original_price AS INTEGER)
                    ELSE price
                END
            ) AS max_original_price
        FROM
            product -- Mengambil dari tabel 'product' yang baru
        WHERE
            price > 0
        GROUP BY
            product_master_id;
    """
    df = pd.read_sql_query(query, conn)
    print(f"Found {len(df)} unique master products to analyze.")
    return df

def generate_recommendations(df):
    """Menerapkan logika dummy model."""
    print("Generating price recommendations...")
    if df.empty: return df

    df['recommended_price'] = (df['avg_price'] * 0.95).round(-2).astype(int)
    return df

def store_recommendations(conn, df):
    """Menyimpan hasil rekomendasi ke dalam tabel price_recommendation."""
    today = date.today()
    print(f"Storing {len(df)} recommendations for date: {today}...")
    
    with conn.cursor() as cur:
        cur.execute("DELETE FROM price_recommendation WHERE date = %s;", (today,))
        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO price_recommendation (product_master_id, price, date)
                VALUES (%s, %s, %s)
                """,
                (int(row['product_master_id']), int(row['recommended_price']), today)
            )
    print("Recommendations stored successfully.")

def main():
    conn = None
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        print("Successfully connected to the database.")

        product_df = fetch_product_data(conn)
        recommendations_df = generate_recommendations(product_df)
        store_recommendations(conn, recommendations_df)
        
        conn.commit()
        print("Transactions committed.")
    except Exception as e:
        print(f"An error occurred: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close(); print("Database connection closed.")

if __name__ == "__main__":
    main()