import os
import re
import json
import base64
import asyncio
import random
from twikit import Client
from src.config import (
    TWITTER_USERNAME, TWITTER_EMAIL, TWITTER_PASSWORD,
    COOKIES_PATH, MAX_TWEETS
)


class TwitterClient:
    """Twikit wrapper for fetching profiles and tweets."""

    def __init__(self):
        self.client = Client("en-US")
        self._user_cache: dict[str, object] = {}

    async def login(self):
        """Login using saved cookies or credentials."""
        # Try environment variable first (for production/Render)
        cookies_b64 = os.getenv("TWITTER_COOKIES_BASE64")
        if cookies_b64:
            try:
                cookies_json = base64.b64decode(cookies_b64).decode("utf-8")
                cookies_dict = json.loads(cookies_json)
                self.client.set_cookies(cookies_dict)
                print(f"✓ Loaded cookies from TWITTER_COOKIES_BASE64 env var")
                return
            except Exception as e:
                print(f"✗ Failed to load cookies from env var: {e}")
                pass  # Fall through to file-based or login
        
        # Try local cookies file
        if os.path.exists(COOKIES_PATH):
            self.client.load_cookies(COOKIES_PATH)
        else:
            # Login and save cookies locally
            await self.client.login(
                auth_info_1=TWITTER_USERNAME,
                auth_info_2=TWITTER_EMAIL,
                password=TWITTER_PASSWORD
            )
            self.client.save_cookies(COOKIES_PATH)

    async def get_profile(self, username: str) -> dict:
        """Fetch user profile info. Raises on not found / protected."""
        # Fetch raw GraphQL data to get birthdate
        try:
            response, _ = await self.client.gql.user_by_screen_name(username)
        except Exception as e:
            raise Exception(f"User @{username} not found") from e

        user_obj = response.get('data', {}).get('user')
        if not user_obj or not user_obj.get('result'):
            raise Exception(f"User @{username} not found")

        user_data = user_obj['result']
        if user_data.get('__typename') == 'UserUnavailable':
            raise Exception(f"User @{username} not found")

        from twikit import User
        user = User(self.client, user_data)

        # Extract birthdate from legacy_extended_profile
        born = ""
        ext_profile = user_data.get("legacy_extended_profile", {})
        bd = ext_profile.get("birthdate", {})
        if bd:
            month_names_tr = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                              "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
            day = bd.get("day")
            month = bd.get("month")
            year = bd.get("year")
            if day and month:
                born = f"{day} {month_names_tr[month]}"
                if year:
                    born += f" {year}"

        # Fallback: parse birthdate from bio text
        if not born:
            bio_text = (user.description if hasattr(user, "description") else "") or ""
            born = self._parse_born_from_bio(bio_text)

        return {
            "id": user.id,
            "username": user.screen_name,
            "display_name": user.name,
            "bio": user.description if hasattr(user, "description") else "",
            "location": getattr(user, "location", ""),
            "born": born,
            "followers_count": user.followers_count if hasattr(user, "followers_count") else 0,
            "following_count": user.friends_count if hasattr(user, "friends_count") else (user.following_count if hasattr(user, "following_count") else 0),
            "tweet_count": user.statuses_count if hasattr(user, "statuses_count") else (user.tweets_count if hasattr(user, "tweets_count") else 0),
            "created_at": user.created_at if hasattr(user, "created_at") else None,
            "protected": user.is_protected if hasattr(user, "is_protected") else False,
            "profile_image_url": user.profile_image_url if hasattr(user, "profile_image_url") else "",
        }

    async def get_tweets(self, username: str, limit: int = 100) -> list[dict]:
        """
        Fetch up to `limit` latest tweets (original + quote only).
        Replies and retweets are excluded.
        Returns list of tweet dicts with needed fields.
        """
        limit = min(limit, MAX_TWEETS)
        user = await self.client.get_user_by_screen_name(username)
        self._user_cache[username.lower()] = user

        tweets_raw = []
        tweet_type = "Tweets"  # latest tweets (no replies tab)

        # Fetch initial batch
        batch = await user.get_tweets(tweet_type, count=min(40, limit))
        if not batch:
            return tweets_raw

        # Process initial batch
        for tweet in batch:
            if self._is_eligible(tweet):
                tweets_raw.append(self._extract(tweet, username))
                if len(tweets_raw) >= limit:
                    return tweets_raw

        # Fetch more batches with humanized delays
        consecutive_errors = 0
        empty_batches = 0
        while len(tweets_raw) < limit:
            # Random delay to mimic human browsing (3-6 seconds)
            await asyncio.sleep(random.uniform(3.0, 6.0))

            try:
                batch = await batch.next()
                if not batch:
                    empty_batches += 1
                    if empty_batches >= 2:
                        break
                    continue
                empty_batches = 0
                consecutive_errors = 0
            except Exception as e:
                error_str = str(e).lower()
                if ("rate" in error_str or "429" in error_str) and consecutive_errors < 3:
                    consecutive_errors += 1
                    # Wait longer on rate limit, then retry
                    wait = random.uniform(20.0, 40.0) * consecutive_errors
                    await asyncio.sleep(wait)
                    continue
                break

            for tweet in batch:
                if self._is_eligible(tweet):
                    tweets_raw.append(self._extract(tweet, username))
                    if len(tweets_raw) >= limit:
                        break

        return tweets_raw

    async def get_replies(self, username: str, max_tweets: int = 150) -> list[dict]:
        """
        Fetch reply tweets from the Replies tab to detect bestfriend.
        For each reply tweet, records who it is replying TO (one entry per tweet).
        Uses in_reply_to or first @mention in text.
        Returns list of dicts: [{"reply_to": "username"}, ...]
        """
        import re
        user = self._user_cache.get(username.lower())
        if not user:
            try:
                user = await self.client.get_user_by_screen_name(username)
            except Exception:
                return []

        replies_data = []
        uname_lower = username.lower()

        def _extract_reply_target(tweet) -> str | None:
            """Get the username this tweet is replying to."""
            # 1) Use in_reply_to if available (twikit User object)
            reply_to = getattr(tweet, "in_reply_to", None)
            if reply_to:
                # in_reply_to may be a user id or screen_name depending on twikit version
                screen = getattr(reply_to, "screen_name", None) or getattr(reply_to, "name", None)
                if screen and screen.lower() != uname_lower:
                    return screen.lower()
            # 2) Fallback: first @mention in tweet text that isn't the user themselves
            text = getattr(tweet, "full_text", None) or getattr(tweet, "text", "") or ""
            mentions = re.findall(r"@(\w+)", text)
            for m in mentions:
                if m.lower() != uname_lower:
                    return m.lower()
            return None

        try:
            # Wait before fetching replies to avoid rate limit
            await asyncio.sleep(random.uniform(8.0, 15.0))
            batch = await user.get_tweets("Replies", count=40)
            if not batch:
                return replies_data
        except Exception:
            return replies_data

        seen_ids = set()
        tweet_count = 0

        # Process first batch
        for tweet in batch:
            if tweet.id in seen_ids:
                continue
            seen_ids.add(tweet.id)
            tweet_count += 1
            target = _extract_reply_target(tweet)
            if target:
                replies_data.append({"reply_to": target})

        # Fetch more batches (up to 4 more to get ~200 replies)
        consecutive_errors = 0
        for _ in range(4):
            if tweet_count >= max_tweets:
                break
            await asyncio.sleep(random.uniform(3.0, 6.0))
            try:
                batch = await batch.next()
                if not batch:
                    break
                consecutive_errors = 0
            except Exception as e:
                error_str = str(e).lower()
                if ("rate" in error_str or "429" in error_str) and consecutive_errors < 1:
                    consecutive_errors += 1
                    await asyncio.sleep(random.uniform(15.0, 30.0))
                    continue
                break

            for tweet in batch:
                if tweet.id in seen_ids:
                    continue
                seen_ids.add(tweet.id)
                tweet_count += 1
                target = _extract_reply_target(tweet)
                if target:
                    replies_data.append({"reply_to": target})

        return replies_data

    @staticmethod
    def _parse_born_from_bio(bio: str) -> str:
        """Try to extract a birth date from bio text using common patterns."""
        if not bio:
            return ""

        month_map_en = {
            "january": "Ocak", "february": "Şubat", "march": "Mart",
            "april": "Nisan", "may": "Mayıs", "june": "Haziran",
            "july": "Temmuz", "august": "Ağustos", "september": "Eylül",
            "october": "Ekim", "november": "Kasım", "december": "Aralık",
            "jan": "Ocak", "feb": "Şubat", "mar": "Mart", "apr": "Nisan",
            "jun": "Haziran", "jul": "Temmuz", "aug": "Ağustos",
            "sep": "Eylül", "oct": "Ekim", "nov": "Kasım", "dec": "Aralık",
        }
        month_map_tr = {
            "ocak": "Ocak", "şubat": "Şubat", "mart": "Mart",
            "nisan": "Nisan", "mayıs": "Mayıs", "haziran": "Haziran",
            "temmuz": "Temmuz", "ağustos": "Ağustos", "eylül": "Eylül",
            "ekim": "Ekim", "kasım": "Kasım", "aralık": "Aralık",
        }
        all_months = {**month_map_en, **month_map_tr}
        month_pattern = "|".join(re.escape(m) for m in all_months.keys())

        bio_lower = bio.lower()

        # Pattern: "DD Month" or "DD Month YYYY" or "Month DD" or "Month DD, YYYY"
        # e.g. "10 Nisan", "April 10", "10 Nisan 2001", "April 10, 2001"
        # Also: "born April 10", "doğum: 10 Nisan"
        patterns = [
            # "10 Nisan 2001" or "10 nisan"
            rf"(\d{{1,2}})\s*({month_pattern})(?:\s*,?\s*(\d{{4}}))?",
            # "April 10, 2001" or "april 10"
            rf"({month_pattern})\s*(\d{{1,2}})(?:\s*,?\s*(\d{{4}}))?",
            # "10.04.2001" or "10/04/2001" (DD.MM.YYYY)
            r"(\d{1,2})[./](\d{1,2})[./](\d{4})",
            # "10.04" (DD.MM)
            r"(\d{1,2})[./](\d{1,2})(?!\d)",
        ]

        month_names_tr = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                          "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]

        for i, pat in enumerate(patterns):
            m = re.search(pat, bio_lower)
            if not m:
                continue
            if i == 0:  # DD Month [YYYY]
                day = m.group(1)
                month_str = all_months.get(m.group(2), "")
                year = m.group(3) or ""
            elif i == 1:  # Month DD [YYYY]
                month_str = all_months.get(m.group(1), "")
                day = m.group(2)
                year = m.group(3) or ""
            elif i == 2:  # DD.MM.YYYY
                day = m.group(1)
                mm = int(m.group(2))
                if 1 <= mm <= 12:
                    month_str = month_names_tr[mm]
                else:
                    continue
                year = m.group(3)
            elif i == 3:  # DD.MM
                day = m.group(1)
                mm = int(m.group(2))
                if 1 <= mm <= 12:
                    month_str = month_names_tr[mm]
                else:
                    continue
                year = ""
            else:
                continue

            if month_str and day:
                result = f"{int(day)} {month_str}"
                if year:
                    result += f" {year}"
                return result

        return ""

    def _is_eligible(self, tweet) -> bool:
        """Only original tweets and quote tweets are eligible."""
        # Skip retweets
        if hasattr(tweet, "retweeted_tweet") and tweet.retweeted_tweet:
            return False
        # Skip replies (in_reply_to is set)
        if hasattr(tweet, "in_reply_to") and tweet.in_reply_to:
            return False
        return True

    def _extract(self, tweet, username: str = "") -> dict:
        """Extract needed fields from a tweet object."""
        is_quote = bool(hasattr(tweet, "quoted_tweet") and tweet.quoted_tweet)
        tweet_id = tweet.id
        return {
            "id": tweet_id,
            "text": tweet.full_text if hasattr(tweet, "full_text") else tweet.text,
            "created_at": tweet.created_at,
            "favorite_count": tweet.favorite_count,
            "retweet_count": tweet.retweet_count,
            "reply_count": getattr(tweet, "reply_count", 0),
            "view_count": getattr(tweet, "view_count", None),
            "is_quote": is_quote,
            "lang": getattr(tweet, "lang", None),
            "url": f"https://x.com/{username}/status/{tweet_id}" if username else "",
        }
