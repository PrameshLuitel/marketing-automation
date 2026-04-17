"""
TikTok scraper using yt-dlp for reliable metadata extraction.
Falls back to oEmbed + web scraping if yt-dlp is unavailable.
No API keys needed.
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Optional
from loguru import logger

from .base import BaseScraper, ScrapedItem, register_scraper

try:
    import requests
except ImportError:
    requests = None


USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


@register_scraper
class TikTokScraper(BaseScraper):
    """Scrapes TikTok public video metadata using yt-dlp + fallbacks."""

    PLATFORM_NAME = "tiktok"

    def __init__(
        self,
        hashtags: Optional[list[str]] = None,
        delay_seconds: float = 3.0,
        max_items: int = 100,
    ):
        super().__init__(
            platform="tiktok",
            delay_seconds=delay_seconds,
            max_items=max_items,
        )
        self.hashtags = hashtags or [
            # English
            "digitalmarketing",
            "marketingtips",
            "socialmediamarketing",
            "contentcreator",
            "brandstrategy",
            "marketingtrends",
            # Viral / Meme culture
            "viral",
            "trending",
            "fyp",
            "memes",
            "relatable",
        ]
        self._ua_index = 0
        self._yt_dlp_available = self._check_yt_dlp()

    def _check_yt_dlp(self) -> bool:
        """Check if yt-dlp is available with TikTok support."""
        try:
            import yt_dlp
            return True
        except ImportError:
            logger.warning("[tiktok] yt-dlp not installed — using web scraping fallback")
            return False

    def _get_user_agent(self) -> str:
        """Rotate user agents."""
        ua = USER_AGENTS[self._ua_index % len(USER_AGENTS)]
        self._ua_index += 1
        return ua

    def _scrape_hashtag_ytdlp(self, hashtag: str, max_results: int = 10) -> list[dict]:
        """Scrape TikTok hashtag page using yt-dlp."""
        try:
            import yt_dlp

            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
                "skip_download": True,
                "ignoreerrors": True,
                "socket_timeout": 20,
                "playlistend": max_results,
                "http_headers": {
                    "User-Agent": self._get_user_agent(),
                },
            }

            videos = []
            url = f"https://www.tiktok.com/tag/{hashtag}"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(url, download=False)

                if not result:
                    return []

                entries = result.get("entries", [])
                if not entries:
                    # Single video result
                    if result.get("id"):
                        entries = [result]
                    else:
                        return []

                for entry in entries:
                    if entry is None:
                        continue
                    videos.append({
                        "video_id": entry.get("id", ""),
                        "description": entry.get("description", "") or "",
                        "url": entry.get("webpage_url", ""),
                        "author": entry.get("uploader", entry.get("creator", "")),
                        "view_count": entry.get("view_count", 0) or 0,
                        "like_count": entry.get("like_count", 0) or 0,
                        "comment_count": entry.get("comment_count", 0) or 0,
                        "share_count": entry.get("repost_count", 0) or 0,
                        "duration": entry.get("duration", 0) or 0,
                        "upload_date": entry.get("upload_date", ""),
                        "hashtag": hashtag,
                        "hashtags": self._extract_hashtags_from_desc(
                            entry.get("description", "") or ""
                        ),
                        "music": entry.get("track", ""),
                    })

            return videos

        except Exception as e:
            logger.warning(f"[tiktok] yt-dlp failed for #{hashtag}: {e}")
            return []

    def _scrape_hashtag_web(self, hashtag: str) -> list[dict]:
        """Fallback: scrape TikTok hashtag page via web."""
        videos = []
        try:
            url = f"https://www.tiktok.com/tag/{hashtag}"
            headers = {
                "User-Agent": self._get_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }

            self._rate_limit()
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"[tiktok] HTTP {resp.status_code} for #{hashtag}")
                return []

            page_text = resp.text

            # Try to extract JSON data from page
            json_patterns = [
                r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
                r'<script id="SIGI_STATE"[^>]*>(.*?)</script>',
            ]

            for pattern in json_patterns:
                matches = re.findall(pattern, page_text, re.DOTALL)
                if matches:
                    try:
                        data = json.loads(matches[0])
                        items = self._extract_items_from_json(data)
                        if items:
                            for item in items:
                                item["hashtag"] = hashtag
                            videos.extend(items)
                            break
                    except json.JSONDecodeError:
                        continue

            # Fallback: extract video links from the page
            if not videos:
                video_urls = re.findall(
                    r'href="(https://www\.tiktok\.com/@[^/]+/video/\d+)"',
                    page_text,
                )
                descriptions = re.findall(
                    r'"description"\s*:\s*"([^"]*)"', page_text
                )
                for i, vurl in enumerate(video_urls[:10]):
                    video_id = vurl.split("/")[-1]
                    desc = descriptions[i] if i < len(descriptions) else ""
                    videos.append({
                        "video_id": video_id,
                        "description": desc,
                        "url": vurl,
                        "hashtag": hashtag,
                        "author": "",
                        "view_count": 0,
                        "like_count": 0,
                        "comment_count": 0,
                    })

        except Exception as e:
            logger.warning(f"[tiktok] Web scrape failed for #{hashtag}: {e}")

        return videos

    def _extract_items_from_json(self, data: dict) -> list[dict]:
        """Extract video items from TikTok page JSON data."""
        items = []

        if not isinstance(data, dict):
            return items

        # Try various TikTok JSON structures
        item_module = data.get("ItemModule", {})
        if not item_module:
            default_scope = data.get("__DEFAULT_SCOPE__", {})
            item_list = default_scope.get("webapp.video-detail", {})
            if item_list:
                struct = item_list.get("itemInfo", {}).get("itemStruct", {})
                if struct.get("id"):
                    item_module = {struct["id"]: struct}

        if item_module and isinstance(item_module, dict):
            for vid_id, vid_data in item_module.items():
                if isinstance(vid_data, dict):
                    stats = vid_data.get("stats", {})
                    items.append({
                        "video_id": vid_id,
                        "description": vid_data.get("desc", ""),
                        "url": f"https://www.tiktok.com/@{vid_data.get('author', 'unknown')}/video/{vid_id}",
                        "author": vid_data.get("author", ""),
                        "view_count": stats.get("playCount", 0),
                        "like_count": stats.get("diggCount", 0),
                        "comment_count": stats.get("commentCount", 0),
                        "share_count": stats.get("shareCount", 0),
                        "hashtags": [
                            t.get("hashtagName", "")
                            for t in vid_data.get("textExtra", [])
                            if t.get("hashtagName")
                        ],
                    })

        return items

    def _get_oembed_data(self, video_url: str) -> Optional[dict]:
        """Get video metadata via TikTok's oEmbed endpoint (reliable, official)."""
        try:
            oembed_url = f"https://www.tiktok.com/oembed?url={video_url}"
            resp = requests.get(oembed_url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "title": data.get("title", ""),
                    "author": data.get("author_name", ""),
                    "author_url": data.get("author_url", ""),
                    "thumbnail": data.get("thumbnail_url", ""),
                }
        except Exception:
            pass
        return None

    def _extract_hashtags_from_desc(self, description: str) -> list[str]:
        """Extract hashtags from description text."""
        return re.findall(r'#(\w+)', description)

    async def scrape(self) -> list[ScrapedItem]:
        """Scrape TikTok content from hashtag pages."""
        items = []
        seen_ids = set()

        for hashtag in self.hashtags:
            if not self._check_limit():
                break

            logger.info(f"[tiktok] Scraping #{hashtag}")
            self._rate_limit()

            # Try yt-dlp first, then web scraping
            if self._yt_dlp_available:
                videos = await asyncio.to_thread(self._scrape_hashtag_ytdlp, hashtag, 10)
            else:
                videos = await asyncio.to_thread(self._scrape_hashtag_web, hashtag)

            for video in videos:
                if not self._check_limit():
                    break

                vid_id = video.get("video_id", "")
                if not vid_id or vid_id in seen_ids:
                    continue
                seen_ids.add(vid_id)

                description = video.get("description", "")
                if not description or len(description) < 10:
                    # Try oEmbed for more data
                    vurl = video.get("url", "")
                    if vurl:
                        oembed = self._get_oembed_data(vurl)
                        if oembed and oembed.get("title"):
                            description = oembed["title"]
                            if not video.get("author"):
                                video["author"] = oembed.get("author", "")

                if not description or len(description) < 10:
                    continue

                content_id = ScrapedItem.generate_id("tiktok", vid_id)
                hashtags_found = video.get("hashtags", [hashtag])

                item = ScrapedItem(
                    platform="tiktok",
                    content_id=content_id,
                    title=f"TikTok #{hashtag}: {description[:80]}",
                    text=description,
                    url=video.get("url", ""),
                    author=video.get("author", ""),
                    metadata={
                        "video_id": vid_id,
                        "hashtag": hashtag,
                        "hashtags": hashtags_found,
                        "music": video.get("music", ""),
                        "duration": video.get("duration", 0),
                        "source": "yt-dlp" if self._yt_dlp_available else "web",
                    },
                    view_count=video.get("view_count", 0),
                    like_count=video.get("like_count", 0),
                    comment_count=video.get("comment_count", 0),
                    share_count=video.get("share_count", 0),
                )

                items.append(item)
                self._items_scraped += 1

        logger.info(f"[tiktok] Total: {len(items)} videos scraped")
        return items
