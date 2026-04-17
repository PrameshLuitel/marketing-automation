"""
Meme & Viral Content scraper.
Scrapes trending memes and viral content from:
  1. Reddit meme subreddits (r/memes, r/dankmemes, r/MemeEconomy, etc.)
  2. Know Your Meme (trending memes database)
  3. Imgflip (popular meme templates + trending)
  4. Reddit viral posts (r/all/rising + r/popular)

This gives the AI agents awareness of meme culture to create
culturally relevant, viral-ready marketing content.
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

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


# Meme subreddits — covers mainstream + niche meme culture
MEME_SUBREDDITS = [
    "memes",
    "dankmemes",
    "MemeEconomy",      # "Invest!" culture — early meme detection
    "me_irl",
    "wholesomememes",
    "AdviceAnimals",
    "funny",
    "shitposting",
    "terriblefacebookmemes",  # Know what NOT to do
    "FellowKids",       # Brands trying to meme (learning from failures)
    "HolUp",
    "antimeme",
    "surrealmemes",
    "meirl",
]

# Viral content subreddits — general world pulse
VIRAL_SUBREDDITS = [
    "popular",          # Reddit's popular feed
    "all",              # Reddit's r/all
    "OutOfTheLoop",     # Explains trending topics
    "todayilearned",
    "Showerthoughts",
    "AskReddit",
    "worldnews",
    "technology",
    "nottheonion",
]


@register_scraper
class MemeScraper(BaseScraper):
    """Scrapes trending memes and viral content for meme-aware marketing."""

    PLATFORM_NAME = "memes"

    def __init__(
        self,
        meme_subreddits: Optional[list[str]] = None,
        viral_subreddits: Optional[list[str]] = None,
        include_kym: bool = True,
        include_imgflip: bool = True,
        delay_seconds: float = 2.0,
        max_items: int = 100,
    ):
        super().__init__(
            platform="memes",
            delay_seconds=delay_seconds,
            max_items=max_items,
        )
        self.meme_subreddits = meme_subreddits or MEME_SUBREDDITS
        self.viral_subreddits = viral_subreddits or VIRAL_SUBREDDITS
        self.include_kym = include_kym
        self.include_imgflip = include_imgflip
        self.headers = {
            "User-Agent": "MarketingMemeResearch/1.0 (trend analysis bot)",
            "Accept": "application/json",
        }
        self.web_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def scrape(self) -> list[ScrapedItem]:
        """Scrape memes and viral content from all sources."""
        items = []

        # ── 1. Reddit Meme Subreddits (hot/rising posts) ──
        meme_items = await self._scrape_reddit_memes()
        items.extend(meme_items)

        # ── 2. Reddit Viral / Rising Posts (world pulse) ──
        viral_items = await self._scrape_reddit_viral()
        items.extend(viral_items)

        # ── 3. Know Your Meme (trending meme database) ──
        if self.include_kym:
            kym_items = await self._scrape_know_your_meme()
            items.extend(kym_items)

        # ── 4. Imgflip (popular templates + trending) ──
        if self.include_imgflip:
            imgflip_items = await self._scrape_imgflip()
            items.extend(imgflip_items)

        logger.info(f"[memes] Total: {len(items)} meme/viral items scraped")
        return items[:self.max_items]

    # ═══════════════════════════════════════════════════════
    # Reddit Meme Subreddits
    # ═══════════════════════════════════════════════════════

    async def _scrape_reddit_memes(self) -> list[ScrapedItem]:
        """Scrape top/hot memes from meme-specific subreddits."""
        items = []
        seen_ids = set()

        for sub in self.meme_subreddits:
            if not self._check_limit():
                break

            for sort in ["hot", "rising"]:
                try:
                    self._rate_limit()
                    url = f"https://www.reddit.com/r/{sub}/{sort}.json?limit=10"
                    resp = await asyncio.to_thread(requests.get, url, headers=self.headers, timeout=15)

                    if resp.status_code == 429:
                        logger.warning(f"[memes] Reddit rate limited on r/{sub}")
                        await asyncio.sleep(10)
                        continue
                    if resp.status_code != 200:
                        continue

                    data = resp.json()
                    children = data.get("data", {}).get("children", [])

                    for child in children:
                        post = child.get("data", {})
                        if post.get("stickied"):
                            continue

                        post_id = post.get("id", "")
                        if not post_id or post_id in seen_ids:
                            continue
                        seen_ids.add(post_id)

                        title = post.get("title", "")
                        if not title:
                            continue

                        # Determine meme type
                        is_image = post.get("post_hint") == "image" or post.get("url", "").endswith((".jpg", ".png", ".gif"))
                        is_video = post.get("is_video", False) or post.get("post_hint") == "hosted:video"
                        meme_type = "video_meme" if is_video else ("image_meme" if is_image else "text_meme")

                        text_parts = [f"MEME TITLE: {title}"]
                        selftext = post.get("selftext", "")
                        if selftext:
                            text_parts.append(f"CONTEXT: {selftext[:500]}")

                        # Image URL for visual context
                        image_url = ""
                        if is_image:
                            image_url = post.get("url", "")
                            text_parts.append(f"IMAGE: {image_url}")

                        text_parts.append(
                            f"SUBREDDIT: r/{sub} | SORT: {sort} | TYPE: {meme_type} | "
                            f"SCORE: {post.get('score', 0)} | COMMENTS: {post.get('num_comments', 0)}"
                        )

                        # Add flair for meme categorization
                        flair = post.get("link_flair_text", "")
                        if flair:
                            text_parts.append(f"FLAIR/CATEGORY: {flair}")

                        text = "\n".join(text_parts)

                        content_id = ScrapedItem.generate_id("memes", post_id)
                        item = ScrapedItem(
                            platform="memes",
                            content_id=content_id,
                            title=f"🔥 Meme (r/{sub}): {title[:100]}",
                            text=text,
                            url=f"https://reddit.com{post.get('permalink', '')}",
                            author=post.get("author", ""),
                            metadata={
                                "subreddit": sub,
                                "sort": sort,
                                "meme_type": meme_type,
                                "image_url": image_url,
                                "flair": flair,
                                "upvote_ratio": post.get("upvote_ratio", 0),
                                "is_original_content": post.get("is_original_content", False),
                            },
                            like_count=post.get("score", 0),
                            comment_count=post.get("num_comments", 0),
                            published_at=datetime.utcfromtimestamp(post.get("created_utc", 0)) if post.get("created_utc") else None,
                        )
                        items.append(item)
                        self._items_scraped += 1

                except Exception as e:
                    logger.warning(f"[memes] Reddit r/{sub}/{sort} failed: {e}")

        logger.info(f"[memes] Scraped {len(items)} memes from Reddit")
        return items

    # ═══════════════════════════════════════════════════════
    # Reddit Viral / World Pulse
    # ═══════════════════════════════════════════════════════

    async def _scrape_reddit_viral(self) -> list[ScrapedItem]:
        """Scrape rising/popular posts from Reddit to get the world's pulse."""
        items = []
        seen_ids = set()

        for sub in self.viral_subreddits[:5]:  # Limit to top 5 viral subs
            if not self._check_limit():
                break

            try:
                self._rate_limit()
                # Use "rising" sort for early viral detection
                url = f"https://www.reddit.com/r/{sub}/rising.json?limit=10"
                resp = await asyncio.to_thread(requests.get, url, headers=self.headers, timeout=15)

                if resp.status_code == 429:
                    await asyncio.sleep(10)
                    continue
                if resp.status_code != 200:
                    continue

                data = resp.json()
                children = data.get("data", {}).get("children", [])

                for child in children:
                    post = child.get("data", {})
                    post_id = post.get("id", "")
                    if not post_id or post_id in seen_ids or post.get("stickied"):
                        continue
                    seen_ids.add(post_id)

                    title = post.get("title", "")
                    score = post.get("score", 0)

                    # Only include posts with some traction
                    if score < 10:
                        continue

                    text = f"VIRAL/RISING: {title}\n"
                    selftext = post.get("selftext", "")
                    if selftext:
                        text += f"\n{selftext[:800]}"
                    text += f"\n\nSUBREDDIT: r/{sub} | SCORE: {score} | COMMENTS: {post.get('num_comments', 0)}"

                    content_id = ScrapedItem.generate_id("memes", f"viral_{post_id}")
                    item = ScrapedItem(
                        platform="memes",
                        content_id=content_id,
                        title=f"🌍 Viral (r/{sub}): {title[:100]}",
                        text=text,
                        url=f"https://reddit.com{post.get('permalink', '')}",
                        author=post.get("author", ""),
                        metadata={
                            "subreddit": sub,
                            "type": "viral_rising",
                            "upvote_ratio": post.get("upvote_ratio", 0),
                        },
                        like_count=score,
                        comment_count=post.get("num_comments", 0),
                    )
                    items.append(item)
                    self._items_scraped += 1

            except Exception as e:
                logger.warning(f"[memes] Reddit viral r/{sub} failed: {e}")

        logger.info(f"[memes] Scraped {len(items)} viral/rising posts")
        return items

    # ═══════════════════════════════════════════════════════
    # Know Your Meme
    # ═══════════════════════════════════════════════════════

    async def _scrape_know_your_meme(self) -> list[ScrapedItem]:
        """Scrape trending memes from Know Your Meme."""
        if BeautifulSoup is None or requests is None:
            return []

        items = []
        urls_to_try = [
            "https://knowyourmeme.com/memes/trending",
            "https://knowyourmeme.com/memes/popular",
            "https://knowyourmeme.com/",
        ]

        for kym_url in urls_to_try:
            if items:
                break  # Already got data

            try:
                self._rate_limit()
                resp = await asyncio.to_thread(requests.get, kym_url, headers=self.web_headers, timeout=15)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                # Find meme entries
                entry_selectors = [
                    soup.find_all("td", class_="entry_header"),
                    soup.find_all("div", class_="entry"),
                    soup.find_all("a", class_="photo_wrapper"),
                    soup.find_all("h2"),
                ]

                for entries in entry_selectors:
                    if not entries:
                        continue

                    for entry in entries[:15]:
                        if not self._check_limit():
                            break

                        # Try to find the link and title
                        link_tag = entry.find("a") if entry.name != "a" else entry
                        if not link_tag or not link_tag.get("href"):
                            continue

                        href = link_tag.get("href", "")
                        if not href.startswith("http"):
                            href = f"https://knowyourmeme.com{href}"

                        # Skip non-meme links
                        if "/memes/" not in href and "/photos/" not in href:
                            continue

                        title = link_tag.get_text(strip=True)
                        if not title or len(title) < 3:
                            continue

                        # Get image if available
                        img = link_tag.find("img") or entry.find("img")
                        image_url = ""
                        if img:
                            image_url = img.get("data-src") or img.get("src") or ""

                        content_id = ScrapedItem.generate_id("memes", f"kym_{title[:30]}")

                        text = (
                            f"MEME: {title}\n"
                            f"SOURCE: Know Your Meme\n"
                            f"STATUS: Trending/Popular\n"
                        )
                        if image_url:
                            text += f"IMAGE: {image_url}\n"
                        text += (
                            f"\nThis meme is currently trending on Know Your Meme. "
                            f"Understanding this meme format could enable culturally relevant, "
                            f"shareable marketing content."
                        )

                        item = ScrapedItem(
                            platform="memes",
                            content_id=content_id,
                            title=f"😂 KYM Trending: {title[:80]}",
                            text=text,
                            url=href,
                            author="Know Your Meme",
                            metadata={
                                "source": "know_your_meme",
                                "type": "trending_meme",
                                "image_url": image_url,
                            },
                        )
                        items.append(item)
                        self._items_scraped += 1

                    if items:
                        break  # Got entries from this selector

            except Exception as e:
                logger.warning(f"[memes] Know Your Meme scrape failed: {e}")

        logger.info(f"[memes] Scraped {len(items)} from Know Your Meme")
        return items

    # ═══════════════════════════════════════════════════════
    # Imgflip — Popular Meme Templates
    # ═══════════════════════════════════════════════════════

    async def _scrape_imgflip(self) -> list[ScrapedItem]:
        """Scrape popular meme templates from Imgflip's public API + trending page."""
        if requests is None:
            return []

        items = []

        # ── Imgflip API (public, no auth) ──
        try:
            self._rate_limit()
            resp = await asyncio.to_thread(requests.get, "https://api.imgflip.com/get_memes", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                memes = data.get("data", {}).get("memes", [])

                for i, meme in enumerate(memes[:20]):
                    template_name = meme.get("name", "")
                    template_url = meme.get("url", "")
                    box_count = meme.get("box_count", 0)
                    width = meme.get("width", 0)
                    height = meme.get("height", 0)

                    content_id = ScrapedItem.generate_id("memes", f"imgflip_{meme.get('id', i)}")

                    text = (
                        f"MEME TEMPLATE: {template_name}\n"
                        f"TEMPLATE RANK: #{i + 1} most popular on Imgflip\n"
                        f"FORMAT: {box_count} text boxes, {width}x{height}px\n"
                        f"IMAGE: {template_url}\n\n"
                        f"This is one of the most-used meme templates on the internet. "
                        f"It can be adapted for marketing by replacing text with brand messaging. "
                        f"Consider using this format for relatable, shareable social content."
                    )

                    item = ScrapedItem(
                        platform="memes",
                        content_id=content_id,
                        title=f"🎭 Template #{i+1}: {template_name}",
                        text=text,
                        url=template_url,
                        author="Imgflip",
                        metadata={
                            "source": "imgflip",
                            "type": "meme_template",
                            "template_id": meme.get("id", ""),
                            "template_name": template_name,
                            "image_url": template_url,
                            "box_count": box_count,
                            "rank": i + 1,
                        },
                    )
                    items.append(item)
                    self._items_scraped += 1

        except Exception as e:
            logger.warning(f"[memes] Imgflip API failed: {e}")

        # ── Imgflip Trending page (web scrape) ──
        if BeautifulSoup:
            try:
                self._rate_limit()
                resp = await asyncio.to_thread(
                    requests.get,
                    "https://imgflip.com/",
                    headers=self.web_headers,
                    timeout=15,
                )
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")

                    # Find featured/trending memes on homepage
                    meme_divs = soup.find_all("div", class_="base-unit")
                    for div in meme_divs[:10]:
                        img = div.find("img")
                        link = div.find("a")
                        if not img or not link:
                            continue

                        title = img.get("alt", "") or link.get_text(strip=True)
                        href = link.get("href", "")
                        img_src = img.get("src", "")

                        if not title or not href:
                            continue

                        if not href.startswith("http"):
                            href = f"https://imgflip.com{href}"
                        if img_src and not img_src.startswith("http"):
                            img_src = f"https:{img_src}" if img_src.startswith("//") else f"https://imgflip.com{img_src}"

                        content_id = ScrapedItem.generate_id("memes", f"imgflip_trend_{title[:20]}")

                        item = ScrapedItem(
                            platform="memes",
                            content_id=content_id,
                            title=f"🎪 Imgflip Trending: {title[:80]}",
                            text=f"TRENDING MEME on Imgflip: {title}\nIMAGE: {img_src}\n\n"
                                 f"This meme is currently featured on Imgflip's homepage, "
                                 f"indicating high viral potential.",
                            url=href,
                            author="Imgflip",
                            metadata={
                                "source": "imgflip_trending",
                                "type": "trending_meme",
                                "image_url": img_src,
                            },
                        )
                        items.append(item)
                        self._items_scraped += 1

            except Exception as e:
                logger.warning(f"[memes] Imgflip trending scrape failed: {e}")

        logger.info(f"[memes] Scraped {len(items)} from Imgflip")
        return items
