import asyncio
import os
import logging
import requests
import time
from typing import Optional

import tweepy
import tweepy.asynchronous
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


STOP_AFTER_ATTEMPTS: int = 3
WAIT_MULTIPLIER: int = 1
WAIT_MIN: int = 2
WAIT_MAX: int = 10
MAX_CONCURRENT_REQUESTS: int = 5

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TwitterClient:
    """A client for interacting with the Twitter API, allowing users to like tweets.

    This client handles authentication, rate limiting, caching, and error handling while liking tweets.
    A semaphore is used to manage concurrent requests, preventing API rate limits from being exceeded.
    """

    liked_tweets: set[int] = set()  # simple cache for liked tweets

    def __init__(self) -> None:
        """Initializes the Twitter client, loads API keys from environment variables, and authenticates the user."""
        load_dotenv()
        self.consumer_key: Optional[str] = os.getenv("CONSUMER_KEY")
        self.consumer_secret: Optional[str] = os.getenv("CONSUMER_SECRET")
        self.access_token: Optional[str] = os.getenv("ACCESS_TOKEN")
        self.access_token_secret: Optional[str] = os.getenv("ACCESS_TOKEN_SECRET")
        self.client: tweepy.asynchronous.AsyncClient = self.authenticate()
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    def authenticate(self) -> tweepy.asynchronous.AsyncClient:
        """Authenticates the user with Twitter API using OAuth 1.0a User Context.

        Returns:
            tweepy.asynchronous.AsyncClient: An authenticated Twitter API client.
        """
        try:
            client: tweepy.asynchronous.AsyncClient = tweepy.asynchronous.AsyncClient(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
            )
            logging.info("Authentication successful.")
            return client
        except Exception:
            logging.exception("Failed to authenticate with Twitter API.")
            raise

    @retry(
        stop=stop_after_attempt(STOP_AFTER_ATTEMPTS),
        wait=wait_exponential(multiplier=WAIT_MULTIPLIER, min=WAIT_MIN, max=WAIT_MAX),
        retry=retry_if_exception_type(tweepy.TwitterServerError),
        reraise=True,
    )
    async def like_tweet(self, tweet_id: int) -> None:
        """Likes a tweet specified by its tweet ID, ensuring rate limits are respected.

        This method includes:
        - Caching of liked tweets to avoid redundant API calls.
        - Automatic retrying on Twitter server errors.
        - Use of an asyncio semaphore to limit concurrent API requests.

        Args:
            tweet_id (int): The ID of the tweet to like.
        """
        async with self.semaphore:
            if tweet_id in TwitterClient.liked_tweets:
                logging.info("Tweet %s is already liked. Skipping.", tweet_id)
                return

            try:
                response: tweepy.Response = await self.client.like(tweet_id=tweet_id)
                if response.errors:
                    logging.error(
                        "Failed to like tweet %s: %s", tweet_id, response.errors
                    )
                else:
                    logging.info("Successfully liked tweet %s.", tweet_id)
                    TwitterClient.liked_tweets.add(tweet_id)
            except tweepy.TooManyRequests as e:
                response: requests.Response = e.response
                reset_time: int = int(response.headers["x-rate-limit-reset"])
                wait_time: int = reset_time - int(time.time())
                logging.warning("Rate limit exceeded. Retry in %s seconds.", wait_time)
            except tweepy.TwitterServerError:
                logging.exception("Twitter API error occurred.")
                raise
            except Exception:
                logging.exception(
                    "An unexpected error occurred while liking the tweet."
                )
                raise


if __name__ == "__main__":
    twitter_client: TwitterClient = TwitterClient()
    tweet_id_input: str = input("Enter the tweet ID to like: ")
    tweet_id: int = int(tweet_id_input)
    asyncio.run(twitter_client.like_tweet(tweet_id))
