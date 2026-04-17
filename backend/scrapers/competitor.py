"""
Competitor website scraper.
Crawls competitor websites for blog posts, product updates, and strategic intelligence.
Uses newspaper3k + BeautifulSoup for extraction.
"""

import asyncio
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse
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

try:
    from newspaper import Article
except ImportError:
    Article = None


@register_scraper
class CompetitorScraper(BaseScraper):
    """Scrapes competitor websites for strategic intelligence."""

    PLATFORM_NAME = "competitor"

    def __init__(
        self,
        competitors: Optional[list[dict]] = None,
        delay_seconds: float = 3.0,
        max_items: int = 50,
    ):
        super().__init__(
            platform="competitor",
            delay_seconds=delay_seconds,
            max_items=max_items,
        )
        self.competitors = competitors or []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _find_blog_urls(self, website: str) -> list[str]:
        """Discover blog/news URLs on a competitor's site."""
        blog_paths = [
            "/blog", "/blog/", "/news", "/news/", "/insights",
            "/resources", "/articles", "/updates", "/press",
        ]

        found_urls = []
        base_url = website.rstrip("/")

        for path in blog_paths:
            try:
                self._rate_limit()
                url = f"{base_url}{path}"
                resp = requests.get(url, headers=self.headers, timeout=10, allow_redirects=True)
                if resp.status_code == 200 and len(resp.text) > 1000:
                    found_urls.append(url)
                    break  # Found a working blog page
            except Exception:
                continue

        if not found_urls:
            found_urls.append(base_url)  # Fall back to homepage

        return found_urls

    def _extract_article_links(self, page_url: str, max_links: int = 10) -> list[str]:
        """Extract article links from a blog/listing page."""
        if BeautifulSoup is None:
            return []

        try:
            self._rate_limit()
            resp = requests.get(page_url, headers=self.headers, timeout=10)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            parsed_base = urlparse(page_url)
            base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"

            links = []
            seen = set()

            # Look for article links — usually in <a> tags within article containers
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]

                # Make absolute
                if href.startswith("/"):
                    href = f"{base_domain}{href}"
                elif not href.startswith("http"):
                    href = urljoin(page_url, href)

                # Filter to same domain
                if urlparse(href).netloc != parsed_base.netloc:
                    continue

                # Skip non-article links
                skip_patterns = [
                    "/tag/", "/category/", "/author/", "/page/",
                    "#", "javascript:", "/cdn-cgi/", "/wp-content/",
                    "/wp-admin/", "/login", "/register", "/cart",
                    "/checkout", "/search",
                ]
                if any(p in href.lower() for p in skip_patterns):
                    continue

                # Heuristic: article URLs are usually longer and contain date-like patterns
                path = urlparse(href).path
                if len(path) > 10 and href not in seen:
                    # Check if it looks like a blog post (has enough path segments)
                    segments = [s for s in path.split("/") if s]
                    if len(segments) >= 2:
                        seen.add(href)
                        links.append(href)

                if len(links) >= max_links:
                    break

            return links

        except Exception as e:
            logger.debug(f"[competitor] Failed to extract links from {page_url}: {e}")
            return []

    def _extract_article(self, url: str) -> Optional[dict]:
        """Extract full article content using newspaper3k."""
        if Article is None:
            return self._extract_article_basic(url)

        try:
            self._rate_limit()
            article = Article(url)
            article.download()
            article.parse()

            if not article.text or len(article.text) < 100:
                return None

            return {
                "title": article.title or "",
                "text": article.text[:5000],
                "authors": article.authors or [],
                "publish_date": article.publish_date,
                "meta_description": article.meta_description or "",
                "top_image": article.top_image or "",
                "tags": list(article.tags)[:10] if article.tags else [],
            }
        except Exception as e:
            logger.debug(f"[competitor] newspaper3k failed for {url}: {e}")
            return self._extract_article_basic(url)

    def _extract_article_basic(self, url: str) -> Optional[dict]:
        """Basic article extraction using BeautifulSoup (fallback)."""
        if BeautifulSoup is None:
            return None

        try:
            self._rate_limit()
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code != 200:
                return None

            soup = BeautifulSoup(resp.text, "html.parser")

            # Get title
            title = ""
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text().strip()
            if not title:
                h1 = soup.find("h1")
                if h1:
                    title = h1.get_text().strip()

            # Get meta description
            meta_desc = ""
            meta = soup.find("meta", attrs={"name": "description"})
            if meta:
                meta_desc = meta.get("content", "")

            # Get main text content
            # Remove script, style, nav, footer
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            # Try to find article/main content
            article = soup.find("article") or soup.find("main") or soup.find("div", class_=re.compile(r"content|post|article", re.I))
            if article:
                text = article.get_text(separator="\n", strip=True)
            else:
                text = soup.get_text(separator="\n", strip=True)

            # Clean up
            lines = [line.strip() for line in text.split("\n") if line.strip() and len(line.strip()) > 20]
            text = "\n".join(lines[:100])  # Cap at 100 meaningful lines

            if len(text) < 100:
                return None

            return {
                "title": title,
                "text": text[:5000],
                "authors": [],
                "publish_date": None,
                "meta_description": meta_desc,
                "top_image": "",
                "tags": [],
            }

        except Exception as e:
            logger.debug(f"[competitor] Basic extraction failed for {url}: {e}")
            return None

    async def scrape(self) -> list[ScrapedItem]:
        """Scrape competitor websites for strategic intelligence."""
        items = []

        for competitor in self.competitors:
            if not self._check_limit():
                break

            name = competitor.get("name", "Unknown")
            website = competitor.get("website", "")

            if not website:
                continue

            logger.info(f"[competitor] Scanning: {name} ({website})")

            # Step 1: Find blog/content pages
            blog_urls = await asyncio.to_thread(self._find_blog_urls, website)

            # Step 2: Extract article links
            all_article_links = []
            for blog_url in blog_urls:
                links = await asyncio.to_thread(self._extract_article_links, blog_url, 8)
                all_article_links.extend(links)

            logger.info(f"[competitor] Found {len(all_article_links)} article links for {name}")

            # Step 3: Extract each article
            for article_url in all_article_links[:10]:  # Max 10 per competitor
                if not self._check_limit():
                    break

                article = await asyncio.to_thread(self._extract_article, article_url)
                if not article:
                    continue

                content_id = ScrapedItem.generate_id("competitor", article_url)

                text = f"COMPETITOR: {name}\n\n"
                if article.get("meta_description"):
                    text += f"META: {article['meta_description']}\n\n"
                text += article.get("text", "")

                pub_date = article.get("publish_date")
                authors = ", ".join(article.get("authors", [])) or name

                item = ScrapedItem(
                    platform="competitor",
                    content_id=content_id,
                    title=f"[{name}] {article.get('title', 'Untitled')}",
                    text=text[:5000],
                    url=article_url,
                    author=authors,
                    metadata={
                        "competitor_name": name,
                        "competitor_website": website,
                        "meta_description": article.get("meta_description", ""),
                        "top_image": article.get("top_image", ""),
                        "tags": article.get("tags", []),
                    },
                    published_at=pub_date,
                )

                items.append(item)
                self._items_scraped += 1
                logger.debug(f"[competitor] Scraped: {article.get('title', '')[:60]}")

        logger.info(f"[competitor] Total: {len(items)} articles scraped")
        return items
