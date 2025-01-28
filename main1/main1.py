from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize Selenium WebDriver
def init_driver():
    service = Service("/usr/bin/chromedriver")  # Ensure this is the correct chromedriver path
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Scrape location tags from Instagram posts
def scrape_location_tags(profile_url, max_posts=10):
    driver = init_driver()
    driver.get(profile_url)
    time.sleep(5)  # Increased initial wait to give time for page to load

    locations = []

    # Wait until the first post thumbnail is visible (increase timeout)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "v1Nh3")))  # Increased wait time to 30 seconds

    # Scroll down using JavaScript for more posts
    for _ in range(5):  # Scroll five times to load more posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for posts to load after scrolling

    # Debug: Print the page source after scrolling
    page_source = driver.page_source
    print("Page Source Loaded. Checking for posts...")

    # Extract post thumbnails
    posts = driver.find_elements(By.CLASS_NAME, "v1Nh3")
    print(f"Found {len(posts)} posts.")  # Log number of posts found

    if len(posts) == 0:
        print("No posts found. Page might not have loaded properly.")

    for i, post in enumerate(posts[:max_posts]):
        try:
            ActionChains(driver).move_to_element(post).click().perform()
            time.sleep(2)  # Wait for the post to load

            # Try to locate the location using a more specific XPath
            location_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/explore/locations/')]")
            if location_elements:
                location = location_elements[0].text  # Extract the location text
                print(f"Post {i + 1}: Found location: {location}")  # Log the location found
                locations.append(location)
            else:
                print(f"Post {i + 1}: No location tag found.")  # Log that no location tag is present

        except Exception as e:
            print(f"Error processing post {i + 1}: {str(e)}")

        # Close the post overlay
        try:
            close_button = driver.find_element(By.CSS_SELECTOR, "button.ckWGn")
            close_button.click()
            time.sleep(1)
        except:
            print("No close button found for post overlay.")

    driver.quit()
    return locations

# Main function
if __name__ == "__main__":
    profile_url = "https://www.instagram.com/sharmashresth?igsh=aTk0ZjE5NHFxZTFx"  # Replace with the profile URL
    max_posts = 5  # Limit number of posts to scrape
    print("Scraping location tags...")
    locations = scrape_location_tags(profile_url, max_posts)
    if locations:
        print("Locations extracted:")
        for loc in locations:
            print(loc)
    else:
        print("No location tags found.")

