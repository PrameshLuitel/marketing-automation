"""
YouTube scraper using yt-dlp (battle-tested, 50k+ GitHub stars) + youtube-transcript-api.
No API keys needed. Extracts metadata, engagement metrics, and transcripts.
"""

import asyncio
import json
import re
import subprocess
from datetime import datetime
from typing import Optional
from loguru import logger

from .base import BaseScraper, ScrapedItem, register_scraper

# Transcript API — still the best for getting captions
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

try:
    import feedparser
except ImportError:
    feedparser = None

try:
    import requests
except ImportError:
    requests = None


@register_scraper
class YouTubeScraper(BaseScraper):
    """Scrapes YouTube using yt-dlp for metadata + youtube-transcript-api for transcripts."""

    PLATFORM_NAME = "youtube"
    CHANNEL_RSS_TEMPLATE = "https://www.youtube.com/feeds/videos.xml?channel_id={}"

    def __init__(
        self,
        channel_ids: Optional[list[str]] = None,
        search_queries: Optional[list[str]] = None,
        delay_seconds: float = 2.0,
        max_items: int = 200,
    ):
        super().__init__(
            platform="youtube",
            delay_seconds=delay_seconds,
            max_items=max_items,
        )
        self.channel_ids = channel_ids or []
        self.search_queries = search_queries or [
            # English — core marketing
            "digital marketing trends",
            "social media marketing strategy",
            "content marketing tips",
            "marketing automation",
            "brand marketing",
            # Viral / Meme culture
            "viral marketing strategy",
            "meme marketing examples",
            "trending memes today",
            "viral social media campaigns",
        ]
        self._yt_dlp_available = self._check_yt_dlp()

    def _check_yt_dlp(self) -> bool:
        """Check if yt-dlp is available."""
        try:
            import yt_dlp
            return True
        except ImportError:
            logger.warning("[youtube] yt-dlp not installed — falling back to RSS/requests")
            return False

    def _search_videos_ytdlp(self, query: str, max_results: int = 5) -> list[dict]:
        """Search YouTube using yt-dlp's ytsearch extractor (no API key needed)."""
        try:
            import yt_dlp

            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
                "skip_download": True,
                "ignoreerrors": True,
                "no_color": True,
                "socket_timeout": 15,
            }

            videos = []
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_term = f"ytsearch{max_results}:{query}"
                result = ydl.extract_info(search_term, download=False)

                if not result or "entries" not in result:
                    return []

                for entry in result["entries"]:
                    if entry is None:
                        continue
                    videos.append({
                        "video_id": entry.get("id", ""),
                        "title": entry.get("title", ""),
                        "description": (entry.get("description", "") or "")[:2000],
                        "author": entry.get("uploader", entry.get("channel", "")),
                        "view_count": entry.get("view_count", 0) or 0,
                        "like_count": entry.get("like_count", 0) or 0,
                        "comment_count": entry.get("comment_count", 0) or 0,
                        "duration": entry.get("duration", 0) or 0,
                        "upload_date": entry.get("upload_date", ""),
                        "tags": entry.get("tags", []) or [],
                        "thumbnail": entry.get("thumbnail", ""),
                        "url": entry.get("webpage_url", f"https://www.youtube.com/watch?v={entry.get('id', '')}"),
                    })

            return videos

        except Exception as e:
            logger.warning(f"[youtube] yt-dlp search failed for '{query}': {e}")
            return []

    def _get_channel_videos_ytdlp(self, channel_id: str, max_results: int = 10) -> list[dict]:
        """Get latest videos from a YouTube channel using yt-dlp."""
        try:
            import yt_dlp

            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": True,
                "skip_download": True,
                "ignoreerrors": True,
                "playlistend": max_results,
                "socket_timeout": 15,
            }

            videos = []
            channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(channel_url, download=False)

                if not result or "entries" not in result:
                    return []

                for entry in result["entries"]:
                    if entry is None:
                        continue
                    videos.append({
                        "video_id": entry.get("id", ""),
                        "title": entry.get("title", ""),
                        "description": "",
                        "author": result.get("uploader", result.get("channel", "")),
                        "view_count": entry.get("view_count", 0) or 0,
                        "like_count": 0,
                        "comment_count": 0,
                        "duration": entry.get("duration", 0) or 0,
                        "upload_date": entry.get("upload_date", ""),
                        "tags": [],
                        "thumbnail": entry.get("thumbnail", ""),
                        "url": entry.get("url", f"https://www.youtube.com/watch?v={entry.get('id', '')}"),
                    })

            return videos

        except Exception as e:
            logger.warning(f"[youtube] yt-dlp channel fetch failed for {channel_id}: {e}")
            return []

    def _get_video_ids_from_rss(self) -> list[dict]:
        """Fallback: Fetch recent video IDs from YouTube RSS feeds."""
        if feedparser is None:
            return []

        videos = []

        for channel_id in self.channel_ids:
            self._rate_limit()
            try:
                url = self.CHANNEL_RSS_TEMPLATE.format(channel_id)
                feed = feedparser.parse(url)
                for entry in feed.entries[:10]:
                    video_id = entry.get("yt_videoid", "")
                    if video_id:
                        videos.append({
                            "video_id": video_id,
                            "title": entry.get("title", ""),
                            "author": entry.get("author", ""),
                            "description": "",
                            "view_count": 0,
                            "like_count": 0,
                            "comment_count": 0,
                            "upload_date": entry.get("published", ""),
                            "url": entry.get("link", ""),
                        })
            except Exception as e:
                logger.warning(f"[youtube] RSS failed for {channel_id}: {e}")

        # Search via web scraping fallback
        for query in self.search_queries:
            self._rate_limit()
            try:
                search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                if requests:
                    resp = requests.get(
                        search_url,
                        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
                        timeout=15,
                    )
                    video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', resp.text)
                    seen = set()
                    for vid in video_ids[:5]:
                        if vid not in seen:
                            seen.add(vid)
                            videos.append({
                                "video_id": vid,
                                "title": "",
                                "author": "",
                                "description": "",
                                "view_count": 0,
                                "like_count": 0,
                                "comment_count": 0,
                                "url": f"https://www.youtube.com/watch?v={vid}",
                            })
            except Exception as e:
                logger.warning(f"[youtube] Search fallback failed for '{query}': {e}")

        return videos

    def _get_transcript(self, video_id: str) -> Optional[str]:
        """Fetch transcript for a YouTube video and translate to English."""
        if YouTubeTranscriptApi is None:
            return None

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            try:
                transcript = transcript_list.find_transcript(['en', 'ne', 'hi'])
            except Exception:
                transcript = list(transcript_list)[0]

            if transcript.language_code != 'en':
                try:
                    transcript = transcript.translate('en')
                except Exception:
                    pass

            fetched_data = transcript.fetch()
            full_text = " ".join([item["text"] for item in fetched_data])
            return full_text.strip()
        except Exception as e:
            logger.debug(f"[youtube] No transcript for {video_id}: {e}")
            return None

    def _get_video_metadata_oembed(self, video_id: str) -> dict:
        """Get basic video metadata via oembed (no API key needed)."""
        try:
            url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "title": data.get("title", ""),
                    "author": data.get("author_name", ""),
                    "thumbnail": data.get("thumbnail_url", ""),
                }
        except Exception:
            pass
        return {}

    async def scrape(self) -> list[ScrapedItem]:
        """Scrape YouTube videos: metadata from yt-dlp, transcripts from API."""
        items = []
        seen_ids = set()

        # ── Primary: yt-dlp based search ──────────────────
        if self._yt_dlp_available:
            # Search queries
            for query in self.search_queries:
                if not self._check_limit():
                    break

                self._rate_limit()
                logger.info(f"[youtube] Searching: '{query}' via yt-dlp")
                videos = await asyncio.to_thread(self._search_videos_ytdlp, query, 5)

                for video in videos:
                    vid_id = video.get("video_id", "")
                    if not vid_id or vid_id in seen_ids:
                        continue
                    seen_ids.add(vid_id)

                    if not self._check_limit():
                        break

                    # Get transcript
                    self._rate_limit()
                    transcript = await asyncio.to_thread(self._get_transcript, vid_id)

                    # Build rich text from description + transcript
                    description = video.get("description", "")
                    text_parts = []
                    if description:
                        text_parts.append(f"DESCRIPTION: {description}")
                    if transcript:
                        text_parts.append(f"TRANSCRIPT: {transcript[:4000]}")
                    if video.get("tags"):
                        text_parts.append(f"TAGS: {', '.join(video['tags'][:20])}")

                    text = "\n\n".join(text_parts)
                    if not text or len(text) < 50:
                        continue

                    content_id = ScrapedItem.generate_id("youtube", vid_id)
                    item = ScrapedItem(
                        platform="youtube",
                        content_id=content_id,
                        title=video.get("title", f"Video {vid_id}"),
                        text=text[:5000],
                        url=video.get("url", f"https://www.youtube.com/watch?v={vid_id}"),
                        author=video.get("author", ""),
                        metadata={
                            "video_id": vid_id,
                            "thumbnail": video.get("thumbnail", ""),
                            "duration": video.get("duration", 0),
                            "upload_date": video.get("upload_date", ""),
                            "tags": video.get("tags", [])[:10],
                            "source": "yt-dlp",
                        },
                        view_count=video.get("view_count", 0),
                        like_count=video.get("like_count", 0),
                        comment_count=video.get("comment_count", 0),
                    )
                    items.append(item)
                    self._items_scraped += 1
                    logger.debug(f"[youtube] Scraped: {item.title[:60]}... (views: {item.view_count})")

            # Channel videos
            for channel_id in self.channel_ids:
                if not self._check_limit():
                    break

                self._rate_limit()
                logger.info(f"[youtube] Fetching channel: {channel_id}")
                videos = await asyncio.to_thread(self._get_channel_videos_ytdlp, channel_id, 10)

                for video in videos:
                    vid_id = video.get("video_id", "")
                    if not vid_id or vid_id in seen_ids:
                        continue
                    seen_ids.add(vid_id)

                    if not self._check_limit():
                        break

                    self._rate_limit()
                    transcript = await asyncio.to_thread(self._get_transcript, vid_id)
                    text = transcript[:5000] if transcript else video.get("description", "")
                    if not text or len(text) < 30:
                        continue

                    content_id = ScrapedItem.generate_id("youtube", vid_id)
                    item = ScrapedItem(
                        platform="youtube",
                        content_id=content_id,
                        title=video.get("title", f"Video {vid_id}"),
                        text=text,
                        url=video.get("url", ""),
                        author=video.get("author", ""),
                        metadata={
                            "video_id": vid_id,
                            "source": "yt-dlp-channel",
                        },
                        view_count=video.get("view_count", 0),
                    )
                    items.append(item)
                    self._items_scraped += 1

        # ── Fallback: RSS + web scraping ──────────────────
        else:
            logger.info("[youtube] Using RSS/web scraping fallback")
            rss_videos = await asyncio.to_thread(self._get_video_ids_from_rss)

            for video_info in rss_videos:
                if not self._check_limit():
                    break

                vid_id = video_info["video_id"]
                if vid_id in seen_ids:
                    continue
                seen_ids.add(vid_id)

                self._rate_limit()
                transcript = await asyncio.to_thread(self._get_transcript, vid_id)
                if not transcript or len(transcript) < 50:
                    continue

                meta = self._get_video_metadata_oembed(vid_id)
                title = video_info.get("title") or meta.get("title", f"Video {vid_id}")
                author = video_info.get("author") or meta.get("author", "Unknown")

                content_id = ScrapedItem.generate_id("youtube", vid_id)
                item = ScrapedItem(
                    platform="youtube",
                    content_id=content_id,
                    title=title,
                    text=transcript[:5000],
                    url=f"https://www.youtube.com/watch?v={vid_id}",
                    author=author,
                    metadata={"video_id": vid_id, "source": "rss_fallback"},
                )
                items.append(item)
                self._items_scraped += 1

        logger.info(f"[youtube] Total: {len(items)} videos scraped")
        return items
