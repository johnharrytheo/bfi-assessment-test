import psycopg2
from fastapi import FastAPI, Depends, HTTPException, Header, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

# --- PENGATURAN KONEKSI DATABASE ---
DB_NAME = "mydatabase"
DB_USER = "myuser"
DB_PASS = "mypassword"
DB_HOST = "localhost"
DB_PORT = "5432"

# --- PENGATURAN API ---
app = FastAPI(
    title="Product Price API (3-Table Schema)",
    description="API untuk mengakses data produk, master produk, dan rekomendasi harga.",
    version="2.0.0"
)

# --- MEKANISME AUTENTIKASI ---
SECRET_API_KEY = "INI_ADALAH_KUNCI_RAHASIA_SAYA_12345"

async def verify_api_key(x_api_key: str = Header(..., description="API Key untuk otentikasi")):
    """Dependensi untuk memverifikasi API Key."""
    if x_api_key != SECRET_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# --- MODEL DATA (Pydantic) UNTUK SKEMA BARU ---

class ProductMaster(BaseModel):
    id: int
    type: Optional[str] = None
    name: Optional[str] = None
    detail: Optional[str] = None

class Product(BaseModel):
    id: int
    name: Optional[str] = None
    price: Optional[int] = None
    original_price: Optional[str] = None
    discount_percentage: Optional[str] = None
    detail: Optional[str] = None
    platform: Optional[str] = None
    product_master_id: int
    created_at: Optional[datetime] = None

class PriceRecommendation(BaseModel):
    # Menambahkan nama produk untuk membuatnya lebih informatif
    product_master_id: int
    product_name: str = Field(..., alias='name') # Menggunakan alias untuk mencocokkan nama kolom dari JOIN
    recommended_price: int = Field(..., alias='price')
    recommendation_date: date = Field(..., alias='date')

    class Config:
        populate_by_name = True # Mengizinkan penggunaan alias

# --- FUNGSI HELPER ---
def get_db_connection():
    """Membuka koneksi baru ke database."""
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )

def fetch_query_results(query: str, params: tuple = None):
    """Fungsi generik untuk menjalankan query SELECT dan mengembalikan hasilnya."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(query, params)
        if cur.description is None:
            return []
        colnames = [desc[0] for desc in cur.description]
        results = [dict(zip(colnames, row)) for row in cur.fetchall()]
    conn.close()
    return results

# --- ENDPOINTS API ---

@app.get("/")
def read_root():
    """Endpoint selamat datang."""
    return {"message": "Welcome to the new Product Price API. Access /docs for documentation."}

@app.get("/product-masters", 
         response_model=List[ProductMaster],
         summary="Get All Product Masters",
         dependencies=[Depends(verify_api_key)])
def get_all_product_masters():
    """Mengambil daftar semua produk master yang unik."""
    query = "SELECT id, type, name, detail FROM product_master ORDER BY id;"
    return fetch_query_results(query)

@app.get("/products", 
         response_model=List[Product],
         summary="Get All Product Listings (Filterable)",
         dependencies=[Depends(verify_api_key)])
def get_all_products(master_id: Optional[int] = Query(None, description="Filter by product_master_id")):
    """
    Mengambil semua data listing produk individual.
    Bisa difilter berdasarkan product_master_id.
    """
    if master_id:
        query = "SELECT * FROM product WHERE product_master_id = %s ORDER BY id;"
        params = (master_id,)
    else:
        query = "SELECT * FROM product ORDER BY id;"
        params = None
    return fetch_query_results(query, params)

@app.get("/recommendations/today", 
         response_model=List[PriceRecommendation],
         summary="Get Today's Price Recommendations with Product Names",
         dependencies=[Depends(verify_api_key)])
def get_today_recommendations():
    """
    Mengambil rekomendasi harga untuk hari ini, digabungkan (JOIN) dengan
    nama produk dari tabel product_master untuk membuatnya lebih informatif.
    """
    query = """
        SELECT
            pr.product_master_id,
            pm.name,
            pr.price,
            pr.date
        FROM
            price_recommendation pr
        JOIN
            product_master pm ON pr.product_master_id = pm.id
        WHERE
            pr.date = CURRENT_DATE
        ORDER BY
            pr.product_master_id;
    """
    return fetch_query_results(query)