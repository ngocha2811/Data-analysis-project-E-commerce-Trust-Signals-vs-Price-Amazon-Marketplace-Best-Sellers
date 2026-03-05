import re
import time
import random
from dataclasses import dataclass, asdict
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# ---------------------------
# Helpers
# ---------------------------

_ASIN_RE = re.compile(r"/(?:dp|gp/product)/([A-Z0-9]{10})", re.I)
_INT_RE = re.compile(r"(\d+)")


def jitter(a: float = 0.15, b: float = 0.45) -> None:
    time.sleep(random.uniform(a, b))


def first_text(root, selectors, default: str = "") -> str:
    for by, value in selectors:
        try:
            txt = root.find_element(by, value).text.strip()
            if txt:
                return txt
        except Exception:
            pass
    return default


def first_attr(root, selectors, attr: str, default: str = "") -> str:
    for by, value in selectors:
        try:
            val = root.find_element(by, value).get_attribute(attr)
            if val:
                return val.strip()
        except Exception:
            pass
    return default


def parse_asin(url: str) -> str:
    if not url:
        return ""
    m = _ASIN_RE.search(url)
    return m.group(1).upper() if m else ""


def parse_int(text: str):
    if not text:
        return None
    m = _INT_RE.search(text.replace(".", "").replace(",", ""))
    return int(m.group(1)) if m else None


# ---------------------------
# Data
# ---------------------------

@dataclass
class Product:
    page: int
    rank: int | None
    title: str
    price: str
    reviews_count: int | None
    rating: str
    asin: str
    url: str
    marketplace: str
    category_path: str


# ---------------------------
# Selenium (Headless + Faster)
# ---------------------------

def make_driver(timeout: int = 20) -> tuple[webdriver.Edge, WebDriverWait]:
    opts = EdgeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-background-networking")
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-renderer-backgrounding")
    opts.add_argument("--blink-settings=imagesEnabled=false")

 
    opts.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

    driver = webdriver.Edge(options=opts)
    driver.set_page_load_timeout(timeout)
    driver.implicitly_wait(0)
    wait = WebDriverWait(driver, timeout)
    return driver, wait


def scroll_page(driver: webdriver.Edge, steps: int = 6) -> None:
    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(steps):
        body.send_keys(Keys.PAGE_DOWN)
        jitter(0.12, 0.30)


