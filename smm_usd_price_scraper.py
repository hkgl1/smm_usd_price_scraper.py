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
import pytz

# ---- SETUP CHROME ----
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# ---- DEFINE PRODUCTS ----
products = {
    "Li2CO3 Technical Grade": "https://www.metal.com/Lithium/201905160001",
    "Li2CO3 Battery Grade": "https://www.metal.com/Chemical-Compound/201102250059",
    "LiOH Industrial Grade": "https://www.metal.com/Lithium/202005200001",
    "LiOH Battery Grade (Coarse)": "https://www.metal.com/Lithium/201102250281",
    "LiOH Battery Grade (CIF CJK)": "https://www.metal.com/Lithium/202107020004",
    "LiOH Battery Grade (Micro)": "https://www.metal.com/Lithium/202106020003",
    "LiOH Battery Grade (SMM Index)": "https://www.metal.com/Lithium/202212140004",

    # --- NEW 5 SERIES ---
    "5s pCAM Mono NEV": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202005200003",
    "5s pCAM Poly CE": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/201603140002",
    "5s Cathode Mono NEV": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202203280001",
    "5s Cathode Poly CE": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/201603140001",

    # --- EXISTING 6 SERIES ---
    "6s pCAM Mono NEV": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202312220004",
    "6s pCAM Poly CE": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/201805220002",
    "6s Cathode Mono NEV": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202306150001",
    "6s Cathode Poly CE": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/201805220001",
    "6s Prismatic Cell": "https://www.metal.com/Lithium-ion-Battery/202405230003",
    "6s Prismatic Pack": "https://www.metal.com/Lithium-ion-Battery/202405230006",
    "6s Battery Pack": "https://www.metal.com/Used-Lithium-ion-Battery/202502250003",

    # --- EXISTING 8 SERIES ---
    "8s pCAM Poly NEV": "https://www.metal.com/Ternary-precursor-material/202005200002",
    "8s pCAM Poly CE": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202312220005",
    "8s Cathode Poly NEV": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202006100012",
    "8s Cathode Poly CE": "https://www.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202304230003",
    "8s Battery Cell": "https://www.metal.com/Lithium-ion-Battery/202412230001",
    "8s Battery Pack": "https://www.metal.com/Used-Lithium-ion-Battery/202502250004",

    # --- NEW SULPHATES ---
    "Ni Sulphate": "https://www.metal.com/Nickel/201908270001",
    "Co Sulphate": "https://www.metal.com/Chemical-Compound/201102250381",
    "Mn Sulphate": "https://www.metal.com/manganese/201805300001"
}

# ---- PRICE EXTRACTION FUNCTION ----
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

# ---- MAIN SCRAPING ----
driver = webdriver.Chrome(options=options)

# Record SG date and time
sg_now = datetime.now(pytz.timezone("Asia/Singapore"))
date_str = sg_now.strftime("%Y-%m-%d")
time_str = sg_now.strftime("%H:%M")

# Start building row data
all_data = {"Date": [date_str], "Time (SGT)": [time_str]}

for name, url in products.items():
    min_, max_, avg, rng = extract_price_info(driver, url)
    all_data[f"{name} Min"] = [min_]
    all_data[f"{name} Max"] = [max_]
    all_data[f"{name} Avg"] = [avg]
    all_data[f"{name} Range"] = [rng]

driver.quit()

# ---- CSV UPDATE ----
csv_path = Path("daily_lithium_prices_horizontal.csv")
df_new = pd.DataFrame(all_data)

if csv_path.exists():
    df_old = pd.read_csv(csv_path)
    df = pd.concat([df_old, df_new], ignore_index=True)
else:
    df = df_new

df.to_csv(csv_path, index=False)
print(f"[{date_str} {time_str}] All prices logged successfully.")
