from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
import json
from math import isfinite
from pathlib import Path
import re
from subprocess import CalledProcessError, check_output
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import chromedriver_autoinstaller
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait



BENCHMARK_PATHS = {
    'SMM Battery-Grade Lithium Carbonate Index (USD/tonne)': 'Lithium/202212050001',
    'Battery-Grade Lithium Carbonate CIF China, Japan and South Korea (USD/kg)': 'Lithium/202306050001',
    'Lithium Sulfate from Africa (CIF China) (USD/tonne)': 'Lithium/202601160004',
    'SMM Battery-Grade Nickel Sulphate Index (USD/tonne)': 'Nickel/202208290001',
    'China Cobalt Sulfate Index (USD/tonne)': 'Cobalt/202212210003',
    'Rotterdam Cobalt Metal (USD/lb)': 'Cobalt/202507310003',
    'China Cobalt Metal FOB (USD/lb)': 'Cobalt/202406250012',
    'China Cobalt Hydroxide (USD/lb)': 'Cobalt/201905280003',
    'China Cobalt Hydroxide Payable (%)': 'Cobalt/202209220002',
    'FOB Nickel in Indonesian MHP (USD/nickel tonne)': 'Nickel/202407290001',
    'SMM FOB Cobalt in Indonesian MHP (USD/cobalt tonne)': 'Nickel/202507310002',
    'MHP Payable Against SMM Battery-grade Nickel Sulphate Index Price (%)': 'Nickel/202208300002',
    'China MHP Cobalt Payable (%)': 'Nickel/202209220001',
    'MHP Cobalt Payable to SMM Rotterdam Cobalt Metal (%)': 'Nickel/202511050013',
    'China NCM 111 Black Mass (USD/tonne)': 'Battery-Recycling/202311230003',
    'China NCM 523 Black Mass (USD/tonne)': 'Battery-Recycling/202311230004',
    'China NCM 622 Black Mass (USD/tonne)': 'Battery-Recycling/202311230005',
    'China NCM 811 Black Mass (USD/tonne)': 'Battery-Recycling/202311230006',
    'China NCM Battery Black Mass (USD/tonne)': 'Battery-Recycling/202311230007',
    'China LCO Battery Black Mass (USD/tonne)': 'Battery-Recycling/202311230008',
    'China LCO Black Mass (USD/tonne)': 'Battery-Recycling/202311230009',
    'China LFP Black Mass (USD/tonne)': 'Battery-Recycling/202303270007',
    'China LFP Battery Black Mass (USD/tonne)': 'Battery-Recycling/202303270008',
    'China NCM Black Mass Nickel Indicator Index (%)': 'Battery-Recycling/202510270001',
    'China NCM Black Mass Lithium Indicator Index (%)': 'Battery-Recycling/202510270002',
    'China NCM Black Mass Cobalt Indicator Index (%)': 'Battery-Recycling/202510270003',
    'China NCM Battery Black Mass Nickel Indicator Index (%)': 'Battery-Recycling/202510270004',
    'China NCM Battery Black Mass Lithium Indicator Index (%)': 'Battery-Recycling/202510270005',
    'China NCM Battery Black Mass Cobalt Indicator Index (%)': 'Battery-Recycling/202510270006',
    'China LCO Black Mass Cobalt Indicator Index (%)': 'Battery-Recycling/202510270007',
    'China LCO Black Mass lithium Indicator Index (%)': 'Battery-Recycling/202510270008',
    'China LCO Battery Black Mass Cobalt Indicator Index (%)': 'Battery-Recycling/202510270009',
    'China LCO Battery Black Mass lithium Indicator Index (%)': 'Battery-Recycling/202510270010',
    'China LFP Black Mass Indicator Cofficient (%)': 'Battery-Recycling/202303270009',
    'China LFP Battery Black Mass Indicator Cofficient (%)': 'Battery-Recycling/202303270010',
    'China LFP Black Mass Indicator (USD/lithium unit)': 'Battery-Recycling/202303270011',
    'China LFP Battery Black Mass lithium Indicator (USD/lithium unit)': 'Battery-Recycling/202303270012',
    'NCM Black Mass Nickel Payable FOB Malaysia (%)': 'Battery-Recycling/202512050003',
    'NCM Black Mass Cobalt Payable FOB Malaysia (%)': 'Battery-Recycling/202512050004',
    'NCM Black Mass Lithium Payable FOB Malaysia (%)': 'Battery-Recycling/202512050005',
    'NCM Battery Black Mass Cobalt Payable FOB Malaysia (%)': 'Battery-Recycling/202601050001',
    'NCM Battery Black Mass Nickel Payable FOB Malaysia (%)': 'Battery-Recycling/202601050002',
    'NCM Battery Black Mass Lithium Payable FOB Malaysia (%)': 'Battery-Recycling/202601050003',
    'Black Mass Nickel Payable FOB Korea (%)': 'Battery-Recycling/202509090003',
    'Black Mass Cobalt Payable FOB Korea (%)': 'Battery-Recycling/202509090002',
    'NCM Battery Black Mass Cobalt Payable FOB Korea (%)': 'Battery-Recycling/202511260011',
    'NCM Battery Black Mass Nickel Payable FOB Korea (%)': 'Battery-Recycling/202511260012',
    'China LFP Positive Pole Piece (USD/tonne)': 'Battery-Recycling/202303270004',
    'China LFP ESS Positive Pole Piece (USD/tonne)': 'Battery-Recycling/202303270005',
    'China Scrap LFP Aluminum Shell Battery Pack (USD/tonne)': 'Battery-Recycling/202502250001',
'China Ferrous Phosphate (USD/tonne)': 'Phosphorus/202111010002',
    'China Ferrous Phosphate (Restorative) (USD/tonne)': 'Phosphorus/202502170001',
    'China Lithium Ferrous Phosphate (Powder Compact Density 2.50g/cm³ min) (USD/tonne)': 'Phosphorus/201801180001',
    'China Lithium Ferrous Phosphate (ESS Type, Powder Compact Density 2.40 g/cm³ min) (USD/tonne)': 'Phosphorus/202210310001',
    'Sodium Sulphate (USD/tonne)': 'Sodium-ion-Battery/202005210138',
    'SMM CIF Indonesia Sodium Hydroxide (USD/tonne)': 'Nickel/202511260009',
    'China Flake Graphite (Shandong)-194 (USD/tonne)': 'Carbon-Anode/202005210030',
    'China Flake Graphite (Heilongjiang)-194 (USD/tonne)': 'Carbon-Anode/202005210031',
    'China Flake Graphite (Inner Mongolia)-194 (USD/tonne)': 'Carbon-Anode/202005210032',
    'China Flake Graphite (Henan)-194 (USD/tonne)': 'Carbon-Anode/202005210033',
    'China Flake Graphite (Nationwide Average Price) - 194 (USD/tonne)': 'Carbon-Anode/202005210034',
    'China Flake Graphite (Heilongjiang)-195 (USD/tonne)': 'Carbon-Anode/202005210035',
    'China Flake Graphite (Inner Mongolia)-195 (USD/tonne)': 'Carbon-Anode/202005210036',
    'China Flake Graphite (Shandong)-195 (USD/tonne)': 'Carbon-Anode/202005210037',
    'China Flake Graphite (Nationwide Average Price) - 195 (USD/tonne)': 'Carbon-Anode/202005210038',
    'China Spherical Graphite (China) (USD/tonne)': 'Carbon-Anode/202005210040',
    'China Spherical Graphite (Shandong) (USD/tonne)': 'Carbon-Anode/202005210041',
    'China Spherical Graphite (Heilongjiang) (USD/tonne)': 'Carbon-Anode/202005210042',
    'China Spherical Graphite (Nationwide Average Price) (USD/tonne)': 'Carbon-Anode/202005210043',
    'China Natural Graphite (High-end) (USD/tonne)': 'Carbon-Anode/202005200007',
    'China Natural Graphite (Mid-end) (USD/tonne)': 'Carbon-Anode/202005200008',
    'China Natural Graphite (Low-end) (USD/tonne)': 'Carbon-Anode/202108310002',
    'China Artificial Graphite (for Low-end ESS Battery) (USD/tonne)': 'Carbon-Anode/202409020001',
    'China Artificial Graphite (for Mid-end ESS Battery) (USD/tonne)': 'Carbon-Anode/202409020002',
    'China Artificial Graphite (for High-end ESS Battery) (USD/tonne)': 'Carbon-Anode/202409020003',
    'China Artificial Graphite (for Low-end EV Battery) (USD/tonne)': 'Carbon-Anode/202409020004',
    'China Artificial Graphite (for Mid-end EV Battery) (USD/tonne)': 'Carbon-Anode/202409020005',
    'China Artificial Graphite (for High-end EV Battery) (USD/tonne)': 'Carbon-Anode/202409020006',
    'China Artificial Graphite (for Low-end Consumer Battery) (USD/tonne)': 'Carbon-Anode/202409020007',
    'China Artificial Graphite (for Mid-end Consumer Battery) (USD/tonne)': 'Carbon-Anode/202409020008',
    'China Artificial Graphite (for High-end Consumer Battery) (USD/tonne)': 'Carbon-Anode/202409020009',
    'China LFP Black Powder Mass Indicator Index (USD/lithium unit)': 'Battery-Recycling/202510270011',
    'China LFP Black Battery Mass Indicator Index (USD/lithium unit)': 'Battery-Recycling/202510270012',
    'China Ternary Aluminum Shell (Type 523) Battery (USD/tonne)': 'Battery-Recycling/202106240003',
    'China Ternary Cylindrical Steel Shell (USD/tonne)': 'Battery-Recycling/202307110001',
    'China Ternary Pouch Battery (USD/tonne)': 'Battery-Recycling/202307110002',
    'China Small Ternary Cylindrical Steel Shell (USD/tonne)': 'Battery-Recycling/202307280001',
    'China Ternary Aluminum Shell (USD/tonne)': 'Battery-Recycling/202307280002',
    'China Small Ternary Pouchl (USD/tonne)': 'Battery-Recycling/202307280003',
    'China Scrap LFP Aluminum Shell Battery (USD/tonne)': 'Battery-Recycling/202303270001',
    'China Scrap LFP Steel Shell Battery (USD/tonne)': 'Battery-Recycling/202303270002',
    'China Scrap LFP Pouch Battery (USD/tonne)': 'Battery-Recycling/202303270003',
    'China LCO Aluminum Shell (USD/tonne)': 'Battery-Recycling/202307280007',
    'China LCO Polymer Pouch (USD/tonne)': 'Battery-Recycling/202106240001',
    'China Scrap Pure Cobalt LCO Aluminum Shell Battery (USD/tonne)': 'Battery-Recycling/202509280003',
    'China Scrap High-Cobalt LCO Aluminum Shell Battery (USD/tonne)': 'Battery-Recycling/202509280004',
    'China Nickel-Cobalt Slag (USD/tonne)': 'Battery-Recycling/202412200004',
    'China Nicke-Cobalt Slag Nickel Indicator (%)': 'Battery-Recycling/202405150001',
    'China Nicke-Cobalt Slag Cobalt Indicator (%)': 'Battery-Recycling/202405150002',
    'China NCM Black Mass Nickel Indicator (%)': 'Battery-Recycling/202302090001',
    'China NCM Black Mass Cobalt Indicator (%)': 'Battery-Recycling/202302090002',
    'China NCM Black Mass Lithium Indicator (%)': 'Battery-Recycling/202302090003',
    'China NCM Black Mass Nickel High Indicator (%)': 'Battery-Recycling/202412200005',
    'China NCM Black Mass High Nickel Cobalt Indicator (%)': 'Battery-Recycling/202503130003',
    'China NCM Black Mass High Nickel Lithium Indicator (%)': 'Battery-Recycling/202503130004',
    'China NCM Battery Black Mass Nickel High Indicator (%)': 'Battery-Recycling/202302090004',
    'China NCM Battery Black Mass Cobalt Indicator (%)': 'Battery-Recycling/202302090005',
    'China NCM Battery Black Mass Lithium Indicator (%)': 'Battery-Recycling/202302090006',
 'China LCO Black Mass Cobalt Indicator (%)': 'Battery-Recycling/202302230001',
    'China LCO Black Mass Lithium Indicator Cofficient (%)': 'Battery-Recycling/202302230002',
    'China LCO Battery Black Mass Cobalt Indicator (%)': 'Battery-Recycling/202302230003',
    'China LCO Battery Black Mass Lithium Indicator (%)': 'Battery-Recycling/202302230004',
    'FOB Nickel in Indonesian High-grade Nickel Matte (USD/nickel tonne)': 'Nickel/202409100001',
    'SMM Shanghai 1# Nickel Cathode (USD/tonne)': 'Nickel/201102250239',
    'Shanghai Jinchuan #1 Refined Nickel (USD/tonne)': 'Nickel/201102250174',
    'Shanghai #1 Imported Refined Nickel (USD/tonne)': 'Nickel/201102250423',
    'SMM Indonesia Refined Nickel (USD/tonne)': 'Nickel/202509120003',
    'China Phosphoric Acid (USD/tonne)': 'Phosphorus/202307250001',
    'SMM Battery-Grade Manganese Sulphate Index (USD/tonne)': 'Nickel-And-Manganese/202208300001',
    'Australian Spodumene Concentrate 6% Li2O CIF China (USD/tonne)': 'Lithium/202311300003',
    'Zimbabwean Spodumene Concentrates 6% Li2O CIF China (USD/tonne)': 'Lithium/202408290001',
    'China Lepidolite Concentrates 1.5%-2.0% Li2O (USD/tonne)': 'Lithium/202005210116',
    'China Lepidolite Concentrates 2%-2.5% Li2O (USD/tonne)': 'Lithium/202005210117',
    'China Lithium Manganese Ferrous Phosphate (USD/tonne)': 'Phosphorus/202406250011',
    'China 4.20V Lithium Cobalt Oxide (USD/tonne)': 'Cathode-Material/202405220001',
    'China 4.40V Lithium Cobalt Oxide (USD/tonne)': 'Cathode-Material/201102250483',
    'China 4.45V Lithium Cobalt Oxide (USD/tonne)': 'Cathode-Material/202305040001',
    'China 4.48V Lithium Cobalt Oxide (USD/tonne)': 'Cathode-Material/202305040002',
    'China 4.50V Lithium Cobalt Oxide (USD/tonne)': 'Cathode-Material/202305040003',
    'China 4.53V Lithium Cobalt Oxide (USD/tonne)': 'Cathode-Material/202411130002',
    'China Restorative Lithium Ferrous Phosphate (USD/tonne)': 'Phosphorus/202404250006',
    'China Restorative Lithium Ferrous Phosphate （High-end) (USD/tonne)': 'Phosphorus/202512080006',
    'China Ternary Aluminum Shell Battery Cell Without Electrolyte Injection (USD/tonne)': 'Battery-Recycling/202307110003',
    'China Ternary Cylindrical Steel Shell Battery Cell Without Electrolyte Injection (USD/tonne)': 'Battery-Recycling/202307110004',
    'China Ternary Pouch Battery Cell Without Electrolyte Injection (USD/tonne)': 'Battery-Recycling/202307110005',
    'China LFP Aluminum Shell Battery Cell Without Electrolyte Injection (USD/tonne)': 'Battery-Recycling/202307110006',
    'China LFP Cylindrical Steel Shell Battery Cell Without Electrolyte Injection (USD/tonne)': 'Battery-Recycling/202307110007',
    'China LFP Pouch Battery Cell Without Electrolyte Injection (USD/tonne)': 'Battery-Recycling/202307110008',
    'China NCM 523 Jelly Roll (USD/tonne)': 'Battery-Recycling/202307110009',
    'China NCM 622 Jelly Roll (USD/tonne)': 'Battery-Recycling/202307110010',
    'China NCM 811 Jelly Roll (USD/tonne)': 'Battery-Recycling/202307110011',
    'China LFP Jelly Roll (USD/tonne)': 'Battery-Recycling/202307110012',
}


