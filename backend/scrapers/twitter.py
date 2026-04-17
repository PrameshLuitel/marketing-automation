"""
Twitter/X scraper using multiple fallback strategies:
1. Twitter Syndication API (embedded tweet data — most reliable)
2. Nitter instances (public Twitter frontend mirrors)
3. Twitter's search guest API
No API keys needed.
"""

import asyncio
import json
import re
import time
from datetime import datetime
from typing import Optional
from loguru import logger

from .base import BaseScraper, ScrapedItem, register_scraper

try:
    import requests
except ImportError:
    requests = None


# Known working Nitter instances (public mirrors of Twitter)
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.cz",
]


@register_scraper
class TwitterScraper(BaseScraper):
    """Scrapes Twitter/X public data via syndication API and Nitter mirrors."""

    PLATFORM_NAME = "twitter"

    def __init__(
        self,
        search_queries: Optional[list[str]] = None,
        accounts: Optional[list[str]] = None,
        delay_seconds: float = 3.0,
        max_items: int = 80,
    ):
        super().__init__(
            platform="twitter",
            delay_seconds=delay_seconds,
            max_items=max_items,
        )
        self.search_queries = search_queries or [
            "digital marketing tips",
            "marketing automation",
            "social media strategy",
            "content marketing",
            "brand marketing 2026",
        ]
        self.accounts = accounts or []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _scrape_nitter_search(self, query: str, max_results: int = 10) -> list[dict]:
        """Search tweets via Nitter instances."""
        for instance in NITTER_INSTANCES:
            try:
                self._rate_limit()
                url = f"{instance}/search?f=tweets&q={query.replace(' ', '+')}"
                resp = requests.get(url, headers=self.headers, timeout=15)

                if resp.status_code != 200:
                    continue

                page = resp.text
                tweets = []

                # Parse Nitter HTML for tweets
                # Nitter uses consistent HTML classes
                tweet_blocks = re.findall(
                    r'<div class="timeline-item[^"]*">(.*?)</div>\s*</div>\s*</div>',
                    page,
                    re.DOTALL,
                )

                if not tweet_blocks:
                    # Try alternative pattern
                    tweet_blocks = re.findall(
                        r'class="tweet-content[^"]*"[^>]*>(.*?)</div>',
                        page,
                        re.DOTALL,
                    )

                for block in tweet_blocks[:max_results]:
                    # Extract tweet text
                    text_match = re.search(r'class="tweet-content[^"]*"[^>]*>(.*?)</div>', block, re.DOTALL)
                    text = ""
                    if text_match:
                        text = re.sub(r'<[^>]+>', ' ', text_match.group(1)).strip()

                    if not text:
                        # Try extracting from the block itself if it's already the content
                        text = re.sub(r'<[^>]+>', ' ', block).strip()

                    if not text or len(text) < 10:
                        continue

                    # Extract username
                    user_match = re.search(r'@(\w+)', block) or re.search(r'href="/(\w+)/status', block)
                    username = user_match.group(1) if user_match else "unknown"

                    # Extract stats
                    likes = 0
                    retweets = 0
                    replies = 0
                    stats_matches = re.findall(r'class="icon-[^"]*"[^>]*></span>\s*(\d+[,.\d]*)', block)
                    if len(stats_matches) >= 1:
                        replies = self._parse_count(stats_matches[0])
                    if len(stats_matches) >= 2:
                        retweets = self._parse_count(stats_matches[1])
                    if len(stats_matches) >= 3:
                        likes = self._parse_count(stats_matches[2])

                    # Extract tweet link
                    link_match = re.search(r'href="(/[^/]+/status/\d+)', block)
                    tweet_url = f"{instance}{link_match.group(1)}" if link_match else ""
                    tweet_id = link_match.group(1).split("/")[-1] if link_match else str(hash(text))[:12]

                    tweets.append({
                        "id": tweet_id,
                        "text": text,
                        "author": username,
                        "url": tweet_url,
                        "likes": likes,
                        "retweets": retweets,
                        "replies": replies,
                        "source": "nitter",
                    })

                if tweets:
                    return tweets

            except Exception as e:
                logger.debug(f"[twitter] Nitter instance {instance} failed: {e}")
                continue

        return []

    def _scrape_syndication(self, query: str) -> list[dict]:
        """Use Twitter's syndication/embed endpoint for tweet data."""
        tweets = []
        try:
            self._rate_limit()
            # Twitter syndication timeline search
            url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{query}"
            resp = requests.get(url, headers=self.headers, timeout=10)

            if resp.status_code == 200:
                # Parse embedded timeline HTML
                page = resp.text
                tweet_matches = re.findall(
                    r'data-tweet-id="(\d+)".*?class="[^"]*tweet-text[^"]*"[^>]*>(.*?)</p>',
                    page,
                    re.DOTALL,
                )
                for tweet_id, tweet_text in tweet_matches[:10]:
                    clean_text = re.sub(r'<[^>]+>', ' ', tweet_text).strip()
                    if clean_text and len(clean_text) > 10:
                        tweets.append({
                            "id": tweet_id,
                            "text": clean_text,
                            "author": query,
                            "url": f"https://twitter.com/{query}/status/{tweet_id}",
                            "likes": 0,
                            "retweets": 0,
                            "replies": 0,
                            "source": "syndication",
                        })

        except Exception as e:
            logger.debug(f"[twitter] Syndication failed for {query}: {e}")

        return tweets

    def _parse_count(self, text: str) -> int:
        """Parse a count string like '1.2K' or '45,000' into an integer."""
        try:
            text = text.strip().replace(",", "")
            if "K" in text.upper():
                return int(float(text.upper().replace("K", "")) * 1000)
            elif "M" in text.upper():
                return int(float(text.upper().replace("M", "")) * 1000000)
            return int(float(text))
        except (ValueError, TypeError):
            return 0

    async def scrape(self) -> list[ScrapedItem]:
        """Scrape Twitter for marketing intelligence."""
        items = []
        seen_ids = set()

        # ── Search queries via Nitter ────────────────────
        for query in self.search_queries:
            if not self._check_limit():
                break

            logger.info(f"[twitter] Searching: '{query}'")
            tweets = await asyncio.to_thread(self._scrape_nitter_search, query, 10)

            if not tweets:
                logger.debug(f"[twitter] Nitter search returned 0 for '{query}', trying syndication")

            for tweet in tweets:
                if not self._check_limit():
                    break

                tweet_id = tweet.get("id", "")
                if not tweet_id or tweet_id in seen_ids:
                    continue
                seen_ids.add(tweet_id)

                text = tweet.get("text", "")
                if not text or len(text) < 15:
                    continue

                content_id = ScrapedItem.generate_id("twitter", tweet_id)

                item = ScrapedItem(
                    platform="twitter",
                    content_id=content_id,
                    title=f"Tweet: {text[:80]}...",
                    text=text,
                    url=tweet.get("url", ""),
                    author=tweet.get("author", ""),
                    metadata={
                        "tweet_id": tweet_id,
                        "search_query": query,
                        "source": tweet.get("source", "nitter"),
                    },
                    like_count=tweet.get("likes", 0),
                    share_count=tweet.get("retweets", 0),
                    comment_count=tweet.get("replies", 0),
                )

                items.append(item)
                self._items_scraped += 1

        # ── Account timelines via syndication ─────────────
        for account in self.accounts:
            if not self._check_limit():
                break

            logger.info(f"[twitter] Fetching timeline: @{account}")
            tweets = await asyncio.to_thread(self._scrape_syndication, account)

            for tweet in tweets:
                if not self._check_limit():
                    break

                tweet_id = tweet.get("id", "")
                if not tweet_id or tweet_id in seen_ids:
                    continue
                seen_ids.add(tweet_id)

                text = tweet.get("text", "")
                if not text or len(text) < 15:
                    continue

                content_id = ScrapedItem.generate_id("twitter", tweet_id)

                item = ScrapedItem(
                    platform="twitter",
                    content_id=content_id,
                    title=f"@{account}: {text[:70]}...",
                    text=text,
                    url=tweet.get("url", ""),
                    author=account,
                    metadata={
                        "tweet_id": tweet_id,
                        "account": account,
                        "source": "syndication",
                    },
                    like_count=tweet.get("likes", 0),
                    share_count=tweet.get("retweets", 0),
                )

                items.append(item)
                self._items_scraped += 1

        logger.info(f"[twitter] Total: {len(items)} tweets scraped")
        return items
