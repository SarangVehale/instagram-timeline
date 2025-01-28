import instaloader
import pandas as pd
import re
import time
import requests

def get_instagram_username_from_url(profile_url):
    """
    This function extracts the username from the provided Instagram profile URL.
    """
    # Regex to extract the username from the URL
    match = re.search(r'https?://(?:www\.)?instagram\.com/([^/]+)/?', profile_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Instagram profile URL")

def get_instagram_data(username, loader):
    """
    This function scrapes the Instagram profile for the given username and retrieves
    the post date, URL, location, latitude, and longitude (if available).
    """
    profile = instaloader.Profile.from_username(loader.context, username)

    posts_data = []

    for post in profile.get_posts():
        try:
            post_date = post.date_utc  # Post timestamp
            post_url = f"https://www.instagram.com/p/{post.shortcode}/"  # URL to the post

            # Extracting location data (if available)
            location_name = post.location.name if post.location else None
            latitude = post.location.latitude if post.location else None
            longitude = post.location.longitude if post.location else None

            # If location details are missing, fetch from Instagram API
            if not location_name or not latitude or not longitude:
                location_name, latitude, longitude = get_location_data_from_api(post_url)

            # Add post data to the list
            posts_data.append({
                "date": post_date,
                "url": post_url,
                "location_name": location_name,
                "latitude": latitude,
                "longitude": longitude
            })
        except Exception as e:
            print(f"Error processing post {post.shortcode}: {e}")
            continue

    return posts_data

def get_location_data_from_api(post_url):
    """
    This function fetches location data (name, latitude, longitude) from the Instagram API
    for a given post URL.
    """
    try:
        # Extract shortcode from the URL and make a request to Instagram's post API
        shortcode = post_url.split('/')[-2]
        api_url = f"https://www.instagram.com/p/{shortcode}/?__a=1"
        response = requests.get(api_url)
        post_data = response.json()

        # Extract location information
        location_data = post_data['graphql']['shortcode_media'].get('location', None)

        if location_data:
            location_name = location_data.get('name', 'Unknown')
            latitude = location_data.get('lat', 'Unknown')
            longitude = location_data.get('lng', 'Unknown')
            return location_name, latitude, longitude
        else:
            return 'Unknown', 'Unknown', 'Unknown'
    except Exception as e:
        print(f"Error fetching location data for {post_url}: {e}")
        return 'Unknown', 'Unknown', 'Unknown'

def save_to_csv(posts_data, filename="location_timeline.csv"):
    """
    This function saves the scraped posts data to a CSV file.
    """
    df = pd.DataFrame(posts_data)
    df.to_csv(filename, index=False)

def main():
    """
    Main function to prompt for Instagram profile URL, scrape posts data,
    and save the results to a CSV file.
    """
    profile_url = input("Enter Instagram profile URL: ").strip()

    # Login to Instagram using your credentials
    username = input("Enter your Instagram username: ").strip()
    password = input("Enter your Instagram password: ").strip()

    loader = instaloader.Instaloader()

    try:
        # Login to Instagram (this session will be used for scraping)
        loader.context.log("Logging in...")
        loader.load_session_from_file(username)  # Attempt to load session if exists
        loader.context.log("Login session loaded.")
    except FileNotFoundError:
        loader.context.log("Session file not found. Logging in with credentials.")
        loader.context.log("Logging in...")
        try:
            loader.login(username, password)  # Login with username and password
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            print("Two-factor authentication is required.")
            # Handle the 2FA process
            while True:
                code = input("Enter the 2FA code sent to your device: ").strip()
                try:
                    loader.two_factor_login(code)  # Attempt 2FA login
                    print("Logged in successfully with 2FA!")
                    break  # Exit the loop after successful login
                except instaloader.exceptions.BadCredentialsException:
                    print("Incorrect 2FA code. Please try again.")
                    time.sleep(2)  # Wait a bit before retrying
        loader.save_session_to_file()  # Save the session for future use

    try:
        # Extract the username from the profile URL
        username_from_url = get_instagram_username_from_url(profile_url)

        # Scrape Instagram profile data
        posts_data = get_instagram_data(username_from_url, loader)

        # Check if any posts were found
        if not posts_data:
            print(f"No posts found for {username_from_url}.")
            return

        # Save the scraped data to CSV
        save_to_csv(posts_data)

        # Print a success message
        print(f"Location timeline saved to 'location_timeline.csv'.")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

