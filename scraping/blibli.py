from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re
from datetime import datetime, timezone, timedelta
import random

def hitung_persentase_diskon(harga_asli_str, harga_jual_str):
    """Menghitung persentase diskon dari dua string harga."""
    try:
        harga_asli = int(re.sub(r'\D', '', harga_asli_str))
        harga_jual = int(re.sub(r'\D', '', harga_jual_str))
        if harga_asli > harga_jual and harga_asli > 0:
            persentase = round(((harga_asli - harga_jual) / harga_asli) * 100)
            return f"{persentase}%"
        else:
            return "0%"
    except (ValueError, TypeError, ZeroDivisionError):
        return "N/A"

# ===================================================================
# PUSAT KONTROL & PENYAMARAN
# ===================================================================
wib_timezone = timezone(timedelta(hours=7))

# --- OPSI UNTUK MENYAMBUNG KE BROWSER ---
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
# -----------------------------------------------------------

driver = webdriver.Chrome(options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

try:
    print("Successfully attached to the existing browser session!")
    print(f"Page Title: {driver.title}")

    print("\nScrolling page a bit more just in case...")
    for _ in range(2):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4)) 

    print("Parsing HTML from the currently open page...")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    products = soup.find_all('div', class_='elf-product-card__container')
    print(f"Found {len(products)} total products on page.")
    
    data = []
    successful_product_count = 0
    MAX_PRODUCTS_TO_SCRAPE = 15
    
    for i, item in enumerate(products):
        if successful_product_count >= MAX_PRODUCTS_TO_SCRAPE:
            print(f"\nBatas {MAX_PRODUCTS_TO_SCRAPE} produk tercapai. Menghentikan proses parsing.")
            break
        try:
            # Menggunakan selector yang lebih spesifik dan stabil
            name_elem = item.find('span', class_='els-product__title')
            price_elem = item.find('div', class_='els-product__fixed-price')
            originalprice_elem = item.find('span', class_='els-product__discount-price')
            
            name = name_elem.text.strip() if name_elem else "N/A"
            price = price_elem.text.strip() if price_elem else "N/A"
            originalprice = originalprice_elem.text.strip() if originalprice_elem else price
            discountpercentage = hitung_persentase_diskon(originalprice, price)
            timestamp_now = datetime.now(wib_timezone).isoformat()
            
            product_data = {
                'name': name,
                'price': price,
                'original_price': originalprice,
                'discount_percentage': discountpercentage,
                'createdat': timestamp_now
            }

            # --- PERUBAHAN DI SINI ---
            # Blok 'if "N/A" in product_data.values():' telah dihapus.
            # Sekarang semua produk akan langsung diproses dan ditampilkan.
            
            successful_product_count += 1
            
            print(f"Product #{successful_product_count} (dari max {MAX_PRODUCTS_TO_SCRAPE}):")
            print(f"  Name: {name}")
            print(f"  Price: {price}")
            print(f"  Original Price: {originalprice}")
            print(f"  Discount: {discountpercentage}")
            print(f"  CreatedAt: {timestamp_now}")
            print("-" * 50)
            
            data.append(product_data)
            
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            print(f"Error parsing product on page #{i+1}: {e}")
            continue
            
    if data:
        df = pd.DataFrame(data)
        df.to_csv('blibli_attached_session_all.csv', index=False, encoding='utf-8')
        print(f"\nSuccess! Scraped {len(data)} total products.")
        print("Data saved to blibli_attached_session_all.csv")
    else:
        print("\nNo products found to save.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    print("\nScript finished. Browser session remains open.")
    # driver.quit()