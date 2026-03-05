from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

import sys
import pandas as pd


SOCIAL_PROOF_ID = "social-proofing-faceout-title-tk_bought"
BOLD_SELECTOR = "span.a-text-bold"


def make_driver() -> webdriver.Edge:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--start-maximized")

    driver = webdriver.Edge(options=options)
    wait = WebDriverWait(driver, 20)

    driver.set_page_load_timeout(20)
    return driver


def get_bought_number(url,driver, wait):
    try:
        driver.get(url)

        container = wait.until(
            EC.presence_of_element_located((By.ID, SOCIAL_PROOF_ID))
        )

        bold_text = container.find_element(By.CSS_SELECTOR, BOLD_SELECTOR).text.strip()
        number_only = bold_text.split()[0]
        return number_only

    except (TimeoutException, WebDriverException):
        return "0"
    except Exception:
        return "0"


def main():
    file_path = sys.argv[1]
    df = pd.read_csv(file_path)

    print(f"Processing {file_path} ({len(df)} URLs)...")

    driver = make_driver()
    wait = WebDriverWait(driver, 20)

    try:
        results = []
        for url in df["url"]:
            results.append(get_bought_number(url,driver, wait))

        df["units_sold"] = results
        df.to_csv(file_path, index=False)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()