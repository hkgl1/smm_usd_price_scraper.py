import chromedriver_autoinstaller
chromedriver_autoinstaller.install()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import pandas as pd
from pathlib import Path
import time

# Set up headless Chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

try:
    url = "https://www.metal.com/Lithium/201905160001"
    driver.get(url)
    time.sleep(10)

    # Extract the leftmost USD/mt VAT-excluded price
    print(driver.page_source)
    price_element = driver.find_element(By.XPATH, "(//div[contains(text(), 'VAT excluded')]/ancestor::div[contains(@class, 'price-item')]//span)[1]")
    raw_price = price_element.text.strip().replace(",", "")
    usd_price = float(raw_price)

    # Prepare CSV file
    csv_path = Path("usd_lithium_price.csv")
    today = datetime.now().strftime("%Y-%m-%d")

    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame(columns=["Date", "USD/mt (ex VAT)"])

    # Add new row and save
    new_row = pd.DataFrame([[today, usd_price]], columns=["Date", "USD/mt (ex VAT)"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(csv_path, index=False)

    print(f"[{today}] Price logged: ${usd_price} USD/mt (VAT excluded)")

except Exception as e:
    print("Extraction failed:", e)

driver.quit()
