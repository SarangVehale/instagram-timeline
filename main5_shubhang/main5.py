import instaloader
import csv
from datetime import datetime

# Initialize Instaloader
L = instaloader.Instaloader(
    download_videos=True,  # Download videos if available
    download_comments=False,  # Disable downloading comments to save time
    save_metadata=True  # Enable saving metadata
)

def download_public_profile(username):
    """
    Download media from a public Instagram profile.

    Parameters:
        username (str): The Instagram username to download.
    """
    try:
        print(f"Downloading public profile: {username}")
        L.download_profile(
            username,
            profile_pic=True,  # Download profile picture
            fast_update=True,  # Skip already-downloaded posts
            download_stories=False,  # Skip downloading stories
            download_tagged=False  # Skip downloading tagged posts
        )
        print(f"Profile {username} downloaded successfully.")
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"The profile {username} does not exist or is private.")
    except Exception as e:
        print(f"An error occurred: {e}")

def list_public_posts(username, filename):
    """
    List posts from a public Instagram profile and save them to a CSV file.

    Parameters:
        username (str): The Instagram username.
        filename (str): The name of the CSV file to save the output.
    """
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        print(f"Fetching posts for public profile: {username}\n")

        # Prepare CSV file to save the output
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Post Number', 'Post ID', 'Date', 'Time', 'Location', 'Hashtags', 'Description', 'Post Type', 'URL'])

            post_number = 1
            for post in profile.get_posts():
                # Format the date and time
                post_date = post.date_utc.strftime('%d/%m/%Y')  # Date in dd/mm/yyyy format
                post_time = post.date_utc.strftime('%H:%M:%S')  # Time in 00:00:00 format

                # Extract location
                if post.location:
                    location_name = post.location.name if hasattr(post.location, 'name') else 'N/A'
                else:
                    location_name = 'N/A'

                # Extract hashtags (if any)
                hashtags = ', '.join(post.caption_hashtags) if post.caption_hashtags else 'N/A'

                # Post description (caption)
                description = post.caption if post.caption else 'N/A'

                # Post type (media type)
                post_type = post.typename  # This could be "GraphImage", "GraphSidecar", etc.

                # Write data to CSV
                writer.writerow([
                    post_number,
                    post.mediaid,
                    post_date,
                    post_time,
                    location_name,
                    hashtags,
                    description,
                    post_type,
                    post.url
                ])

                # Debugging output
                print(f"Post Number: {post_number}")
                print(f"Post ID: {post.mediaid}")
                print(f"Date: {post_date}")
                print(f"Time: {post_time}")
                print(f"Location: {location_name}")
                print(f"Hashtags: {hashtags}")
                print(f"Description: {description}")
                print(f"Post Type: {post_type}")
                print(f"URL: {post.url}")
                print("\n")

                post_number += 1

        print(f"Post details saved to {filename}.")
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"The profile {username} does not exist or is private.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Get Instagram username from user input
    username = input("Enter the Instagram username: ")

    # File name will be the username with .csv extension
    filename = f"{username}.csv"

    # Download the public profile and its media
    download_public_profile(username)

    # List public posts and save them to CSV
    list_public_posts(username, filename)

if __name__ == "__main__":
    main()

