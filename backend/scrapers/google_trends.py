"""
Google Trends scraper — WORLD-WIDE multi-geo coverage.
Scrapes trending topics from multiple countries/regions simultaneously.
RSS primary (no deps, very reliable) + pytrends for interest-over-time.

Coverage:
  - Global real-time trends (multiple geos: US, IN, NP, GB, AU, CA, etc.)
  - Industry-specific keyword trends
  - Rising/breakout queries
  - Local language trending (Hindi, Nepali, etc.)
"""

import asyncio
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

from .base import BaseScraper, ScrapedItem, register_scraper

try:
    import requests
except ImportError:
    requests = None


# Geos to scrape — covers major markets + South Asia
DEFAULT_GEOS = [
    "",       # Worldwide / Global
    "US",     # United States
    "IN",     # India (Hindi trends)
    "NP",     # Nepal (Nepali trends)
    "GB",     # United Kingdom
    "AU",     # Australia
    "CA",     # Canada
    "DE",     # Germany
    "BR",     # Brazil
    "JP",     # Japan
    "NG",     # Nigeria
    "PH",     # Philippines
]

GEO_LABELS = {
    "": "Worldwide",
    "US": "United States",
    "IN": "India",
    "NP": "Nepal",
    "GB": "United Kingdom",
    "AU": "Australia",
    "CA": "Canada",
    "DE": "Germany",
    "BR": "Brazil",
    "JP": "Japan",
    "NG": "Nigeria",
    "PH": "Philippines",
}


