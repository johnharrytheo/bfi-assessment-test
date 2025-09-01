from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import re
from datetime import datetime, timezone, timedelta

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

wib_timezone = timezone(timedelta(hours=7))
url = "https://www.tokopedia.com/unilever-official-store/product"

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=chrome_options)

try:
    print("Loading page...")
    driver.get(url)
    time.sleep(5)
    
    print("Scrolling page...")
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
    
    print("Parsing HTML...")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    products = soup.find_all('div', class_='y-oybT3IAd310DVdH3OwVg==')
    print(f"Found {len(products)} total products on page.")
    
    data = []
    # 1. Variabel baru untuk menghitung produk yang berhasil
    successful_product_count = 0
    
    for i, item in enumerate(products):
        try:
            name_elem = item.find('span', class_='+tnoqZhn89+NHUA43BpiJg==')
            price_elem = item.find('div', class_='urMOIDHH7I0Iy1Dv2oFaNw== HJhoi0tEIlowsgSNDNWVXg==')
            originalprice_elem = item.find('span', class_='hC1B8wTAoPszbEZj80w6Qw==')
            
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

            if "N/A" in product_data.values():
                # 2. Gunakan 'i + 1' untuk pesan 'DILEWATI' agar tahu posisi aslinya
                print(f"Product on page #{i+1}: '{name}' DILEWATI karena data tidak lengkap.")
                continue
            
            # 3. Tambah 1 ke counter produk berhasil & gunakan untuk penomoran
            successful_product_count += 1
            print(f"Product #{successful_product_count}:") # Gunakan counter baru
            print(f"  Name: {name}")
            print(f"  Price: {price}")
            print(f"  Original Price: {originalprice}")
            print(f"  Discount: {discountpercentage}")
            print(f"  CreatedAt: {timestamp_now}")
            print("-" * 50)
            
            data.append(product_data)
            
        except Exception as e:
            print(f"Error parsing product on page #{i+1}: {e}")
            continue
            
    if data:
        df = pd.DataFrame(data)
        df.to_csv('tokopedia_products_clean.csv', index=False, encoding='utf-8')
        print(f"\nSuccess! Scraped {len(data)} complete products.")
        print("Data saved to tokopedia_products_clean.csv")
    else:
        print("\nNo complete products found to save.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    print("Closing browser...")
    driver.quit()