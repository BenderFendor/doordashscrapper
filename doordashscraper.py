<<<<<<< HEAD
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from time import sleep
from bs4 import BeautifulSoup

def scrolldownbutonlyalittle(driver):
    driver.execute_script("window.scrollBy(0, 1000);")

driver = uc.Chrome(enable_cdp_events=True, use_subprocess=True)

driver.implicitly_wait(30)
driver.maximize_window()

# navigate to the application home page
driver.get("https://www.doordash.com/convenience/store/24666582/?event_type=autocomplete&pickup=false")

search_field = driver.find_element(By.ID, "FieldWrapper-2")

print(search_field)

# enter search keyword and submit
if search_field.is_displayed():
    print("search field is displayed")
    search_field.send_keys("450 Easton Rd, Warrington, PA")
    print(search_field.get_attribute("value"))
    search_field.send_keys(Keys.RETURN)

    # Click button
    continue_button = driver.find_element(By.CSS_SELECTOR, ".eEQFmZ")
    if continue_button.is_displayed():
        print("Button is displayed")
        driver.execute_script("arguments[0].click();", continue_button) 
        print("Button clicked")
    else:
        print("Button is not displayed")
else:
    print("Search field is not displayed")

driver.get("https://www.doordash.com/convenience/store/24666582/search/*/?attr_src=search&disable_spell_check=false")

food_items = driver.find_elements(By.CSS_SELECTOR, ".sc-47165498-2.eubzCg")

def getfooditems(driver,food_items,startcount=0):
    try:

        print(f"Found {len(food_items)} food items")
        
        for i, item in enumerate(food_items):
            i = i + startcount

            if (i + 1) % 10 == 0:
                sleep(3)
                scrolldownbutonlyalittle(driver)
            print(f"Item {i}:")
            name = item.find_element(By.CSS_SELECTOR, "[data-telemetry-id='priceNameInfo.name']").text

            price = item.find_element(By.CSS_SELECTOR, ".jbmWRu").text
            
            try:
                # Set a timeout for waiting for the element
                itemcount_elements = WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".iSSisX")))
                if itemcount_elements:  # Check if elements are found
                    itemcount = itemcount_elements[0].text
                    formatted_price = f"{price}{itemcount}"
                else:
                    formatted_price = price
            except:
                # If element not found within timeout, handle the situation here
                print("Element not found. Skipping...")
                formatted_price = price

            print(f"Name: {name} Price: {formatted_price}")

            if i == len(food_items) - 1:
                print("Reached the end of the list")
                scrolldownbutonlyalittle(driver)
                food_items = food_items + driver.find_elements(By.CSS_SELECTOR, ".sc-47165498-2.eubzCg")
                sleep(3)
                getfooditems(driver,food_items,i+1)

    except TimeoutException:
        print("Food items not found within the specified timeout.")
    # Handle the timeout exception as needed

getfooditems(driver,food_items)
=======
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
>>>>>>> master
