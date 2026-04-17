"""
Scrapers package — auto-registers all platform scrapers.
Import this module to populate the SCRAPER_REGISTRY.
"""

from .base import SCRAPER_REGISTRY, BaseScraper, ScrapedItem
from .youtube import YouTubeScraper
from .tiktok import TikTokScraper
from .news import NewsScraper
from .google_trends import GoogleTrendsScraper
from .reddit import RedditScraper
from .twitter import TwitterScraper
from .competitor import CompetitorScraper
from .memes import MemeScraper

__all__ = [
    "SCRAPER_REGISTRY",
    "BaseScraper",
    "ScrapedItem",
    "YouTubeScraper",
    "TikTokScraper",
    "NewsScraper",
    "GoogleTrendsScraper",
    "RedditScraper",
    "TwitterScraper",
    "CompetitorScraper",
    "MemeScraper",
]