products = {
    "Li2CO3 Technical Grade": "https://www-old.metal.com/Lithium/201905160001",
    "Li2CO3 Battery Grade": "https://www-old.metal.com/Chemical-Compound/201102250059",
    "LiOH Industrial Grade": "https://www-old.metal.com/Lithium/202005200001",
    "LiOH Battery Grade (Coarse)": "https://www-old.metal.com/Lithium/201102250281",
    "LiOH Battery Grade (CIF CJK)": "https://www-old.metal.com/Lithium/202107020004",
    "LiOH Battery Grade (Micro)": "https://www-old.metal.com/Lithium/202106020003",
    "LiOH Battery Grade (SMM Index)": "https://www-old.metal.com/Lithium/202212140004",

    # --- NEW 5 SERIES ---
    "5s pCAM Mono NEV": "https://www-old.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202005200003",
    "5s pCAM Poly CE": "https://www-old.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/201603140002",
    "5s Cathode Mono NEV": "https://www-old.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202203280001",
    "5s Cathode Poly CE": "https://www-old.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/201603140001",

    # --- EXISTING 6 SERIES ---
    "6s pCAM Mono NEV": "https://www-old.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202312220004",
    "6s pCAM Poly CE": "https://www-old.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/201805220002",
    "6s Cathode Mono NEV": "https://www-old.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202306150001",
    "6s Cathode Poly CE": "https://www-old.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/201805220001",
    "6s Prismatic Cell": "https://www-old.metal.com/Lithium-ion-Battery/202405230003",
    "6s Prismatic Pack": "https://www-old.metal.com/Lithium-ion-Battery/202405230006",
    "6s Battery Pack": "https://www-old.metal.com/Used-Lithium-ion-Battery/202502250003",

    # --- EXISTING 8 SERIES ---
    "8s pCAM Poly NEV": "https://www-old.metal.com/Ternary-precursor-material/202005200002",
    "8s pCAM Poly CE": "https://www-old.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202312220005",
    "8s Cathode Poly NEV": "https://www-old.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202006100012",
    "8s Cathode Poly CE": "https://www-old.metal.com/Lithium%20Battery%20Cathode%20Precursor%20and%20Material/202304230003",
    "8s Battery Cell": "https://www-old.metal.com/Lithium-ion-Battery/202412230001",
    "8s Battery Pack": "https://www-old.metal.com/Used-Lithium-ion-Battery/202502250004",

    # --- NEW SULPHATES ---
    "Ni Sulphate": "https://www-old.metal.com/Nickel/201908270001",
    "Co Sulphate": "https://www-old.metal.com/Chemical-Compound/201102250381",
    "Mn Sulphate": "https://www-old.metal.com/manganese/201805300001"
}

