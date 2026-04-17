"""
Company profile configuration.
Defines your company, competitors, industry, and target audience.
This data feeds into scrapers (what to search for) and agents (context for generation).
"""

import os
import json
from typing import Optional
from loguru import logger

DEFAULT_PROFILE_PATH = "./data/company_profile.json"

DEFAULT_PROFILE = {
    "company": {
        "name": "Your Company",
        "industry": "Technology",
        "niche": "SaaS / Digital Marketing",
        "description": "We help businesses automate their marketing workflows with AI.",
        "website": "https://yourcompany.com",
        "brand_voice": "Professional yet approachable, data-driven, innovative",
        "target_audience": "Marketing managers, CMOs, and growth teams at mid-size companies",
        "unique_selling_points": [
            "AI-powered automation",
            "Free-tier friendly",
            "All-in-one marketing platform",
        ],
        "brand_primary_color": "#FF6B6B",
        "brand_secondary_color": "#4285F4",
        "brand_font_family": "Inter",
        "logo_url": "https://example.com/logo.png",
        "product_image_urls": [
            "https://example.com/product1.png"
        ],
    },
    "competitors": [
        {
            "name": "HubSpot",
            "website": "https://hubspot.com",
            "youtube_channel_id": "",
            "tiktok_handle": "",
            "strengths": "All-in-one platform, strong content marketing",
            "weaknesses": "Expensive for small teams",
        },
        {
            "name": "Mailchimp",
            "website": "https://mailchimp.com",
            "youtube_channel_id": "",
            "tiktok_handle": "",
            "strengths": "Email marketing leader, easy to use",
            "weaknesses": "Limited beyond email",
        },
    ],
    "content_focus": {
        "topics": [
            "marketing automation",
            "AI in marketing",
            "content strategy",
            "social media trends",
            "email marketing",
        ],
        "hashtags": [
            "digitalmarketing",
            "marketingtips",
            "contentmarketing",
            "socialmediamarketing",
            "AImarketing",
        ],
        "youtube_search_queries": [
            "marketing automation 2026",
            "AI marketing strategy",
            "social media marketing tips",
            "content marketing trends",
            "email marketing best practices",
        ],
        "rss_feeds": [
            "https://blog.hubspot.com/marketing/rss.xml",
            "https://contentmarketinginstitute.com/feed/",
            "https://www.socialmediaexaminer.com/feed/",
            "https://neilpatel.com/blog/feed/",
            "https://moz.com/feed",
            "https://sproutsocial.com/insights/feed/",
        ],
    },
    "platforms": {
        "youtube": True,
        "tiktok": True,
        "news_rss": True,
        "google_trends": True,
        "reddit": True,
        "twitter": True,
        "competitor": True,
        "memes": True,
    },
    "task_routes": {
        "trend_analysis": "balanced",
        "market_research": "balanced",
        "strategy_planning": "power",
        "seo_analysis": "balanced",
        "copy_generation": "power",
        "creative_direction": "power",
        "video_direction": "balanced",
        "media_buying": "balanced",
        "critic_review": "fast",
        "presentation": "balanced",
        "scoring": "fast",
    },
}


