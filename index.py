# Author: Jorge A. Gill Romero
# Date: April 2025


from bs4 import BeautifulSoup
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import StaleElementReferenceException

import os
import time
import random
import json
import requests
import sys
import csv
import datetime



VEHICLE_MAKES = [
    "acura", "alfa romeo", "aston martin", "audi", "bentley", "bmw", "buick", "cadillac", 
    "chevrolet", "chrysler", "citroën", "dodge", "ferrari", "fiat", "ford", "genesis", 
    "gmc", "honda", "hyundai", "infiniti", "jaguar", "jeep", "kia", "lamborghini", 
    "land rover", "lexus", "lincoln", "maserati", "mazda", "mclaren", "mercedes-benz", 
    "mini", "mitsubishi", "nissan", "peugeot", "porsche", "ram", "renault", "rolls-royce", 
    "saab", "subaru", "suzuki", "tesla", "toyota", "volkswagen", "volvo",
    "aprilia", "arctic cat", "can-am", "ducati", "harley-davidson", "honda motorcycles", 
    "indian", "kawasaki", "ktm", "polaris", "royal enfield", "suzuki motorcycles", 
    "triumph", "vespa", "yamaha", "freightliner", "hino", "international", "kenworth", 
    "mack", "peterbilt", "volvo trucks", "western star", "freightliner", "isuzu"
]

PRODUCT_TITLE_XPATH = '//div[@aria-hidden="false"]/h1'
PRODUCT_PRICE_XPATH = '//div[@aria-hidden="false"]/span'
PRODUCT_DESCRIPTION_XPATH = '//div[@aria-hidden="false"]/span'
PRODUCT_IMAGE_XPATH = "//img[contains(@alt, 'Product photo of')]"

MILEAGE = "background-position: -21px -63px;"
FUEL_TYPE_AND_TRANSMISSION = "background-position: -42px -63px;"
INTERIOR_EXTERIOR_COLOR = "background-position: -84px -21px;"
CONSUMPTION = "background-position: -84px -63px;"
DEBT = "background-position: -84px -63px;"
TITLE = "background-position: -84px -105px;"
OWNERS = 'background-position: -21px -181px;'
PAID_OFF = 'background-position: 0px 0px;'
CLEAN_TITLE = 'background-position: -63px -105px;'


abs_path = os.path.abspath(__file__)
dir_path = os.path.dirname(abs_path)