products.update({
    name: "https://www-old.metal.com/" + path
    for name, path in BENCHMARK_PATHS.items()
})

LME_CONTRACTS = {
    "LME Nickel": ("non-ferrous/lme-nickel", "3-month"),
    "LME Cobalt": ("ev/lme-cobalt", "3-month"),
    "LME Cobalt (Fastmarkets MB)": ("ev/lme-cobalt-fastmarkets-mb", "Month 2"),
}

VAT_PANELS = "//div[contains(@class, 'priceItem')]"
VAT_EXCLUDED = (
    VAT_PANELS + "[.//div[normalize-space()='VAT excluded']]"
    "//div[contains(@class, 'price___')]"
)
PLAIN_AVERAGE = "//span[normalize-space()='Avg.:']/following-sibling::span[1]"
PRICE_RANGE = "//span[normalize-space()='Price Range:']/following-sibling::span[1]"
NUMBER = r"[+−-]?[0-9][0-9,]*(?:\.[0-9]+)?"
RANGE_PATTERN = re.compile(rf"({NUMBER})\s*[-–—−]\s*({NUMBER})")


def read_smm_quote(find_text, has_vat_panels):
    bounds = RANGE_PATTERN.fullmatch(find_text(PRICE_RANGE))
    if not bounds:
        return None

    def amount(value):
        return Decimal(value.replace(",", "").replace("−", "-"))

    try:
        low, high = map(amount, bounds.groups())
        average_text = find_text(VAT_EXCLUDED if has_vat_panels else PLAIN_AVERAGE)
        if re.fullmatch(NUMBER, average_text):
            average = amount(average_text)
        elif not has_vat_panels and not average_text:
            heading = find_text("//h1")
            if heading.endswith("%"):
                average = (low + high) / 2
            elif heading.endswith("USD/lithium unit") and low == high:
                average = low
            else:
                return None
        else:
            return None
    except InvalidOperation:
        return None

    if low > high:
        return None
    return tuple(map(float, (low, high, average, high - low)))


