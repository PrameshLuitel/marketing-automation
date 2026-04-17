"""
Base scraper class with built-in rate limiting, retry logic, structured output,
and scraper registry for auto-discovery.
All platform scrapers inherit from this.
"""

import time
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

# Global scraper registry — scrapers register themselves on import
SCRAPER_REGISTRY: dict[str, type] = {}


def register_scraper(cls):
    """Decorator to register a scraper class in the global registry."""
    SCRAPER_REGISTRY[cls.PLATFORM_NAME] = cls
    return cls


class ScrapedItem:
    """Standardized scraped content item."""

    def __init__(
        self,
        platform: str,
        content_id: str,
        title: str,
        text: str,
        url: str = "",
        author: str = "",
        metadata: Optional[dict] = None,
        view_count: int = 0,
        like_count: int = 0,
        comment_count: int = 0,
        share_count: int = 0,
        published_at: Optional[datetime] = None,
    ):
        self.platform = platform
        self.content_id = content_id
        self.title = title
        self.text = text
        self.url = url
        self.author = author
        self.metadata = metadata or {}
        self.view_count = view_count
        self.like_count = like_count
        self.comment_count = comment_count
        self.share_count = share_count
        self.published_at = published_at
        self.scraped_at = datetime.utcnow()

    @property
    def engagement_score(self) -> float:
        """Weighted engagement score for ranking content importance."""
        return (
            (self.view_count * 0.1)
            + (self.like_count * 1.0)
            + (self.comment_count * 2.0)
            + (self.share_count * 3.0)
        )

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "content_id": self.content_id,
            "title": self.title,
            "text": self.text,
            "url": self.url,
            "author": self.author,
            "metadata": self.metadata,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "share_count": self.share_count,
            "engagement_score": self.engagement_score,
            "published_at": self.published_at,
            "scraped_at": self.scraped_at,
        }

    @staticmethod
    def generate_id(platform: str, unique_key: str) -> str:
        """Generate a deterministic content ID."""
        raw = f"{platform}:{unique_key}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class BaseScraper(ABC):
    """
    Abstract base class for all platform scrapers.
    Provides rate limiting, retry logic, item counting, and error isolation.
    """

    PLATFORM_NAME = "base"

    def __init__(
        self,
        platform: str,
        delay_seconds: float = 2.0,
        max_items: int = 200,
    ):
        self.platform = platform
        self.delay_seconds = delay_seconds
        self.max_items = max_items
        self._items_scraped = 0
        self._last_request_time = 0.0
        self._errors: list[str] = []

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay_seconds:
            sleep_time = self.delay_seconds - elapsed
            logger.debug(f"[{self.platform}] Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)
        self._last_request_time = time.time()

    def _check_limit(self) -> bool:
        """Check if we've hit the daily item limit."""
        if self._items_scraped >= self.max_items:
            logger.warning(
                f"[{self.platform}] Daily limit reached: {self._items_scraped}/{self.max_items}"
            )
            return False
        return True

    def _safe_request(self, func, *args, **kwargs):
        """Wrap a request function with error handling. Returns None on failure."""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"[{self.platform}] Request failed: {e}"
            logger.warning(error_msg)
            self._errors.append(error_msg)
            return None

    @abstractmethod
    async def scrape(self) -> list[ScrapedItem]:
        """
        Scrape content from the platform.
        Must be implemented by subclasses.
        """
        pass

    async def run(self) -> list[ScrapedItem]:
        """Execute the scraper with logging and error handling."""
        logger.info(f"[{self.platform}] Starting scrape (max {self.max_items} items)")
        self._items_scraped = 0
        self._errors = []
        start = time.time()

        try:
            items = await self.scrape()
            duration = time.time() - start
            logger.success(
                f"[{self.platform}] Scraped {len(items)} items in {duration:.1f}s"
            )
            if self._errors:
                logger.warning(
                    f"[{self.platform}] Completed with {len(self._errors)} errors"
                )
            return items
        except Exception as e:
            logger.error(f"[{self.platform}] Scrape failed: {e}")
            return []

    def get_health(self) -> dict:
        """Return health status of this scraper."""
        return {
            "platform": self.platform,
            "items_scraped": self._items_scraped,
            "errors": self._errors,
            "healthy": len(self._errors) == 0,
        }
