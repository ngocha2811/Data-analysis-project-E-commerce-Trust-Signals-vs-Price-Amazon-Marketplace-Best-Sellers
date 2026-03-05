from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


marketplaces = ['co.uk','de','fr','it','es']

save_path = your_path #replace with your path
#def make_driver():

options = Options()
options.add_argument("--headless=new")   # run browser without UI
options.add_argument("--window-size=1920,1080")

driver = webdriver.Edge(options=options)
wait = WebDriverWait(driver, 10)


try:
    for marketplace in marketplaces:
        URL = f"https://www.amazon.{marketplace}/-/en/gp/bestsellers"

        df['marketplace'] = str(marketplace)


        #driver = make_driver()
        driver.get(URL)

        # Wait until dropdown is present
        wait.until(EC.presence_of_element_located((By.ID, "searchDropdownBox")))

        # Get all option elements
        options_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "#searchDropdownBox option"
        )

        # Extract only search-alias values
        categories = [
            opt.get_attribute("value").split("=")[1]
            for opt in options_elements
            if opt.get_attribute("value") and "search-alias=" in opt.get_attribute("value")
        ]

        df_new = pd.DataFrame({
        "marketplace": [marketplace] * len(categories),
        "category_path": categories
                })

        df = pd.concat([df, df_new], ignore_index=True)

        print(f'Processed {marketplace} marketplace, names of category:', categories)

finally:
    driver.quit()

df.to_csv(save_path,index=False)