def extract_price_info(driver, url):
    def current_quote(browser):
        def find_text(xpath):
            matches = browser.find_elements(By.XPATH, xpath)
            return matches[0].text.strip() if matches else ""

        return read_smm_quote(find_text, bool(browser.find_elements(By.XPATH, VAT_PANELS)))

    try:
        driver.get(url)
        return WebDriverWait(driver, 20).until(current_quote)
    except WebDriverException as error:
        print(f"Could not read the SMM quote at {url}: {type(error).__name__}")
        return None, None, None, None


SUMMARY_TABS = {
    "LME Nickel": "Summary",
    "LME Cobalt": "Trading+summary",
    "LME Cobalt (Fastmarkets MB)": "Trading+day+summary",
}

READ_TABLE = r"""
const wanted = arguments[0].toLowerCase();
for (const table of document.querySelectorAll('table[aria-describedby]')) {
    const header = document.getElementById(table.getAttribute('aria-describedby'));
    const title = header?.querySelector('.data-set-table__title')?.textContent.trim();
    if (title?.toLowerCase() !== wanted) continue;
    const panel = table.closest('[id^="dataset-tab-"]');
    const date = panel?.innerText.match(/Data valid for\s+(\d{1,2} [A-Za-z]{3} \d{4})/i)?.[1];
    const rows = Array.from(table.tBodies[0]?.rows ?? []).map(row => [
        row.querySelector('[data-table-column-header="Contract"]')?.textContent.trim(),
        row.querySelector('[data-table-column-header="Price"]')?.textContent.trim(),
    ]);
    if (date && rows.some(([contract, price]) => contract && price)) return [date, rows];
}
return null;
"""


