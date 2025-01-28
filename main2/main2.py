import requests
from datetime import datetime

def get_instagram_location_timeline(user_id, access_token):
    """
    Fetches location-based timeline of Instagram posts using Instagram Graph API.
    
    Args:
        user_id (str): The Instagram User ID.
        access_token (str): The Instagram Graph API access token.
    
    Returns:
        list: A list of dictionaries with locations and timestamps of the posts.
    """
    url = f"https://graph.instagram.com/{user_id}/media"
    params = {
        'fields': 'id,caption,location,timestamp',
        'access_token': access_token
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        return []

    # Extract location timeline from the posts
    posts = response.json().get('data', [])
    location_timeline = []

    for post in posts:
        location = post.get('location')
        timestamp = post.get('timestamp')

        if location:
            location_timeline.append({
                'location': location['name'],
                'timestamp': datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            })

    return location_timeline


if __name__ == "__main__":
    user_id = input("Enter the Instagram User ID: ")
    access_token = input("Enter your Instagram Graph API Access Token: ")

    timeline = get_instagram_location_timeline(user_id, access_token)
    
    if timeline:
        print(f"Location timeline for user {user_id}:")
        for entry in timeline:
            print(f"Location: {entry['location']}, Timestamp: {entry['timestamp']}")
    else:
        print(f"No location data found for user {user_id}.")

