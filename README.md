# Sistem Scraper dan Rekomendasi Harga E-commerce

Proyek ini adalah sistem end-to-end yang dirancang untuk mengumpulkan data produk dari berbagai platform e-commerce, memprosesnya, menyimpan dalam database, dan menyajikannya melalui API dengan model rekomendasi harga sederhana.

## Fitur Utama
- **Web Scraping Multi-Platform**: Mengambil data produk (nama, harga, diskon) dari Tokopedia, Blibli, dan KlikIndomaret menggunakan Selenium dan BeautifulSoup.
- **Pemrosesan & Standarisasi Data**: Membersihkan, memformat, dan menstrukturkan data mentah ke dalam skema 3-tabel yang ternormalisasi (`product_master`, `product`, `price_recommendation`).
- **Penyimpanan Data**: Menggunakan **PostgreSQL** yang berjalan di dalam container **Docker** untuk penyimpanan data yang persisten dan terisolasi.
- **Model Rekomendasi Harga**: Sebuah model Machine Learning (Regresi Linear) sederhana untuk menghasilkan rekomendasi harga berdasarkan data historis.
- **REST API**: Dibangun dengan **FastAPI** untuk menyajikan data produk dan rekomendasi harga, lengkap dengan dokumentasi otomatis dan autentikasi via API Key.

## Arsitektur Sistem
Sistem ini terdiri dari beberapa komponen yang bekerja secara berurutan:

1.  **Scrapers (`Selenium`)** → Mengambil data mentah dari situs web.
2.  **File CSV Mentah** → Hasil output sementara dari scraper.
3.  **Data Processor (`Pandas`)** → Membersihkan dan menstrukturkan data dari file CSV.
4.  **Loader Script (`psycopg2`)** → Memuat data terstruktur ke dalam database.
5.  **PostgreSQL Database (`Docker`)** → Menyimpan semua data secara permanen.
6.  **ML Recommender (`scikit-learn`)** → Membaca data dari DB, membuat prediksi, dan menyimpan hasilnya kembali ke DB.
7.  **REST API (`FastAPI`)** → Membaca data dari DB dan menyajikannya ke pengguna.

## Tumpukan Teknologi (Tech Stack)
- **Bahasa**: Python 3.9+
- **Web Scraping**: Selenium, BeautifulSoup4
- **Pemrosesan Data**: Pandas
- **Database**: PostgreSQL
- **Kontainerisasi**: Docker, Docker Compose
- **API**: FastAPI, Uvicorn
- **Driver Database**: psycopg2-binary
- **Machine Learning**: Scikit-learn

---

## Panduan Instalasi & Menjalankan Sistem Secara Lokal

### Prasyarat
- [Python 3.9](https://www.python.org/downloads/) atau lebih tinggi
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/downloads/) (Opsional, untuk kloning repositori)

### 1. Setup Awal
```bash
# 1. Kloning repositori ini
git clone https://github.com/johnharrytheo/bfi-assessment-test
cd bfi-assesment-test

# 2. (Sangat disarankan) Buat dan aktifkan virtual environment
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Instal semua library yang dibutuhkan
pip install -r requirements.txt
```
**File `requirements.txt`:**
```
selenium
beautifulsoup4
pandas
psycopg2-binary
fastapi[all]
scikit-learn
webdriver-manager
```

### 2. Menjalankan Sistem (Urutan Penting)

#### Langkah A: Jalankan Database
Pastikan Docker Desktop sedang berjalan. Buka terminal di root folder proyek dan jalankan:
```bash
docker-compose up -d
```
Perintah ini akan membuat dan menjalankan container PostgreSQL di latar belakang. Anda bisa memverifikasinya dengan `docker ps`.

#### Langkah B: Kumpulkan & Proses Data
1.  **Jalankan Scraper**: Jalankan skrip-skrip scraper untuk mengumpulkan data mentah dan menyimpannya sebagai file CSV. (Contoh: `python scraper_tokopedia.py`)
2.  **Strukturkan Data**: Jalankan skrip untuk memproses file-file CSV mentah menjadi format yang bersih dan terstruktur. (Contoh: `python process_structured_data.py`)
3.  **Muat ke Database**: Jalankan skrip untuk memuat data yang sudah terstruktur ke dalam PostgreSQL.
    ```bash
    py load_to_db.py
    ```

#### Langkah C: Hasilkan Rekomendasi Harga
Jalankan skrip model ML untuk menganalisis data di database dan mengisi tabel `price_recommendation`.
```bash
py ml_recommender.py
```

#### Langkah D: Jalankan Server API
Terakhir, jalankan server API untuk menyajikan data.
```bash
uvicorn main_api:app --reload
```
Server API sekarang berjalan di `http://127.0.0.1:8000`.

---

## Dokumentasi & Pengujian API

API ini dilindungi oleh API Key. Gunakan key berikut di header `X-API-Key`: `INI_ADALAH_KUNCI_RAHASIA_SAYA_12345`

1.  **Buka Dokumentasi Interaktif**: Buka browser Anda dan kunjungi `http://127.0.0.1:8000/docs`.
2.  **Lakukan Uji Coba**:
    - Klik pada salah satu *endpoint*.
    - Klik **"Try it out"**.
    - Masukkan API Key di atas.
    - Klik **"Execute"** untuk melihat hasilnya.

| Method | Endpoint | Deskripsi |
| :--- | :--- | :--- |
| `GET` | `/product-masters` | Menampilkan semua produk master yang unik. |
| `GET` | `/products` | Menampilkan semua listing produk. Bisa difilter dengan `?master_id=...` |
| `GET` | `/recommendations/today` | Menampilkan rekomendasi harga untuk hari ini, lengkap dengan nama produk. |

---

## Diskusi: Peningkatan & Skalabilitas

Proyek ini dapat dikembangkan lebih lanjut dengan beberapa cara:
- **Skalabilitas Scraper**: Menggunakan *message queue* (seperti RabbitMQ/Kafka) dan *worker* terdistribusi (seperti Celery) untuk menjalankan puluhan scraper secara paralel.
- **Robustness**: Mengimplementasikan layanan proxy profesional dengan rotasi IP dan user-agent yang lebih canggih untuk menghindari blokir.
- **Model Machine Learning**: Mengganti model Regresi Linear sederhana dengan model yang lebih kompleks seperti *Gradient Boosting* (XGBoost) atau model *time-series* (seperti LSTM) jika data historis harga dikumpulkan dari waktu ke waktu.
- **Deployment & CI/CD**: Memindahkan database ke layanan *managed* (seperti AWS RDS), men-deploy API ke cloud (seperti AWS ECS atau Google Cloud Run), dan membuat pipeline CI/CD (menggunakan GitHub Actions) untuk otomatisasi testing dan deployment.
- **Keamanan API**: Mengganti API Key statis dengan standar yang lebih aman seperti OAuth2/JWT untuk autentikasi pengguna.