def parse_lme_curve(quote_date, rows):
    closing_date = datetime.strptime(quote_date, "%d %b %Y").date().isoformat()
    prices = {}
    for label, value in rows:
        if not label or not value:
            continue
        if re.fullmatch(r"[A-Za-z]{3} \d{2}", label):
            prompt = datetime.strptime(label, "%b %y").strftime("%Y-%m")
        elif label.casefold() == "3-month":
            prompt = "3-month"
        else:
            # Retain any new prompt label LME introduces.
            prompt = label
        try:
            close = float(value.replace(",", ""))
        except ValueError:
            continue
        if isfinite(close):
            prices[prompt] = close

    if not prices:
        raise ValueError("No numeric closes in the LME contract table")
    return closing_date, prices


def fetch_lme_curve(driver, contract, path):
    url = f"https://www.lme.com/metals/{path}#{SUMMARY_TABS[contract]}"
    try:
        driver.get(url)
        quote_date, rows = WebDriverWait(driver, 20).until(
            lambda browser: browser.execute_script(READ_TABLE, f"{contract} Closing Prices")
        )
        return parse_lme_curve(quote_date, rows)
    except (WebDriverException, ValueError) as error:
        print(f"Could not read the {contract} closing curve: {type(error).__name__}")
        return None, {}


