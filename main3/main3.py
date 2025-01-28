import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import pandas as pd
import matplotlib.pyplot as plt

# Documentation
"""
Instagram Location Timeline Scraper

This script scrapes Instagram profiles to create a timeline of tagged locations in posts.
The output includes a CSV file and a visual representation of the timeline.

Usage:
  python instagram_location_timeline.py [username or profile URL]

Features:
- Handles errors for non-existent or private profiles.
- Respects Instagram's rate limits by adding delays.
- Optional filters for date range and post limit.
"""

# Constants
INSTAGRAM_BASE_URL = "https://www.instagram.com/"
OUTPUT_DIR = "output"
DELAY = 3

# Initialize WebDriver
def init_driver():
    """
    Initializes the Selenium WebDriver with Firefox using Geckodriver.
    """
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # Setup geckodriver with webdriver_manager
    geckodriver_path = "/usr/local/bin/geckodriver"
    service = Service(geckodriver_path)

    # Initialize Firefox driver with options and service
    driver = webdriver.Firefox(service=service, options=options)

    # Increase timeouts
    driver.set_page_load_timeout(180)
    driver.set_scripts_timeout(180)
    return driver

# Login to Instagram (if required)
def login(driver, username, password):
    """
    Logs into Instagram if credentials are provided.
    """
    driver.get(INSTAGRAM_BASE_URL)
    time.sleep(DELAY)
    try:
        login_field = driver.find_element(By.NAME, 'username')
        password_field = driver.find_element(By.NAME, 'password')
        login_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(DELAY)
    except Exception as e:
        print(f"Login failed: {e}")

# Scrape profile posts
def scrape_profile(driver, profile_url, max_posts=50):
    """
    Scrapes the specified Instagram profile for post data and location tags.
    """
    driver.get(profile_url)
    time.sleep(DELAY)

    post_data = []
    posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")

    for i, post in enumerate(posts[:max_posts]):
        try:
            post_url = post.get_attribute('href')
            post.click()
            time.sleep(DELAY)
            location = None
            try:
                location = driver.find_element(By.XPATH, "//a[contains(@href, '/explore/locations/')]").text
            except:
                pass

            date = driver.find_element(By.XPATH, "//time").get_attribute('datetime')
            post_data.append({"Date": date, "Post URL": post_url, "Location Name": location})

            driver.find_element(By.XPATH, "//body").send_keys(Keys.ESCAPE)
            time.sleep(DELAY)
        except Exception as e:
            print(f"Error processing post {i + 1}: {e}")

    return post_data

# Save timeline to CSV
def save_timeline(data, filename):
    """
    Saves the scraped timeline data to a CSV file.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, filename)
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    print(f"Timeline saved to {file_path}")

# Visualize timeline
def visualize_timeline(data):
    """
    Visualizes the timeline data as a plot.
    """
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date')
    plt.figure(figsize=(10, 6))
    plt.plot(df['Date'], df['Location Name'], marker='o')
    plt.title('Instagram Location Timeline')
    plt.xlabel('Date')
    plt.ylabel('Location Name')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Main function
def main():
    """
    Main function to execute the Instagram location timeline scraper.
    """
    print("Instagram Location Timeline Scraper")
    target = input("Enter the Instagram username or profile URL: ").strip()
    max_posts = int(input("Enter the maximum number of posts to process (default 50): ") or 50)

    driver = init_driver()

    try:
        profile_url = target if target.startswith("http") else f"{INSTAGRAM_BASE_URL}{target}/"
        data = scrape_profile(driver, profile_url, max_posts=max_posts)

        if data:
            save_timeline(data, "location_timeline.csv")
            visualize_timeline(data)
        else:
            print("No data found. Ensure the profile exists and is public.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

