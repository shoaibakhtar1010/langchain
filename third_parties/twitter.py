import os
from typing import List, Dict
from dotenv import load_dotenv
import tweepy
import requests

load_dotenv()

# Constants
MOCK_TWEETS_URL = (
    "https://gist.githubusercontent.com/emarco177/827323bb599553d0f0e662da07b9ff68/"
    "raw/57bf38cf8acce0c87e060f9bb51f6ab72098fbd6/eden-marco-twitter.json"
)

# Initialize Twitter Client
try:
    twitter_client = tweepy.Client(
        bearer_token=os.environ["TWITTER_BEARER_TOKEN"],
        consumer_key=os.environ["TWITTER_API_KEY"],
        consumer_secret=os.environ["TWITTER_API_KEY_SECRET"],
        access_token=os.environ["TWITTER_ACCESS_TOKEN"],
        access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
    )
except KeyError as e:
    raise ValueError(f"Missing required environment variable: {e}")

def scrape_user_tweets(username: str, num_tweets: int = 5, mock: bool = False) -> List[Dict[str, str]]:
    """
    Scrapes a Twitter user's original tweets (i.e., not retweets or replies).

    Args:
        username (str): The Twitter username to scrape.
        num_tweets (int): Number of tweets to fetch. Defaults to 5.
        mock (bool): If True, uses mock data instead of real API calls. Defaults to False.

    Returns:
        List[Dict[str, str]]: A list of dictionaries with tweet details (text, url).

    Raises:
        ValueError: If the username is invalid or no tweets are found.
        Exception: For API or network-related issues.
    """
    if not username.strip():
        raise ValueError("The username parameter cannot be empty or whitespace.")

    try:
        if mock:
            response = requests.get(MOCK_TWEETS_URL, timeout=5)
            response.raise_for_status()
            tweets = response.json()
        else:
            user = twitter_client.get_user(username=username)
            if not user.data:
                raise ValueError(f"No user found with username: {username}")
            
            user_id = user.data.id
            tweets_response = twitter_client.get_users_tweets(
                id=user_id, max_results=num_tweets, exclude=["retweets", "replies"]
            )
            if not tweets_response.data:
                raise ValueError(f"No tweets found for user: {username}")

            tweets = tweets_response.data

        # Process tweets into the desired format
        return [
            {
                "text": tweet["text"],
                "url": f"https://twitter.com/{username}/status/{tweet['id']}",
            }
            for tweet in tweets
        ]

    except requests.RequestException as e:
        raise RuntimeError(f"Error during mock request: {e}")
    except tweepy.TweepyException as e:
        raise RuntimeError(f"Error during Twitter API call: {e}")


if __name__ == "__main__":
    try:
        tweets = scrape_user_tweets(username="EdenEmarco177", mock=True)
        print(tweets)
    except Exception as e:
        print(f"An error occurred: {e}")