class fbm_scraper():
    
    
    def __init__(self, city_code, profile, proxy, threshold=100, headless=False, download_images=False):


        self.threshold = threshold
        self.download_images = download_images
        self.login_blocks = 0
        self.city_code = city_code
        # Set the options for the Chrome browser. Keep these to avoid detections.

        """options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--incognito")

        """

        self.browser = Driver(browser="chrome", user_data_dir=f"./profiles/{profile}", window_size="1440,900", block_images=True,headed=True, proxy=proxy, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")

        self.checkpoint = [x.replace(".json", "") for x in os.listdir(f"{dir_path}/publications/")]
        self.links = {}
        self.url_to_scrap = f"https://www.facebook.com/marketplace/{city_code}/vehicles?sortBy=creation_time_descend&exact=true"
        
        self.print_and_log(f"{self.city_code} INFO: Starting the scrap of city code.")

    def log(self, message):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        log_message = f"[{now}] {message}\n"
        log_file = os.path.join(dir_path, "scraper.log")
        with open(log_file, "a") as f:
            f.write(log_message)

    def print_and_log(self, message):
        self.log(message)
        print(message)

    def log_in(self, email, password):
        self.browser.get("https://www.facebook.com/")
        email_input = WebDriverWait(self.browser, 8).until(EC.presence_of_element_located((By.XPATH, "//input[contains(@aria-label, 'Email')]")))
        password_input = self.browser.find_element(By.XPATH, "//input[contains(@aria-label, 'Password')]")
        self.human_key_input(email_input, email)
        self.human_key_input(password_input, password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)
        try:
            captcha_prompt = self.browser.find_element(By.XPATH, "//span[contains(text(), 'Enter the characters you see')]")
            captcha = True
        except:
            captcha = False
        return captcha
    
    def change_language(self):
        self.browser.get("https://www.facebook.com/settings/?tab=language")
        buttons = WebDriverWait(self.browser, 8).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@role="listitem"]/div/div[2]/div/div/div')))
        time.sleep(2)
        language_button = buttons[0]
        self.browser.execute_script("arguments[0].click();", language_button)
        
        time.sleep(8)
        options = self.browser.find_elements(By.XPATH, "//span[contains(@id,'_r_')]")
        for option in options:
            if "english" in option.text.lower():
                self.browser.execute_script("arguments[0].click();", option)
                break

    def execute_scrap_process(self):
        self.browser.get(self.url_to_scrap)
        self.human_scroll()

    def scrap_links(self):
        elements = self.browser.find_elements(By.XPATH, '//div[@class="x3ct3a4"]')
        for element in elements:
            product_href = element.find_element(By.XPATH, 'a')
            product_id = product_href.get_attribute('href').split("/")[5]
            if product_id in self.checkpoint:
                continue
            self.links[product_id] = product_href.get_attribute('href')

    def human_key_input(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.2390, 0.3573))

    def human_scroll(self):
        total_scroll = 1
        recorded_heights = []
        while True:
            random_pixels = random.randint(600, 1300)
            random_wait = random.uniform(1,2.0)
            total_scroll += random_pixels
            # Scroll down to the bottom of the page to load all items.
            self.browser.execute_script(
                f"window.scrollTo(0, {total_scroll});")
            
            current_height = self.browser.execute_script("return document.body.scrollHeight")
            recorded_heights.append(current_height)
            
            if len(recorded_heights) > 5 and all(recorded_heights[-i] == recorded_heights[-i-1] for i in range(1, min(len(recorded_heights), 5))):
                print(f"INFO: No more items to load, starting the scrap of {len(self.links)} items.")
                break
            if len(self.links) >= self.threshold:
                break
            else:
                try:
                    self.scrap_links()
                except:
                    print("WARNING: No more links found or the page has changed during the scroll process.")
                    return

                time.sleep(random_wait)
    
    def scrap_images(self, publication_id, download_images = False):
        image_elements = self.browser.find_elements(By.XPATH, PRODUCT_IMAGE_XPATH)
        if not os.path.exists(f"{dir_path}/images/{publication_id}"):
            os.makedirs(f"{dir_path}/images/{publication_id}")
    
        image_counts = 0
        image_urls = []
        for image_element in image_elements:
            image_url = image_element.get_attribute("src")
            if "https://scontent" in image_url:
                if image_counts >= 3:
                    break
                
                if download_images:
                    r = requests.get(image_url, stream=True)
                    if r.status_code == 200:
                        with open(f"{dir_path}/images/{publication_id}/{publication_id}_{image_counts}.png", 'wb') as f:
                            for chunk in r:
                                f.write(chunk)

                image_urls.append(image_url)
                image_counts += 1

        return image_urls
                
    
    def scrap_publication_date(self):
        ### !!! WARNING: In testing this element has always been the last one in the list, but this may change.
        try:
            posted = self.browser.find_elements(By.XPATH, "//span[contains(text(), 'ago')]")[-1].text
        except:
            return "N/A"
        #about an hour ago

        if "about" in posted:
            numerical_time = 1
            time_period = posted.split(" ")[2]
        elif len(posted.split(" ")) == 3:
            try:
                numerical_time = int(posted.split(" ")[0])
                time_period = posted.split(" ")[1]
            except:
                numerical_time = 1
                time_period = posted.split(" ")[1]
        else:
            return "N/A"


        if "hour" in time_period:
            multiplier = 3600
        elif "minute" in time_period:
            multiplier = 60
        elif "day" in time_period:
            multiplier = 86400
        elif "week" in time_period:
            multiplier = 604800
        
        try:
            seconds_ago = numerical_time * multiplier
            publication_date = time.time() - seconds_ago
            publication_date = time.strftime("%Y-%m-%d", time.localtime(publication_date))
            return publication_date
        except Exception as e:
            return "N/A"


    def scrap_vehicle_info(self): 
        # Due to the format of the attribute 'style' in //i elements changing constantly, we need to iterate through all of them.
        page_i_elements = self.browser.find_elements(By.XPATH, """//i""")
        vehicle_info = {}
        
        for element in page_i_elements:
            try:
                style_attribute = element.get_attribute("style")
            except:
                continue
            if MILEAGE in style_attribute:
                parent_element = element.find_element(By.XPATH, "..")
                grandparent_element = parent_element.find_element(By.XPATH, "..")
                grandparent_element = grandparent_element.text.split("\n")[0].replace(" miles", "")
                grandparent_element = grandparent_element.split("\n")[0].replace(",", "")
                vehicle_info["mileage"] = int(grandparent_element.split("\n")[0].replace("Driven ", ""))
            
            elif INTERIOR_EXTERIOR_COLOR in style_attribute:
                parent_element = element.find_element(By.XPATH, "..")
                grandparent_element = parent_element.find_element(By.XPATH, "..")
                exterior_color = grandparent_element.text.split("\n")[0].split("·")[0].split(":")[-1]
                try:
                    interior_color = grandparent_element.text.split("\n")[0].split("·")[1].split(":")[-1]
                except:
                    interior_color = "N/A"
                
                vehicle_info["interior_color"] = interior_color.strip()
                vehicle_info["exterior_color"] = exterior_color.strip()
            elif FUEL_TYPE_AND_TRANSMISSION in style_attribute:
                style_text = element.find_element(By.XPATH, "../..").text
                if "transmission" in style_text:
                    vehicle_info["transmission"] = style_text.split("\n")[0].replace(" transmission ", "").strip()
                else:
                    vehicle_info["fuel_type"] = style_text.split("\n")[0].replace("Fuel type: ", "")
            elif CONSUMPTION in style_attribute:
                parent_element = element.find_element(By.XPATH, "..")
                grandparent_element = parent_element.find_element(By.XPATH, "..")
                city_consumption = float(grandparent_element.text.split("\n")[0].split("·")[0].replace(" MPG city", "").strip())
                highway_consumption = float(grandparent_element.text.split("\n")[0].split("·")[1].replace(" MPG highway", "").strip())
                vehicle_info["consumption"] = {"city": city_consumption, "highway": highway_consumption}
            
            elif OWNERS in style_attribute:
                style_text = element.find_element(By.XPATH, "../..").text
                if style_text != "":
                    vehicle_info["owners"] = style_text
            elif DEBT in style_attribute:
                parent_element = element.find_element(By.XPATH, "..")
                grandparent_element = parent_element.find_element(By.XPATH, "..")
                vehicle_info["debt"] = grandparent_element.text.split("\n")[0].strip()
            
            elif CLEAN_TITLE in style_attribute:
                vehicle_info["clean_title"] = True
            elif PAID_OFF in style_attribute:
                vehicle_info["misc"] = "Paid off"
            
            elif TITLE in style_attribute:
                parent_element = element.find_element(By.XPATH, "..")
                grandparent_element = parent_element.find_element(By.XPATH, "..")
                vehicle_info["title"] = grandparent_element.text.split("\n")[0].replace(" title", "").strip()
        
        return vehicle_info
    
    def scrap_seller_profile(self):
        profile_element = self.browser.find_element(By.XPATH, "//a[contains(@href, '/marketplace/profile')]")
        profile_href = profile_element.get_attribute("href")
        profile_id = profile_href.split("/")[5]
        self.browser.execute_script("arguments[0].click();", profile_element)
        time.sleep(2)
        car_makes_checks = 0
        listings = self.browser.find_elements(By.XPATH, "//a[contains(@href, '/?ref=marketplace_profile')]")
        for listing in listings:
            try:
                listing_text = listing.text.lower()
            except:
                break
            listing_words = listing_text.split(" ")
            for word in listing_words:
                if word in VEHICLE_MAKES:
                    car_makes_checks += 1
                    break

        
        if car_makes_checks > 1:
            is_dealership = True
        else:
            is_dealership = True
        

        try:
            lives_in = self.browser.find_element(By.XPATH, "//div[contains(text(), 'Lives in')]").text.replace("Lives in ", "").strip()
        except:
            lives_in = "N/A"

        try:
            joined_facebook_in = int(self.browser.find_element(By.XPATH, "//div[contains(text(), 'Joined Facebook in')]").text.replace("Joined Facebook in", "").strip())
        except:
            joined_facebook_in = "N/A"

        try:
            seller_name = self.browser.find_element(By.XPATH, '//span[@class="x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x14z4hjw x1x48ksl x579bpy xjkpybl x1xlr1w8 xzsf02u x1yc453h"]').text.split("\n")[0]
        except:
            seller_name = "N/A"
            
        return seller_name, is_dealership, profile_id, lives_in, joined_facebook_in, car_makes_checks
    
    def scrap_product_location(self):
        location_element = self.browser.find_element(By.XPATH, '//span[@style="--fontSize: 13px; --lineHeight: 18.166px;"]')
        return location_element.text
    
    def scrap_link(self, link):
        
        self.browser.get(link)
        
        publication_data = {}

        publication_id = link.split("/")[5]
        publication_date = self.scrap_publication_date()
        try:
            product_title = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, PRODUCT_TITLE_XPATH))).text.split("\n")[0]
        except:
            product_title = "N/A"
        try:
            product_price = int(self.browser.find_elements(By.XPATH, PRODUCT_PRICE_XPATH)[0].text.replace("$", "").replace(",", "").strip())
        except:
            product_price = 0
        try: # Some vehicles may have a short description, no need to click on "See more"
            see_more = self.browser.find_element(By.XPATH, "//*[contains(text(), 'See more')]")
            see_more.click()
        except Exception as e:
            None

        vehicle_info = self.scrap_vehicle_info()
        
        
        try: # Some vehicles may have no description
            publication_description = self.browser.find_elements(By.XPATH, PRODUCT_DESCRIPTION_XPATH)
            publication_description = publication_description[-1].text
        except:
            publication_description = "N/A"

        seller_name, is_dealership, profile_id, lives_in_element, joined_facebook_in, car_makes_checks = self.scrap_seller_profile()
        
        
        image_urls = self.scrap_images(publication_id)
        print(publication_id)


        profile_info = {
            "profile_id": int(profile_id),
            "profile_name": seller_name,
            "is_dealership": is_dealership,
            "lives_in": lives_in_element,
            "joined_facebook_in": joined_facebook_in,
            "car_listings":car_makes_checks
            }
        
        publication_info = {
            "publication_id": int(publication_id),
            "publication_date": publication_date,
            "product_title": product_title,
            "product_price": product_price,
            "publication_description": publication_description,
            "publication_link": f"https://www.facebook.com/marketplace/item/{publication_id}/",
            "images":image_urls
        }
        
        
        data = {
            "date": publication_date,
            "product_title": product_title,
            "product_price": product_price,
            "vehicle_info": vehicle_info,
            "publication_info": publication_info,
            "profile_info": profile_info,
        }

        
        
        return data
    
    def format_files(self):
        pass

