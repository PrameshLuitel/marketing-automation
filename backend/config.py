"""
Central configuration for the Marketing Automation platform.
Loads from environment variables with sensible defaults.
GROQ-ONLY — no Gemini, no Mistral.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # ── Groq API Key (ONLY LLM provider) ─────────────────
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")

    # ── Groq Model Tiers ─────────────────────────────────
    groq_model_fast: str = Field(
        default="llama-3.1-8b-instant", env="GROQ_MODEL_FAST"
    )
    groq_model_balanced: str = Field(
        default="meta-llama/llama-4-scout-17b-16e-instruct", env="GROQ_MODEL_BALANCED"
    )
    groq_model_power: str = Field(
        default="llama-3.3-70b-versatile", env="GROQ_MODEL_POWER"
    )

    # ── Groq Rate Limiting ───────────────────────────────
    groq_daily_limit: int = Field(default=14000, env="GROQ_DAILY_LIMIT")
    groq_rate_limit_cooldown: int = Field(default=5, env="GROQ_RATE_LIMIT_COOLDOWN")

    # ── Database ──────────────────────────────────────────
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/marketing.db",
        env="DATABASE_URL",
    )
    chroma_persist_dir: str = Field(default="./data/chroma", env="CHROMA_PERSIST_DIR")
    output_dir: str = Field(default="./data/outputs", env="OUTPUT_DIR")

    # ── Notifications ─────────────────────────────────────
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: str = Field(default="", env="SMTP_USER")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    smtp_from: str = Field(default="", env="SMTP_FROM")
    notification_email_to: str = Field(default="", env="NOTIFICATION_EMAIL_TO")

    slack_webhook_url: str = Field(default="", env="SLACK_WEBHOOK_URL")

    telegram_bot_token: str = Field(default="", env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", env="TELEGRAM_CHAT_ID")

    # ── Scheduler ─────────────────────────────────────────
    scheduler_timezone: str = Field(default="UTC", env="SCHEDULER_TIMEZONE")
    scrape_hour: int = Field(default=2, env="SCRAPE_HOUR")
    analysis_hour: int = Field(default=3, env="ANALYSIS_HOUR")
    agents_hour: int = Field(default=4, env="AGENTS_HOUR")
    creative_hour: int = Field(default=5, env="CREATIVE_HOUR")

    # ── Rate Limits ───────────────────────────────────────
    max_items_per_platform: int = Field(default=200, env="MAX_ITEMS_PER_PLATFORM")
    scrape_delay_seconds: int = Field(default=2, env="SCRAPE_DELAY_SECONDS")

    # ── App ───────────────────────────────────────────────
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        env="CORS_ORIGINS",
    )

    # ── LLM Daily Budgets (requests) ──────────────────────
    budget_warning_pct: float = 0.85  # warn at 85% usage

    # ── RSS Feeds ─────────────────────────────────────────
    rss_feeds: list[str] = [
        "https://feeds.feedburner.com/TechCrunch",
        "https://blog.hubspot.com/marketing/rss.xml",
        "https://contentmarketinginstitute.com/feed/",
        "https://feeds.feedburner.com/searchengineland",
        "https://www.socialmediaexaminer.com/feed/",
        "https://neilpatel.com/blog/feed/",
        "https://moz.com/feed",
        "https://www.searchenginejournal.com/feed/",
    ]

    # ── YouTube Channels (for scraping) ───────────────────
    youtube_channel_ids: list[str] = [
        # Add target channel IDs here
    ]

    # ── Quality Gate ──────────────────────────────────────
    quality_threshold: float = 7.0
    max_retries: int = 2

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    # VideoDB
    videodb_api_key: Optional[str] = Field(default=None, env="VIDEO_DB_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