def get_grid_items(driver: webdriver.Edge, wait: WebDriverWait, timeout: int = 15):
    """Return tiles if present; otherwise return empty list (no crash)."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.any_of(
                EC.presence_of_element_located((By.ID, "gridItemRoot")),
                EC.presence_of_element_located((By.ID, "zg-left-col")),   # bestseller layout container
                EC.presence_of_element_located((By.ID, "a-page")),        # generic page container
            )
        )
    except TimeoutException:
        return []

    tiles = driver.find_elements(By.ID, "gridItemRoot")
    return tiles


def extract_product(tile, marketplace: str, category_path: str, page_num: int) -> Product:
    url = first_attr(tile, [(By.CSS_SELECTOR, "a.a-link-normal")], attr="href", default="")
    asin = (tile.get_attribute("data-asin") or "").strip() or parse_asin(url)

    rank_text = first_text(
        tile,
        [
            (By.CSS_SELECTOR, "span.zg-bdg-text"),
            (By.CSS_SELECTOR, "span.zg-badge-text"),
            (By.XPATH, ".//span[contains(@class,'zg-bdg-text')]"),
            (By.XPATH, ".//span[contains(@class,'zg-badge-text')]"),
        ],
        default="",
    )
    rank = parse_int(rank_text)

    title = first_text(
        tile,
        [
            (By.CLASS_NAME, "_cDEzb_p13n-sc-css-line-clamp-3_g3dy1"),
            (By.CSS_SELECTOR, "div.p13n-sc-truncate-desktop-type2"),
            (By.CSS_SELECTOR, "div.p13n-sc-truncate"),
            (By.XPATH, ".//*[self::div or self::span][contains(@class,'p13n-sc-truncate')]"),
        ],
        default="no title",
    )

    price = first_text(
        tile,
        [
            (By.CLASS_NAME, "_cDEzb_p13n-sc-price_3mJ9Z"),
            (By.CSS_SELECTOR, "span.p13n-sc-price"),
            (By.CSS_SELECTOR, "span.a-price > span.a-offscreen"),
            (By.CSS_SELECTOR, "span.a-price-whole"),
        ],
        default="",
    )

    reviews_text = first_text(
        tile,
        [
            (By.CSS_SELECTOR, "span.a-size-small"),
            (By.XPATH, ".//span[contains(@class,'a-size-small')]"),
        ],
        default="",
    )
    reviews_count = parse_int(reviews_text)

    rating = (
        first_attr(tile, [(By.CSS_SELECTOR, "i.a-icon-star-small span.a-icon-alt")], attr="innerText", default="")
        or first_text(tile, [(By.CSS_SELECTOR, "span.a-icon-alt")], default="")
    )

    return Product(
        marketplace=marketplace,
        category_path=category_path,
        page=page_num,
        rank=rank,
        title=title,
        price=price,
        reviews_count=reviews_count,
        rating=rating,
        asin=asin,
        url=url,
    )


def scrape_many_categories(
    driver: webdriver.Edge,
    wait: WebDriverWait,
    marketplace: str,
    category_path: str,
    total_pages: int = 2,
) -> pd.DataFrame:
    results: list[Product] = []
    leaf = category_path.split("/")[-1]

    for page in range(1, total_pages + 1):
        url = (
            f"https://www.amazon.{marketplace}/-/en/gp/bestsellers/{category_path}/"
            f"ref=zg_bs_pg_{page}_{leaf}?ie=UTF8&pg={page}"
        )

        driver.get(url)
        jitter(0.2, 0.6)
        scroll_page(driver, steps=6)

        tiles = get_grid_items(driver, wait, timeout=15)

        # Retry once if nothing loaded (often fixes flaky loads)
        if not tiles:
            driver.refresh()
            jitter(0.2, 0.6)
            scroll_page(driver, steps=4)
            tiles = get_grid_items(driver, wait, timeout=15)

        if not tiles:
            print(f"SKIP (no tiles): {marketplace} | {category_path} | page {page}")
            continue

        for tile in tiles:
            try:
                results.append(extract_product(tile, marketplace, category_path, page))
            except Exception:
                continue

        jitter(0.25, 0.8)

    return pd.DataFrame(asdict(p) for p in results)




marketplaces = ['co.uk','de','fr','it','es']
category_paths = ['baby', 'beauty', 'automotive',  'computers', 
                  'photo',
       'electronics', 'fashion', 'outdoor',
        'grocery', 'handmade', 'drugstore', 
       'kitchen', 'industrial', 'appliances', 'lighting',
         'pets','sports', 'office-products', 'office','toys', 'photo',
         'garden', 'hpc', 'pet-supplies','officeproduct','sporting']

total_pages = 2

out_dir = Path('your_file_path') #replace with your own path
out_dir.mkdir(parents=True, exist_ok=True)
current_date = pd.Timestamp.now().date()

driver, wait = make_driver(timeout=20)
try:
    for marketplace in marketplaces:
        for category_path in category_paths:
            df = scrape_many_categories(
                driver=driver,
                wait=wait,
                marketplace=marketplace,
                category_path=category_path,
                total_pages=total_pages,
            )
            try:
                df['date'] = current_date
                file_name = f"amz_{marketplace}_{category_path}.csv"
                df.to_csv(out_dir / file_name, index=False)
                print(f'File saved to {out_dir}')
            except TypeError as e:
                print(f"Category path {category_path} doesn't exit at marketplace {marketplace}. Skip to the next category path...")
            
finally:
    driver.quit()