if __name__ == "__main__":

    headless = True
    save_html = True
    


    with open(f"{dir_path}/input.csv", "r") as f:
        reader = csv.reader(f)
        lines = list(reader)

    if not os.path.exists(f"{dir_path}/publications"):
        os.makedirs(f"{dir_path}/publications")

    if not os.path.exists(f"{dir_path}/images"):
        os.makedirs(f"{dir_path}/images")  

    for line in lines:
        print(line)
        email, password, city_code, threshold, proxy, change_language = line
        
        threshold = int(threshold.strip())
        city_code = city_code.strip()
        email = email.strip()
        profile = email.split("@")[0]
        change_language = bool(change_language.capitalize())
        
        if not os.path.exists(f"{dir_path}/profiles/{profile}"):
            worker = fbm_scraper(city_code, profile, proxy, threshold, headless)
            print(f"INFO: Profile {profile} not logged, attempting a log in.")
            
            captcha = worker.log_in(email, password)
            if change_language:
                worker.change_language()
            if captcha:
                input(f"WARNING: Captcha detected for profile {profile}. Terminating.")
                sys.exit(0)
        else:
            worker = fbm_scraper(city_code, profile, proxy, threshold, headless)

        

        worker.execute_scrap_process()

        for product_id, link in worker.links.items():
            publication = worker.scrap_link(link)    
            with open(f"{dir_path}/publications/{product_id}.json", "w") as f:
                json.dump(publication, f, indent=4)
            if save_html:
                
                source = worker.browser.find_element(By.TAG_NAME, 'body')
                bs = BeautifulSoup(source.text, "lxml")
                for script in bs.find_all("script"):
                    script.decompose()
                with open(f"{dir_path}/publications/{product_id}.html", "w", encoding="utf-8") as f:
                    f.write(str(bs))
            time.sleep(0.5)