def fetch_lme_headline(contract, path, tenor):
    """Use the public contract-page headline when the live table is unavailable."""
    class Headline(HTMLParser):
        def __init__(self):
            super().__init__()
            self.date = ""
            self.fields = {"hero-metal-data__number": "", "hero-metal-data__text": ""}
            self.active = None

        def handle_starttag(self, tag, attributes):
            attrs = dict(attributes)
            if tag == "day-delayed-data-table":
                if attrs.get("header", "").casefold() == f"{contract} Closing Prices".casefold():
                    self.date = attrs.get("valid-for-text", "")
            elif tag in ("div", "span"):
                for css_class in attrs.get("class", "").split():
                    if css_class in self.fields:
                        self.active = (tag, css_class)
                        break

        def handle_data(self, data):
            if self.active:
                self.fields[self.active[1]] += data

        def handle_endtag(self, tag):
            if self.active and tag == self.active[0]:
                self.active = None

    try:
        body = check_output(
            ["curl", "-fsSL", "--compressed", "--max-time", "20",
             f"https://www.lme.com/metals/{path}"],
            encoding="utf-8",
        )
        page = Headline()
        page.feed(body)
        expected = f"{tenor} Closing Price (day-delayed)"
        caption = " ".join(page.fields["hero-metal-data__text"].split())
        date = re.search(r"\b\d{2}/\d{2}/\d{4}\b", page.date)
        close = float(page.fields["hero-metal-data__number"].strip().replace(",", ""))
        if caption.casefold() != expected.casefold() or not date or not isfinite(close):
            raise ValueError("Wrong tenor or missing LME headline date")
        return close, datetime.strptime(date.group(), "%d/%m/%Y").date().isoformat()
    except (OSError, CalledProcessError, ValueError) as error:
        print(f"Could not read the {contract} headline: {type(error).__name__}")
        return None, None


SETTLEMENTS_URL = "https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/8971/FUT"


