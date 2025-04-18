import chromedriver_autoinstaller
chromedriver_autoinstaller.install()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd
from pathlib import Path

# Set up headless Chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# All product names and URLs in the desired order
products = {
    "Li2CO3 Technical Grade": "https://www.metal.com/Lithium/201905160001",
    "Li2CO3 Battery Grade": "https://www.metal.com/Chemical-Compound/201102250059",
    "LiOH Industrial Grade": "https://www.metal.com/Lithium/202005200001",
    "LiOH Battery Grade (Coarse)": "https://www.metal.com/Lithium/201102250281",
    "LiOH Battery Grade (CIF CJK)": "https://www.metal.com/Lithium/202107020004",
    "LiOH Battery Grade (Micro)": "https://www.metal.com/Lithium/202106020003",
    "LiOH Battery Grade (SMM Index)": "https://www.metal.com/Lithium/202212140004",
    "6s pCAM Mono NEV": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202312220004",
    "6s pCAM Poly CE": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/201805220002",
    "6s Cathode Mono NEV": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202306150001",
    "6s Cathode Poly CE": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/201805220001",
    "6s Prismatic Cell": "https://www.metal.com/Lithium-ion-Battery/202405230003",
    "6s Prismatic Pack": "https://www.metal.com/Lithium-ion-Battery/202405230006",
    "6s Battery Pack": "https://www.metal.com/Used-Lithium-ion-Battery/202502250003",
    "8s pCAM Poly NEV": "https://www.metal.com/Ternary-precursor-material/202005200002",
    "8s pCAM Poly CE": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202312220005",
    "8s Cathode Poly NEV": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202006100012",
    "8s Cathode Poly CE": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202304230003",
    "8s Battery Cell": "https://www.metal.com/Lithium-ion-Battery/202412230001",
    "8s Battery Pack": "https://www.metal.com/Used-Lithium-ion-Battery/202502250004"
}

def extract_price_info(driver, url):
    driver.get(url)
    try:
        price_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH,
                "//div[contains(@class, 'priceItem')][.//div[text()='VAT excluded']]//div[contains(@class, 'price___')]"
            ))
        )
        price_range_element = driver.find_element(By.XPATH,
            "//span[contains(text(), 'Price Range')]/following-sibling::span"
        )

        avg = float(price_element.text.replace(",", "").strip())
        min_, max_ = [float(x.replace(",", "").strip()) for x in price_range_element.text.split("-")]
        price_range = round(max_ - min_, 2)
        return min_, max_, avg, price_range

    except Exception as e:
        print(f"Failed to extract from {url}: {e}")
        return None, None, None, None

# Main scraping process
driver = webdriver.Chrome(options=options)
today = datetime.now().strftime("%Y-%m-%d")
all_data = {"Date": [today]}

for name, url in products.items():
    min_, max_, avg, rng = extract_price_info(driver, url)
    all_data[f"{name} Min"] = [min_]
    all_data[f"{name} Max"] = [max_]
    all_data[f"{name} Avg"] = [avg]
    all_data[f"{name} Range"] = [rng]

driver.quit()

# Save to CSV
csv_path = Path("daily_lithium_prices_horizontal.csv")
if csv_path.exists():
    df_old = pd.read_csv(csv_path)
    df_new = pd.DataFrame(all_data)
    df = pd.concat([df_old, df_new], ignore_index=True)
else:
    df = pd.DataFrame(all_data)

df.to_csv(csv_path, index=False)
print(f"[{today}] All prices logged successfully.")