class CompanyProfile:
    """Manages the company profile that feeds into all modules."""

    def __init__(self, profile_path: str = DEFAULT_PROFILE_PATH):
        self.profile_path = profile_path
        self._data = None

    @property
    def data(self) -> dict:
        if self._data is None:
            self._data = self.load()
        return self._data

    def load(self) -> dict:
        """Load profile from disk, or create default."""
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, "r") as f:
                    data = json.load(f)
                logger.info(f"Loaded company profile: {data['company']['name']}")
                return data
            except Exception as e:
                logger.warning(f"Failed to load profile: {e}, using default")

        # Create default
        self.save(DEFAULT_PROFILE)
        return DEFAULT_PROFILE.copy()

    def save(self, data: dict) -> None:
        """Save profile to disk."""
        os.makedirs(os.path.dirname(self.profile_path) or ".", exist_ok=True)
        with open(self.profile_path, "w") as f:
            json.dump(data, f, indent=2)
        self._data = data
        logger.info(f"Saved company profile: {data['company']['name']}")

    def update(self, data: dict) -> dict:
        """Update profile with partial data (merges)."""
        current = self.data.copy()
        for key, value in data.items():
            if isinstance(value, dict) and key in current and isinstance(current[key], dict):
                current[key].update(value)
            else:
                current[key] = value
        self.save(current)
        return current

    # ── Convenience Getters ───────────────────────────────

    @property
    def company_name(self) -> str:
        return self.data["company"]["name"]

    @property
    def industry(self) -> str:
        return self.data["company"]["industry"]

    @property
    def niche(self) -> str:
        return self.data["company"]["niche"]

    @property
    def description(self) -> str:
        return self.data["company"]["description"]

    @property
    def brand_voice(self) -> str:
        return self.data["company"]["brand_voice"]

    @property
    def target_audience(self) -> str:
        return self.data["company"]["target_audience"]

    @property
    def brand_primary_color(self) -> str:
        return self.data["company"].get("brand_primary_color", "#000000")

    @property
    def brand_secondary_color(self) -> str:
        return self.data["company"].get("brand_secondary_color", "#FFFFFF")

    @property
    def brand_font_family(self) -> str:
        return self.data["company"].get("brand_font_family", "sans-serif")
        
    @property
    def logo_url(self) -> str:
        return self.data["company"].get("logo_url", "")
        
    @property
    def product_image_urls(self) -> list[str]:
        return self.data["company"].get("product_image_urls", [])

    @property
    def competitors(self) -> list[dict]:
        return self.data.get("competitors", [])

    @property
    def competitor_names(self) -> list[str]:
        return [c["name"] for c in self.competitors]

    @property
    def topics(self) -> list[str]:
        return self.data.get("content_focus", {}).get("topics", [])

    @property
    def hashtags(self) -> list[str]:
        return self.data.get("content_focus", {}).get("hashtags", [])

    @property
    def youtube_queries(self) -> list[str]:
        return self.data.get("content_focus", {}).get("youtube_search_queries", [])

    @property
    def rss_feeds(self) -> list[str]:
        return self.data.get("content_focus", {}).get("rss_feeds", [])

    @property
    def youtube_channel_ids(self) -> list[str]:
        """Collect YouTube channel IDs from competitors."""
        ids = []
        for c in self.competitors:
            cid = c.get("youtube_channel_id", "")
            if cid:
                ids.append(cid)
        return ids

    @property
    def tiktok_handles(self) -> list[str]:
        """Collect TikTok handles from competitors."""
        handles = []
        for c in self.competitors:
            handle = c.get("tiktok_handle", "")
            if handle:
                handles.append(handle)
        return handles

    @property
    def enabled_platforms(self) -> dict:
        return self.data.get("platforms", {})

    @property
    def task_routes(self) -> dict:
        return self.data.get("task_routes", {})

    def get_agent_context(self) -> str:
        """Generate context string for AI agents about the company."""
        competitors_str = ", ".join(self.competitor_names) if self.competitor_names else "N/A"
        usps = ", ".join(self.data["company"].get("unique_selling_points", []))

        return f"""COMPANY CONTEXT:
- Company: {self.company_name}
- Industry: {self.industry} / {self.niche}
- Description: {self.description}
- Brand Voice: {self.brand_voice}
- Target Audience: {self.target_audience}
- Unique Selling Points: {usps}
- Key Competitors: {competitors_str}
- Content Focus Topics: {', '.join(self.topics[:5])}

When generating content, always align with this brand voice and target audience.
Reference competitors where relevant for competitive positioning.
Focus on topics that matter to our audience in the {self.industry} space."""

    def to_dict(self) -> dict:
        """Return full profile as dict (for API responses)."""
        return self.data.copy()