@register_scraper
class GoogleTrendsScraper(BaseScraper):
    """Scrapes trending searches from multiple countries for full world coverage."""

    PLATFORM_NAME = "google_trends"

    # Google Trends RSS feeds (no API key, no pytrends dependency)
    TRENDING_RSS_URL = "https://trends.google.com/trending/rss?geo={geo}"
    REALTIME_RSS_URL = "https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"

    def __init__(
        self,
        industry_keywords: list[str] = None,
        geo: str = "",
        geos: list[str] = None,
        delay_seconds: float = 2.0,
        max_items: int = 100,
    ):
        super().__init__(platform="google_trends", delay_seconds=delay_seconds, max_items=max_items)
        self.industry_keywords = industry_keywords or [
            "marketing automation",
            "AI marketing",
            "social media",
        ]
        self.local_keywords = []
        self.local_configs = []
        self.geo = geo
        self.geos = geos or DEFAULT_GEOS
        self._pytrends = None
        self._pytrends_available = True

    def _get_pytrends(self):
        """Lazy init pytrends with retry-friendly config."""
        if self._pytrends is None:
            try:
                from pytrends.request import TrendReq
                self._pytrends = TrendReq(
                    hl="en-US",
                    tz=360,
                    timeout=(10, 25),
                    retries=3,
                    backoff_factor=1.0,
                )
            except ImportError:
                logger.warning("[GoogleTrends] pytrends not installed — using RSS only")
                self._pytrends_available = False
                return None
            except Exception as e:
                logger.warning(f"[GoogleTrends] pytrends init failed: {e}")
                self._pytrends_available = False
                return None
        return self._pytrends

    async def scrape(self) -> list[ScrapedItem]:
        """Fetch trending searches from MULTIPLE geos + industry keyword trends."""
        items = []

        # ── Part 1: WORLD TRENDS — RSS from multiple geos ──
        world_items = await self._get_world_trends_rss()
        items.extend(world_items)

        # ── Part 2: Industry-specific keyword trends (pytrends) ──
        if self._pytrends_available:
            iot_items = await self._get_industry_trends_pytrends()
            items.extend(iot_items)

            # Part 3: Related/rising queries
            related_items = await self._get_related_queries_pytrends()
            items.extend(related_items)

            # Part 4: Local language keyword trends
            local_items = await self._get_local_language_trends()
            items.extend(local_items)

        logger.info(f"[GoogleTrends] Collected {len(items)} trend items from {len(self.geos)} regions")
        return items[:self.max_items]

    async def _get_world_trends_rss(self) -> list[ScrapedItem]:
        """Get daily trending searches from MULTIPLE geos via RSS — full world coverage."""
        if requests is None:
            return []

        items = []

        for geo in self.geos:
            if len(items) >= self.max_items:
                break

            geo_label = GEO_LABELS.get(geo, geo or "Worldwide")
            logger.info(f"[GoogleTrends] Fetching trends for: {geo_label}")

            urls_to_try = [
                self.TRENDING_RSS_URL.format(geo=geo),
                self.REALTIME_RSS_URL.format(geo=geo),
            ]

            for rss_url in urls_to_try:
                try:
                    self._rate_limit()
                    resp = requests.get(
                        rss_url,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                            "Accept": "application/rss+xml,application/xml,text/xml",
                            "Accept-Language": "en-US,en;q=0.9,ne;q=0.8,hi;q=0.7",
                        },
                        timeout=15,
                    )

                    if resp.status_code != 200:
                        logger.debug(f"[GoogleTrends] RSS HTTP {resp.status_code} for {geo_label}")
                        continue

                    root = ET.fromstring(resp.text)
                    ns = {"ht": "https://trends.google.com/trending/rss"}
                    idx = 0

                    for item_elem in root.iter("item"):
                        if idx >= 10:  # Max 10 per geo to keep balanced
                            break

                        title = ""
                        description = ""
                        link = ""
                        traffic = ""

                        title_el = item_elem.find("title")
                        if title_el is not None:
                            title = title_el.text or ""

                        desc_el = item_elem.find("description")
                        if desc_el is not None:
                            description = desc_el.text or ""

                        link_el = item_elem.find("link")
                        if link_el is not None:
                            link = link_el.text or ""

                        traffic_el = item_elem.find("ht:approx_traffic", ns)
                        if traffic_el is not None:
                            traffic = traffic_el.text or ""
                        if not traffic:
                            traffic_el = item_elem.find("approx_traffic")
                            if traffic_el is not None:
                                traffic = traffic_el.text or ""

                        if not title:
                            continue

                        clean_desc = re.sub(r'<[^>]+>', '', description).strip()

                        text = (
                            f"'{title}' is currently trending on Google Search in {geo_label}. "
                        )
                        if traffic:
                            text += f"Approximate search volume: {traffic}. "
                        if clean_desc:
                            text += f"Related context: {clean_desc[:500]}. "
                        text += (
                            f"This represents a real-time spike in public interest in {geo_label}. "
                            f"Consider creating localized content if this aligns with your brand."
                        )

                        item = ScrapedItem(
                            platform="google_trends",
                            content_id=f"gtrend_{geo or 'world'}_{datetime.now().strftime('%Y%m%d')}_{idx}",
                            title=f"🌍 Trending ({geo_label}): {title}",
                            text=text,
                            url=link or f"https://trends.google.com/trends/explore?q={title.replace(' ', '+')}&geo={geo}",
                            author="Google Trends",
                            metadata={
                                "type": "world_trending",
                                "rank": idx + 1,
                                "query": title,
                                "traffic": traffic,
                                "geo": geo or "worldwide",
                                "geo_label": geo_label,
                                "source": "rss",
                            },
                        )
                        items.append(item)
                        idx += 1

                    if idx > 0:
                        logger.info(f"[GoogleTrends] Got {idx} trends from {geo_label}")
                        break  # Got data from first URL, skip second

                except ET.ParseError as e:
                    logger.debug(f"[GoogleTrends] RSS XML parse error for {geo_label}: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"[GoogleTrends] RSS fetch failed for {geo_label}: {e}")
                    continue

        logger.info(f"[GoogleTrends] Total world trends: {len(items)} from {len(self.geos)} regions")
        return items

    async def _get_industry_trends_pytrends(self) -> list[ScrapedItem]:
        """Get interest-over-time for industry keywords using pytrends."""
        pt = self._get_pytrends()
        if not pt:
            return []

        items = []
        try:
            for batch_start in range(0, len(self.industry_keywords), 5):
                batch = self.industry_keywords[batch_start:batch_start + 5]
                if not batch:
                    break

                self._rate_limit()
                await asyncio.sleep(2)

                try:
                    await asyncio.to_thread(
                        pt.build_payload,
                        kw_list=batch,
                        cat=0,
                        timeframe="now 7-d",
                        geo=self.geo,
                    )

                    iot = await asyncio.to_thread(pt.interest_over_time)
                except Exception as e:
                    if "429" in str(e) or "rate" in str(e).lower():
                        logger.warning("[GoogleTrends] pytrends rate limited — skipping industry trends")
                        self._pytrends_available = False
                        break
                    raise

                if iot.empty:
                    continue

                for keyword in batch:
                    if keyword not in iot.columns:
                        continue

                    series = iot[keyword]
                    avg_interest = float(series.mean())
                    peak_interest = float(series.max())
                    current = float(series.iloc[-1]) if len(series) > 0 else 0
                    trend_direction = "rising" if current > avg_interest else "declining"

                    item = ScrapedItem(
                        platform="google_trends",
                        content_id=f"gtrend_iot_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
                        title=f"📈 Industry Trend: {keyword}",
                        text=f"Google Trends data for '{keyword}' (past 7 days): "
                             f"Average interest: {avg_interest:.0f}/100, "
                             f"Peak: {peak_interest:.0f}/100, "
                             f"Current: {current:.0f}/100. "
                             f"Trend is {trend_direction}. "
                             f"{'This keyword is gaining momentum — good time to create content.' if trend_direction == 'rising' else 'Interest is cooling — consider a fresh angle.'}",
                        url=f"https://trends.google.com/trends/explore?q={keyword.replace(' ', '+')}",
                        author="Google Trends",
                        metadata={
                            "type": "industry_trend",
                            "keyword": keyword,
                            "avg_interest": avg_interest,
                            "peak_interest": peak_interest,
                            "current_interest": current,
                            "trend_direction": trend_direction,
                            "geo": self.geo or "Worldwide",
                            "source": "pytrends",
                        },
                    )
                    items.append(item)

                self._rate_limit()

            logger.info(f"[GoogleTrends] Got {len(items)} industry trend items")

        except Exception as e:
            logger.warning(f"[GoogleTrends] Industry trends failed: {e}")

        return items

    async def _get_related_queries_pytrends(self) -> list[ScrapedItem]:
        """Get related/rising queries for industry keywords using pytrends."""
        pt = self._get_pytrends()
        if not pt:
            return []

        items = []
        try:
            for batch_start in range(0, len(self.industry_keywords), 5):
                batch = self.industry_keywords[batch_start:batch_start + 5]
                if not batch:
                    break

                self._rate_limit()
                await asyncio.sleep(2)

                try:
                    await asyncio.to_thread(
                        pt.build_payload,
                        kw_list=batch,
                        timeframe="today 1-m",
                        geo=self.geo,
                    )

                    related = await asyncio.to_thread(pt.related_queries)
                except Exception as e:
                    if "429" in str(e) or "rate" in str(e).lower():
                        logger.warning("[GoogleTrends] pytrends rate limited — skipping related queries")
                        break
                    raise

                for keyword in batch:
                    if keyword not in related:
                        continue

                    kw_data = related[keyword]

                    # Rising queries (breakout opportunities)
                    if kw_data.get("rising") is not None and not kw_data["rising"].empty:
                        rising_df = kw_data["rising"].head(5)
                        rising_queries = []
                        for _, row in rising_df.iterrows():
                            q = row.get("query", "")
                            val = row.get("value", 0)
                            rising_queries.append(f"{q} ({val}% growth)")

                        if rising_queries:
                            item = ScrapedItem(
                                platform="google_trends",
                                content_id=f"gtrend_rising_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
                                title=f"🚀 Rising Queries for: {keyword}",
                                text=f"Breakout and rising search queries related to '{keyword}': "
                                     f"{', '.join(rising_queries)}. "
                                     f"These represent emerging search demand — "
                                     f"creating content around these terms could capture early traffic.",
                                url=f"https://trends.google.com/trends/explore?q={keyword.replace(' ', '+')}",
                                author="Google Trends",
                                metadata={
                                    "type": "rising_queries",
                                    "parent_keyword": keyword,
                                    "rising": rising_queries,
                                    "source": "pytrends",
                                },
                            )
                            items.append(item)

                    # Top queries (consistent interest)
                    if kw_data.get("top") is not None and not kw_data["top"].empty:
                        top_df = kw_data["top"].head(5)
                        top_queries = [row.get("query", "") for _, row in top_df.iterrows()]

                        if top_queries:
                            item = ScrapedItem(
                                platform="google_trends",
                                content_id=f"gtrend_top_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
                                title=f"🔥 Top Related Queries: {keyword}",
                                text=f"Most popular related searches for '{keyword}': "
                                     f"{', '.join(top_queries)}. "
                                     f"These are consistently searched terms — "
                                     f"use them in SEO and content targeting.",
                                url=f"https://trends.google.com/trends/explore?q={keyword.replace(' ', '+')}",
                                author="Google Trends",
                                metadata={
                                    "type": "top_queries",
                                    "parent_keyword": keyword,
                                    "top": top_queries,
                                    "source": "pytrends",
                                },
                            )
                            items.append(item)

                self._rate_limit()

            logger.info(f"[GoogleTrends] Got {len(items)} related query items")

        except Exception as e:
            logger.warning(f"[GoogleTrends] Related queries failed: {e}")

        return items

    async def _get_local_language_trends(self) -> list[ScrapedItem]:
        """Get trends for local language keywords via pytrends dynamically."""
        pt = self._get_pytrends()
        if not pt or not hasattr(self, 'local_configs') or not self.local_configs:
            return []

        items = []
        # local_configs should be passed dynamically e.g.:
        # [{"keywords": ["..."], "geo": "NP", "label": "Nepal (Nepali)"}]
        local_configs = getattr(self, "local_configs", [])

        for config in local_configs:
            try:
                self._rate_limit()
                await asyncio.sleep(3)

                await asyncio.to_thread(
                    pt.build_payload,
                    kw_list=config["keywords"][:5],
                    timeframe="now 7-d",
                    geo=config["geo"],
                )

                iot = await asyncio.to_thread(pt.interest_over_time)

                if iot.empty:
                    continue

                for keyword in config["keywords"]:
                    if keyword not in iot.columns:
                        continue

                    series = iot[keyword]
                    avg = float(series.mean())
                    current = float(series.iloc[-1]) if len(series) > 0 else 0
                    direction = "rising" if current > avg else "declining"

                    item = ScrapedItem(
                        platform="google_trends",
                        content_id=f"gtrend_local_{config['geo']}_{keyword[:10]}_{datetime.now().strftime('%Y%m%d')}",
                        title=f"🌏 Local Trend ({config['label']}): {keyword}",
                        text=f"Local language search trend for '{keyword}' in {config['label']}: "
                             f"Average interest: {avg:.0f}/100, Current: {current:.0f}/100. "
                             f"Trend direction: {direction}. "
                             f"Local language content creation opportunity — "
                             f"{'target this keyword for regional campaigns.' if direction == 'rising' else 'interest is cooling but may be ripe for counter-content.'}",
                        url=f"https://trends.google.com/trends/explore?q={keyword.replace(' ', '+')}&geo={config['geo']}",
                        author="Google Trends",
                        metadata={
                            "type": "local_language_trend",
                            "keyword": keyword,
                            "geo": config["geo"],
                            "region": config["label"],
                            "avg_interest": avg,
                            "current_interest": current,
                            "trend_direction": direction,
                            "source": "pytrends_local",
                        },
                    )
                    items.append(item)

            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower():
                    logger.warning(f"[GoogleTrends] Rate limited on local trends for {config['label']}")
                    break
                logger.warning(f"[GoogleTrends] Local trends failed for {config['label']}: {e}")

        logger.info(f"[GoogleTrends] Got {len(items)} local language trend items")
        return items
