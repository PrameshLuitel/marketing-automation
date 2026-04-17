"""
Reddit scraper using the public JSON API (no auth needed).
Append .json to any subreddit URL for structured data.
Scrapes trending discussions, pain points, and industry buzz.
"""

import asyncio
import time
from datetime import datetime
from typing import Optional
from loguru import logger

from .base import BaseScraper, ScrapedItem, register_scraper

try:
    import requests
except ImportError:
    requests = None


@register_scraper
class RedditScraper(BaseScraper):
    """Scrapes Reddit public JSON API for marketing intelligence."""

    PLATFORM_NAME = "reddit"

    def __init__(
        self,
        subreddits: Optional[list[str]] = None,
        search_queries: Optional[list[str]] = None,
        delay_seconds: float = 2.0,
        max_items: int = 100,
    ):
        super().__init__(
            platform="reddit",
            delay_seconds=delay_seconds,
            max_items=max_items,
        )
        self.subreddits = subreddits or [
            "marketing",
            "digitalmarketing",
            "socialmedia",
            "advertising",
            "content_marketing",
            "SEO",
            "PPC",
            "copywriting",
            "smallbusiness",
            "Entrepreneur",
        ]
        self.search_queries = search_queries or []
        self.headers = {
            "User-Agent": "MarketingAutomation/1.0 (research bot; +https://github.com)",
            "Accept": "application/json",
        }

    def _fetch_subreddit(self, subreddit: str, sort: str = "hot", limit: int = 15) -> list[dict]:
        """Fetch posts from a subreddit's JSON API."""
        posts = []
        try:
            self._rate_limit()
            url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
            resp = requests.get(url, headers=self.headers, timeout=15)

            if resp.status_code == 429:
                logger.warning(f"[reddit] Rate limited on r/{subreddit}, backing off...")
                time.sleep(10)
                return []

            if resp.status_code != 200:
                logger.warning(f"[reddit] HTTP {resp.status_code} for r/{subreddit}")
                return []

            data = resp.json()
            children = data.get("data", {}).get("children", [])

            for child in children:
                post_data = child.get("data", {})
                if post_data.get("stickied"):
                    continue  # Skip pinned posts

                posts.append({
                    "id": post_data.get("id", ""),
                    "title": post_data.get("title", ""),
                    "selftext": post_data.get("selftext", ""),
                    "url": f"https://reddit.com{post_data.get('permalink', '')}",
                    "author": post_data.get("author", "[deleted]"),
                    "subreddit": subreddit,
                    "score": post_data.get("score", 0),
                    "upvote_ratio": post_data.get("upvote_ratio", 0),
                    "num_comments": post_data.get("num_comments", 0),
                    "flair": post_data.get("link_flair_text", ""),
                    "created_utc": post_data.get("created_utc", 0),
                    "is_self": post_data.get("is_self", False),
                })

        except Exception as e:
            logger.warning(f"[reddit] Failed to fetch r/{subreddit}: {e}")

        return posts

    def _fetch_top_comments(self, permalink: str, max_comments: int = 5) -> list[str]:
        """Fetch top-level comments for richer context."""
        try:
            self._rate_limit()
            url = f"https://www.reddit.com{permalink}.json?limit=10&sort=top"
            resp = requests.get(url, headers=self.headers, timeout=10)

            if resp.status_code != 200:
                return []

            data = resp.json()
            if len(data) < 2:
                return []

            comments = []
            for child in data[1].get("data", {}).get("children", []):
                body = child.get("data", {}).get("body", "")
                if body and len(body) > 20 and body != "[deleted]":
                    comments.append(body[:500])
                    if len(comments) >= max_comments:
                        break

            return comments

        except Exception:
            return []

    def _search_reddit(self, query: str, limit: int = 10) -> list[dict]:
        """Search Reddit for specific queries."""
        posts = []
        try:
            self._rate_limit()
            url = f"https://www.reddit.com/search.json?q={query.replace(' ', '+')}&sort=relevance&t=week&limit={limit}"
            resp = requests.get(url, headers=self.headers, timeout=15)

            if resp.status_code != 200:
                return []

            data = resp.json()
            for child in data.get("data", {}).get("children", []):
                post_data = child.get("data", {})
                posts.append({
                    "id": post_data.get("id", ""),
                    "title": post_data.get("title", ""),
                    "selftext": post_data.get("selftext", ""),
                    "url": f"https://reddit.com{post_data.get('permalink', '')}",
                    "author": post_data.get("author", "[deleted]"),
                    "subreddit": post_data.get("subreddit", ""),
                    "score": post_data.get("score", 0),
                    "num_comments": post_data.get("num_comments", 0),
                    "created_utc": post_data.get("created_utc", 0),
                })

        except Exception as e:
            logger.warning(f"[reddit] Search failed for '{query}': {e}")

        return posts

    async def scrape(self) -> list[ScrapedItem]:
        """Scrape Reddit for marketing intelligence."""
        items = []
        seen_ids = set()

        # ── Subreddit scraping ────────────────────────────
        for subreddit in self.subreddits:
            if not self._check_limit():
                break

            logger.info(f"[reddit] Scraping r/{subreddit}")
            posts = await asyncio.to_thread(self._fetch_subreddit, subreddit, "hot", 15)

            for post in posts:
                if not self._check_limit():
                    break

                post_id = post.get("id", "")
                if not post_id or post_id in seen_ids:
                    continue
                seen_ids.add(post_id)

                title = post.get("title", "")
                selftext = post.get("selftext", "")

                # Build rich text: title + body + top comments
                text_parts = [f"TITLE: {title}"]
                if selftext:
                    text_parts.append(f"POST: {selftext[:2000]}")

                # Get top comments for high-engagement posts
                if post.get("num_comments", 0) > 10:
                    permalink = post.get("url", "").replace("https://reddit.com", "")
                    if permalink:
                        comments = await asyncio.to_thread(self._fetch_top_comments, permalink, 3)
                        if comments:
                            text_parts.append(f"TOP COMMENTS:\n" + "\n---\n".join(comments))

                text = "\n\n".join(text_parts)
                if len(text) < 30:
                    continue

                content_id = ScrapedItem.generate_id("reddit", post_id)

                # Parse publish date
                pub_date = None
                created_utc = post.get("created_utc", 0)
                if created_utc:
                    pub_date = datetime.utcfromtimestamp(created_utc)

                item = ScrapedItem(
                    platform="reddit",
                    content_id=content_id,
                    title=title,
                    text=text[:5000],
                    url=post.get("url", ""),
                    author=post.get("author", ""),
                    metadata={
                        "subreddit": subreddit,
                        "flair": post.get("flair", ""),
                        "upvote_ratio": post.get("upvote_ratio", 0),
                        "is_self": post.get("is_self", False),
                    },
                    view_count=0,
                    like_count=post.get("score", 0),
                    comment_count=post.get("num_comments", 0),
                    published_at=pub_date,
                )

                items.append(item)
                self._items_scraped += 1

        # ── Search queries ────────────────────────────────
        for query in self.search_queries:
            if not self._check_limit():
                break

            logger.info(f"[reddit] Searching: '{query}'")
            posts = await asyncio.to_thread(self._search_reddit, query, 10)

            for post in posts:
                if not self._check_limit():
                    break

                post_id = post.get("id", "")
                if not post_id or post_id in seen_ids:
                    continue
                seen_ids.add(post_id)

                title = post.get("title", "")
                selftext = post.get("selftext", "")
                text = f"{title}\n\n{selftext}".strip()

                if len(text) < 30:
                    continue

                content_id = ScrapedItem.generate_id("reddit", post_id)

                item = ScrapedItem(
                    platform="reddit",
                    content_id=content_id,
                    title=title,
                    text=text[:5000],
                    url=post.get("url", ""),
                    author=post.get("author", ""),
                    metadata={
                        "subreddit": post.get("subreddit", ""),
                        "search_query": query,
                    },
                    like_count=post.get("score", 0),
                    comment_count=post.get("num_comments", 0),
                )

                items.append(item)
                self._items_scraped += 1

        logger.info(f"[reddit] Total: {len(items)} posts scraped")
        return items
