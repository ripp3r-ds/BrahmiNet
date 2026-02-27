import os
import requests
import tweepy
import instaloader
from typing import List

class TenorAPI:
    def __init__(self):
        self.api_key = os.getenv("TENOR_API_KEY")
        self.client_key = "brahminet_agent"

    def fetch_gifs(self, query: str = "brahmanandam", limit: int = 20) -> List[str]:
        if not self.api_key:
            return []
        url = f"https://tenor.googleapis.com/v2/search?q={query}&key={self.api_key}&client_key={self.client_key}&limit={limit}"
        try:
            r = requests.get(url)
            r.raise_for_status()
            results = r.json().get("results", [])
            urls = []
            for item in results:
                # Extract the highest quality static or gif URL
                media = item.get("media_formats", {})
                if "gif" in media:
                    urls.append(media["gif"]["url"])
                elif "tinygif" in media:
                    urls.append(media["tinygif"]["url"])
            return urls
        except Exception as e:
            print(f"Tenor API error: {e}")
            return []

class TwitterScraper:
    def __init__(self):
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.client = tweepy.Client(bearer_token=bearer_token) if bearer_token else None

    def fetch_recent_memes(self, query: str = "brahmanandam meme has:images", max_results=20) -> List[str]:
        if not self.client:
            return []
        try:
            response = self.client.search_recent_tweets(query=query, media_fields=["url"], expansions=["attachments.media_keys"], max_results=max_results)
            urls = []
            if response.includes and "media" in response.includes:
                for media in response.includes["media"]:
                    if media.type in ["photo", "animated_gif"] and media.url:
                        urls.append(media.url)
            return urls
        except Exception as e:
            print(f"Twitter Scraping error: {e}")
            return []

class InstagramScraper:
    def __init__(self):
        self.L = instaloader.Instaloader(download_videos=False, save_metadata=False, post_metadata_txt_pattern="")
        
    def fetch_hashtag_posts(self, hashtag: str = "brahmanandam", max_count: int = 10) -> List[str]:
        urls = []
        try:
            posts = instaloader.NodeIterator(self.L.context, "9b498c08113f1e09617a1703c22b2f32", lambda d: d['data']['hashtag']['edge_hashtag_to_media'], lambda n: instaloader.Post(self.L.context, n), {'tag_name': hashtag}, f"https://www.instagram.com/explore/tags/{hashtag}/")
            for i, post in enumerate(posts):
                if i >= max_count:
                    break
                urls.append(post.url)
        except Exception as e:
            print(f"Instagram scraping error: {e}")
        return urls
