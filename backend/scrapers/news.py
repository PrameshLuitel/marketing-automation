"""
News/RSS scraper using feedparser + newspaper3k.
Completely free, no API limits, no keys needed.
"""

import asyncio
from datetime import datetime
from typing import Optional
from loguru import logger

from .base import BaseScraper, ScrapedItem, register_scraper

try:
    import feedparser
except ImportError:
    feedparser = None

try:
    from newspaper import Article
except ImportError:
    Article = None


@register_scraper
class NewsScraper(BaseScraper):
    """Scrapes marketing news and blog posts from RSS feeds."""

    PLATFORM_NAME = "news"

    def __init__(
        self,
        rss_feeds: Optional[list[str]] = None,
        delay_seconds: float = 1.5,
        max_items: int = 200,
    ):
        super().__init__(
            platform="news",
            delay_seconds=delay_seconds,
            max_items=max_items,
        )
        self.rss_feeds = rss_feeds or [
            "https://feeds.feedburner.com/TechCrunch",
            "https://blog.hubspot.com/marketing/rss.xml",
            "https://contentmarketinginstitute.com/feed/",
            "https://feeds.feedburner.com/searchengineland",
            "https://www.socialmediaexaminer.com/feed/",
            "https://neilpatel.com/blog/feed/",
            "https://moz.com/feed",
            "https://www.searchenginejournal.com/feed/",
            "https://adespresso.com/feed/",
            "https://sproutsocial.com/insights/feed/",
        ]

    def _parse_feed(self, feed_url: str) -> list[dict]:
        """Parse an RSS feed and return entries."""
        if feedparser is None:
            logger.error("feedparser not installed")
            return []

        try:
            self._rate_limit()
            feed = feedparser.parse(feed_url)

            if feed.bozo and not feed.entries:
                logger.warning(f"[news] Feed error for {feed_url}: {feed.bozo_exception}")
                return []

            entries = []
            for entry in feed.entries[:15]:  # Max 15 per feed
                entries.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "author": entry.get("author", ""),
                    "published": entry.get("published", ""),
                    "feed_title": feed.feed.get("title", feed_url),
                })

            return entries

        except Exception as e:
            logger.warning(f"[news] Failed to parse {feed_url}: {e}")
            return []

    def _extract_full_text(self, url: str) -> str:
        """Extract full article text using newspaper3k."""
        if Article is None:
            return ""

        try:
            self._rate_limit()
            article = Article(url)
            article.download()
            article.parse()
            return article.text[:5000]  # Cap at 5000 chars
        except Exception as e:
            logger.debug(f"[news] Failed to extract text from {url}: {e}")
            return ""

    async def scrape(self) -> list[ScrapedItem]:
        """Scrape all configured RSS feeds."""
        items = []

        for feed_url in self.rss_feeds:
            if not self._check_limit():
                break

            logger.info(f"[news] Parsing feed: {feed_url[:60]}...")
            entries = self._parse_feed(feed_url)

            for entry in entries:
                if not self._check_limit():
                    break

                title = entry.get("title", "")
                url = entry.get("url", "")
                summary = entry.get("summary", "")

                if not title or not url:
                    continue

                # Try to get full text, fallback to summary
                full_text = self._extract_full_text(url) if url else ""
                text = full_text if full_text else summary

                if not text or len(text) < 30:
                    continue

                # Clean HTML from text
                text = self._clean_html(text)

                content_id = ScrapedItem.generate_id("news", url)

                # Parse published date
                pub_date = None
                if entry.get("published"):
                    try:
                        import email.utils
                        parsed = email.utils.parsedate_to_datetime(entry["published"])
                        pub_date = parsed
                    except Exception:
                        pass

                item = ScrapedItem(
                    platform="news",
                    content_id=content_id,
                    title=title,
                    text=text,
                    url=url,
                    author=entry.get("author", ""),
                    metadata={
                        "feed": entry.get("feed_title", ""),
                        "has_full_text": bool(full_text),
                    },
                    published_at=pub_date,
                )

                items.append(item)
                self._items_scraped += 1

        return items

    @staticmethod
    def _clean_html(text: str) -> str:
        """Remove HTML tags from text."""
        import re
        clean = re.sub(r"<[^>]+>", "", text)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean
