from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
# 1. Tambahkan kembali import untuk datetime
from datetime import datetime, timezone, timedelta

# --- Pengaturan Awal ---
# 2. Tambahkan kembali definisi zona waktu
wib_timezone = timezone(timedelta(hours=7))
url = "https://www.klikindomaret.com/search/?key=unilever"

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
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
    
    print("Parsing HTML...")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    products = soup.find_all('div', class_='card-product relative h-[254px] w-full !border des:h-[363px] sm:!w-[160px] md:!w-[148px] lg:!w-[169px] des:!w-full overflow-hidden')
    print(f"Found {len(products)} total products on page.")
    
    data = []
    successful_product_count = 0
    
    for i, item in enumerate(products):
        try:
            name_elem = item.find('h2', class_='md-0 line-clamp-2 text-b1 text-neutral-70 des:mb-2')
            price_elem = item.find('div', class_='wrp-price')
            
            name = name_elem.text.strip() if name_elem else "N/A"
            price = price_elem.text.strip() if price_elem else "N/A"
            
            # 3. Buat timestamp seperti sebelumnya
            timestamp_now = datetime.now(wib_timezone).isoformat()
            
            # Tambahkan 'createdat' ke dalam dictionary
            product_data = {
                'name': name,
                'price': price,
                'createdat': timestamp_now
            }

            if "N/A" in product_data.values():
                print(f"Product on page #{i+1}: '{name}' DILEWATI karena data tidak lengkap.")
                continue
            
            successful_product_count += 1
            print(f"Product #{successful_product_count}:")
            print(f"  Name: {name}")
            print(f"  Price: {price}")
            print(f"  CreatedAt: {timestamp_now}") # Tampilkan juga di log
            print("-" * 50)
            
            data.append(product_data)
            
        except Exception as e:
            print(f"Error parsing product on page #{i+1}: {e}")
            continue
            
    if data:
        df = pd.DataFrame(data)
        df.to_csv('indomaret_products_timestamped.csv', index=False, encoding='utf-8')
        print(f"\nSuccess! Scraped {len(data)} complete products.")
        print("Data saved to indomaret_products_timestamped.csv")
    else:
        print("\nNo complete products found to save.")
        with open('debug_indomaret.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("HTML saved to debug_indomaret.html for inspection.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    print("Closing browser...")
    driver.quit()