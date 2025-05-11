from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import random

def setup_driver():
    chrome_options = Options()
   # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36')
    
    service = Service(r'chromedriver.exe')  
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver



def extract_listings(driver, keyword):
    """Extract product listings from DoneDeal search results (no click-in)."""
    listings = []

    try:
        # Go to DoneDeal homepage
        driver.get("https://www.donedeal.ie")
        
        # Find and interact with the search box
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
        )
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.submit()

        # Wait for the search results container to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul[data-testid='card-list']"))
        )

        print("Scraping search result listings...")

        # Get all listings on current page
        listing_elements = driver.find_elements(By.CSS_SELECTOR, "ul[data-testid='card-list'] li a")

        for element in listing_elements:
            try:
                # Safe title extraction
                try:
                    title = element.find_element(By.CSS_SELECTOR, "p[class*='Title']").text
                except NoSuchElementException:
                    title = "N/A"

                # Safe price extraction
                try:
                    price = element.find_element(By.CSS_SELECTOR, "div[class*='Price']").text
                except NoSuchElementException:
                    price = "N/A"

                # Safe location extraction
                meta_items = element.find_elements(By.CSS_SELECTOR, "li[class*='MetaInfoItem']")
                location = meta_items[1].text if len(meta_items) > 1 else "N/A"

                # Safe link extraction
                link = element.get_attribute("href")
                full_link = f"https://www.donedeal.ie{link}" if link and link.startswith("/") else link or "N/A"

                # Save the extracted data
                listings.append({
                    "title": title,
                    "price": price,
                    "location": location,
                    "url": full_link
                })

            except Exception as e:
                print(f"❌ Failed to parse one listing: {e}")
                continue

    except TimeoutException:
        print("⏰ Timeout waiting for elements to load")
    except Exception as e:
        print(f"❌ General error in extract_listings: {e}")

    return listings



def main():
    driver = setup_driver()
       
  # Search keyword - can be modified as needed
    keyword = "Iphone"
        
    # Extract listings
    print(f"Searching for '{keyword}' on DoneDeal...")
    listings = extract_listings(driver, keyword)
    if listings:
        df = pd.DataFrame(listings)
        df.to_csv("donedeal_results.csv", index=False)
        print(f"✅ Saved {len(listings)} listings to donedeal_results.csv")
    else:
        print("⚠️ No listings found.")

if __name__ == "__main__":
    main() 