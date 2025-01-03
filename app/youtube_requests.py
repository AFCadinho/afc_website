import requests
from app.config import Config

API_KEY = Config.YOUTUBE_API_KEY
CHANNEL_ID = Config.YOUTUBE_CHANNEL_ID
YOUTUBE_API_URL = 'https://www.googleapis.com/youtube/v3/search'


def get_latest_video():
    params = {
        'part': 'snippet',
        'channelId': CHANNEL_ID,
        'order': 'date',
        'maxResults': 1,
        'type': 'video',
        'key': API_KEY
    }
    
    response = requests.get(YOUTUBE_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            video_id = data['items'][0]['id']['videoId']
            video_title = data['items'][0]['snippet']['title']
            video_url = f"https://www.youtube.com/embed/{video_id}"
            print(f"Returning: {video_url} and {video_title}")
            return video_url, video_title
    return None, None


