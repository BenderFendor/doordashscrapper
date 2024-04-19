import json
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
import os

def scrolldownbutonlyalittle(driver):
    driver.execute_script("window.scrollBy(0, 1000);")

driver = uc.Chrome(enable_cdp_events=True, use_subprocess=True)

driver.implicitly_wait(30)
driver.maximize_window()

driver.get("https://www.doordash.com/convenience/store/24666582/search/*/?attr_src=search&disable_spell_check=false")

find = driver.find_element(By.XPATH, '//*[@id="__NEXT_DATA__"]')

# Dumb workaround to get it to work inside childern folders
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print("Current Working Directory: ", os.getcwd())

if find.is_enabled():
    print("Element is enabled")
    with open("doordashoutput.json", "w", encoding='utf-8') as file:
        print("Printing File...")
        json_data = json.loads(find.get_attribute('innerHTML'))
        json.dump(json_data, file, indent=4)
else:
    print("Element is disabled")

driver.quit()