def front_month_settlement(data, trade_date):
    if data.get("dsHeader") != "Cobalt Metal (Fastmarkets) Futures":
        raise ValueError("Unexpected CME settlement product")
    if datetime.strptime(data["tradeDate"], "%m/%d/%Y").date() != trade_date:
        raise ValueError("CME returned a different trade date")

    months = []
    for row in data.get("settlements", []):
        try:
            month = datetime.strptime(row["month"], "%b %y").date()
        except ValueError:
            continue
        if month >= trade_date.replace(day=1):
            months.append((month, row["settle"]))

    if not months:
        return None
    month, value = min(months, key=lambda entry: entry[0])
    try:
        settlement = float(value.replace(",", ""))
    except ValueError:
        return None
    if not isfinite(settlement) or settlement <= 0:
        return None
    return settlement, month.strftime("%Y-%m"), trade_date.isoformat()


def fetch_cme_cobalt_front_month(as_of=None):
    if as_of is None:
        as_of = datetime.now(ZoneInfo("America/Chicago")).date()

    for days_back in range(8):
        trade_date = as_of - timedelta(days=days_back)
        if trade_date.weekday() >= 5:
            continue
        params = urlencode({"tradeDate": trade_date.strftime("%m/%d/%Y"), "pageSize": 50})
        try:
            body = check_output(
                ["curl", "-fsSL", "--compressed", "--max-time", "10",
                 f"{SETTLEMENTS_URL}?{params}"],
                encoding="utf-8",
            )
            result = front_month_settlement(json.loads(body), trade_date)
        except (CalledProcessError, OSError, KeyError, TypeError, ValueError) as error:
            print(f"Could not read CME cobalt settlements for {trade_date}: {error}")
            return None, None, None
        if result:
            return result

    print("CME returned no cobalt front-month settlement in the last eight calendar days.")
    return None, None, None


def main():
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    sg_now = datetime.now(ZoneInfo("Asia/Singapore"))
    date_str = sg_now.strftime("%Y-%m-%d")
    time_str = sg_now.strftime("%H:%M")
    all_data = {"Date": date_str, "Time (SGT)": time_str}
    smm_successes = 0
    curves = {}

    with webdriver.Chrome(options=options) as driver:
        driver.set_page_load_timeout(30)
        for name, url in products.items():
            low, high, average, spread = extract_price_info(driver, url)
            smm_successes += average is not None
            if spread is not None and name not in BENCHMARK_PATHS:
                spread = round(spread, 2)
            all_data[f"{name} Min"] = low
            all_data[f"{name} Max"] = high
            all_data[f"{name} Avg"] = average
            all_data[f"{name} Range"] = spread

        for name, (path, _) in LME_CONTRACTS.items():
            curves[name] = fetch_lme_curve(driver, name, path)

    lme_successes = 0
    for name, (path, tenor) in LME_CONTRACTS.items():
        curve_date, curve = curves[name]
        close = curve.get(tenor)
        quote_date = curve_date
        if close is None:
            close, quote_date = fetch_lme_headline(name, path, tenor)
        lme_successes += close is not None or bool(curve)
        all_data[f"{name} {tenor} Close (USD/t)"] = close
        all_data[f"{name} {tenor} Quote Date"] = quote_date
        all_data[f"{name} Curve Quote Date"] = curve_date
        for prompt, price in curve.items():
            if prompt != tenor:
                all_data[f"{name} {prompt} Close (USD/t)"] = price

    cme_close, cme_month, cme_date = fetch_cme_cobalt_front_month()
    all_data["CME COB Front Month Settlement (USD/lb)"] = cme_close
    all_data["CME COB Front Month Contract Month"] = cme_month
    all_data["CME COB Settlement Trade Date"] = cme_date

    if not (smm_successes or lme_successes or cme_close is not None):
        raise RuntimeError("No SMM, LME or CME quotes were available. CSV was not updated.")

    csv_path = Path("daily_lithium_prices_horizontal.csv")
    new_data = pd.DataFrame([all_data])
    if csv_path.exists():
        new_data = pd.concat([pd.read_csv(csv_path), new_data], ignore_index=True)
    new_data.to_csv(csv_path, index=False)
    print(
        f"[{date_str} {time_str}] Logged {smm_successes}/{len(products)} SMM quotes, "
        f"{lme_successes}/{len(LME_CONTRACTS)} LME products "
        f"({sum(len(curve) for _, curve in curves.values())} closing-table rows), "
        f"and {int(cme_close is not None)}/1 CME quotes."
    )


if __name__ == "__main__":
    main()

