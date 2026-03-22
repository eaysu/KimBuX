import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "")
TWITTER_EMAIL = os.getenv("TWITTER_EMAIL", "")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"

DATABASE_URL = os.getenv("DATABASE_URL", "")

COOKIES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookies.json")

MAX_TWEETS = 1000
TWEET_LIMITS = [100, 500, 1000]

ACTIVE_ACCOUNT_DAILY_TWEETS = 3
ACTIVE_ACCOUNT_TTL_DAYS = 15
INACTIVE_ACCOUNT_TTL_DAYS = 30

RECENT_TOP_LIKED_DAYS = 30

GPT_BATCH_SIZE = 50

ANALYSIS_VERSION = "v1"
