import os
import time
import tweepy
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.search import search_memes
from dotenv import load_dotenv

load_dotenv()

class BrahmiBot:
    def __init__(self):
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            print("Twitter Bot credentials missing. Bot will dry-run only.")
            self.client = None
        else:
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret,
                wait_on_rate_limit=True
            )
            
        self.bot_user_id = os.getenv("TWITTER_BOT_USER_ID") # Needed for fetching mentions easily

    def get_best_meme_reply(self, tweet_text: str, db: Session) -> str:
        """
        Uses the RAG search pipeline to find the most appropriate meme for the incoming tweet.
        """
        # Clean the tweet (remove mentions, etc)
        # Assuming the query is the remaining text
        query = " ".join([word for word in tweet_text.split() if not word.startswith('@')])
        
        # If no real text, default to a generic confused or waiting brahmi reaction
        if len(query) < 2:
            query = "confused staring"
            
        results = search_memes(db, query, limit=1)
        
        if not results:
            return "Em chepparu sir... ardam kaale! (No suitable meme found for this context)"
            
        selected_meme = results[0]
        
        # We need the public URL representation
        public_url = f"https://your-public-r2-domain.com/{selected_meme.r2_key}"
        
        caption = selected_meme.text_caption if selected_meme.text_caption else ""
        return f"{caption}\n\n{public_url}"

    def poll_mentions(self, interval_seconds=60):
        """
        Simple polling mechanism to reply to new mentions.
        In production, a webhook (Account Activity API) is vastly superior and fully asynchronous.
        """
        if not self.client or not self.bot_user_id:
            print("Cannot poll without valid auth/bot ID.")
            return
            
        print("Bot started polling for mentions...")
        last_id = None # In production, store this in DB or Redis
        
        while True:
            try:
                mentions = self.client.get_users_mentions(
                    id=self.bot_user_id,
                    since_id=last_id,
                    max_results=5 # Keep it low for free tier polling
                )
                
                if mentions.data:
                    for mention in reversed(mentions.data):
                        last_id = mention.id # Update marker
                        print(f"Replying to {mention.id}: {mention.text}")
                        
                        db = SessionLocal()
                        try:
                            # Generate the perfect reply
                            reply_text = self.get_best_meme_reply(mention.text, db)
                            
                            # Reply to the tweet
                            self.client.create_tweet(
                                text=reply_text,
                                in_reply_to_tweet_id=mention.id
                            )
                        finally:
                            db.close()
                
                time.sleep(interval_seconds)
            except tweepy.TooManyRequests:
                print("Rate limit hit. Waiting 15 minutes...")
                time.sleep(15 * 60)
            except Exception as e:
                print(f"Error during polling: {e}")
                time.sleep(interval_seconds)

if __name__ == "__main__":
    bot = BrahmiBot()
    # bot.poll_mentions()
