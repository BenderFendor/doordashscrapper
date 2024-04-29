import json
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import json
import os

def scrolldownbutonlyalittle(driver):
    driver.execute_script("window.scrollBy(0, 1000);")

def scraper(url):

    driver = uc.Chrome(enable_cdp_events=True, use_subprocess=True)

    driver.implicitly_wait(30)
    driver.maximize_window()

    print("Opening Chrome...")
    print("url: ", url)
    
    driver.get(url)


    find = driver.find_element(By.XPATH, '//*[@id="__NEXT_DATA__"]')

    # Doesn't Scrape all items

    # Dumb workaround to get it to work inside childern folders
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print("Current Working Directory: ", os.getcwd())

    search_part = url.split("/")[-2]
    print("Search Part: ", search_part)
        
    if not os.path.exists('jsonfiles'):
        os.mkdir('jsonfiles')
    
    tabname = driver.title

    fileoutput = "jsonfiles/" + tabname + search_part + ".json"

    
    if find.is_enabled():
        print("Element is enabled")
        with open(fileoutput, "w", encoding='utf-8') as file:
            print("Printing File...")
            json_data = json.loads(find.get_attribute('innerHTML'))
            json.dump(json_data, file, indent=4)
    else:
        print("Element is disabled")

    driver.quit()
    
def jsonreader(jsonfile):
    # Dumb workaround to get it to work inside childern folders
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("Current Working Directory: ", os.getcwd())

    with open(jsonfile, 'r', encoding='utf-8') as file:
        data = file.read()

    # Parse the JSON data
    parsed_data = json.loads(data)

    pageTitle = parsed_data["props"]["pageProps"]["pageProps"]["pageTitle"]

    print(pageTitle)  # Outputs: ACME (2101 Cottman Avenue),
    
    parsed_data = parsed_data["props"]["pageProps"]["ssrPageProps"]["initialApolloState"]["ROOT_QUERY"]

    outputname = pageTitle + ".csv"

    # Define a function to find a key in a nested dictionary because without this idk how you get the data
    def find_key_in_dict(dictionary, key):
        if key in dictionary:
            return dictionary[key]
        for k, v in dictionary.items():
            if isinstance(v, dict):
                item = find_key_in_dict(v, key)
                if item is not None:
                    return item

    legoRetailItems = find_key_in_dict(parsed_data, 'legoRetailItems')

    for item in legoRetailItems:
        __typename = item["__typename"]
        id_ = item["id"]
        childrenCount = item["childrenCount"]
        component_ref = item["component"]["__ref"]
        custom_data = json.loads(item["custom"])  # Parse custom field separately
        item_data = custom_data["item_data"]
        item_name = item_data["item_name"]
        price = item_data["price"]["display_string"]
        store_name = item_data["store_name"]
        image_uri = custom_data["image"]["remote"]["uri"]
        
        print(f"item_name: {item_name} and price: {price} and image_uri: {image_uri}")

        # export to csv
        with open(outputname, "a") as file:
            empty = (file.tell() == 0)
            if empty:
                file.write("item_name,price,image_url,image_urlpart2,image_urlpart3,image_urlpart4,image_urlpart5\n")
            file.write(f"{item_name},{price},{image_uri}\n")

def main():
    searchs = ['meat', 'produce', 'bakery', 'snacks', 'beverages', 'pantry', 'frozen', 'dairy', 'eggs', 'deli', 'household', 'health', 'beauty', 'baby', 'pet', 'alcohol']

    # Automate getting mutiple stores many even like just putting a location and it gets all the near by grocery stores idk?

    basicurl = "https://www.doordash.com/convenience/store/24666862/search/*/?attr_src=home&disable_spell_check=false"
    urls = []
    for search in searchs:
        urls.append(basicurl.replace("*", search))
    
    print(urls)

    for url in urls:
        scraper(url)

    # get all the json files in the dir
    jsonfiles = [f for f in os.listdir('jsonfiles') if f.endswith(".json")]

    
    for jsons in jsonfiles:
        jsons = "jsonfiles/" + jsons
        jsonreader(jsons)

if __name__ == "__main__":
    main()