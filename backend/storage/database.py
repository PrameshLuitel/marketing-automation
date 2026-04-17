"""
SQLite database models and CRUD operations.
Uses SQLAlchemy async with aiosqlite for non-blocking DB access.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Text, Float, Integer, Boolean, DateTime, JSON, Enum as SQLEnum,
    ForeignKey, Index, func
)
from datetime import datetime
from typing import Optional
import enum


# ── Base ──────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ── Enums ─────────────────────────────────────────────────

class Platform(str, enum.Enum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    NEWS = "news"
    RSS = "rss"
    GOOGLE_TRENDS = "google_trends"
    REDDIT = "reddit"
    TWITTER = "twitter"
    COMPETITOR = "competitor"


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AgentRole(str, enum.Enum):
    TREND_ANALYST = "trend_analyst"
    MARKET_RESEARCHER = "market_researcher"
    STRATEGY_PLANNER = "strategy_planner"
    SEO_SPECIALIST = "seo_specialist"
    COPYWRITER = "copywriter"
    CREATIVE_DIRECTOR = "creative_director"
    VIDEO_DIRECTOR = "video_director"
    MEDIA_BUYER = "media_buyer"
    PRESENTATION_DESIGNER = "presentation_designer"
    CRITIC = "critic"


class LLMProvider(str, enum.Enum):
    GROQ = "groq"


# ── Models ────────────────────────────────────────────────

class ScrapedContent(Base):
    """Raw scraped content from various platforms."""

    __tablename__ = "scraped_content"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(20), index=True)
    content_id: Mapped[str] = mapped_column(String(255), unique=True)
    title: Mapped[Optional[str]] = mapped_column(String(500))
    text: Mapped[str] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(String(1000))
    author: Mapped[Optional[str]] = mapped_column(String(255))
    metadata_json: Mapped[Optional[str]] = mapped_column(Text)  # JSON string
    view_count: Mapped[Optional[int]] = mapped_column(Integer)
    like_count: Mapped[Optional[int]] = mapped_column(Integer)
    comment_count: Mapped[Optional[int]] = mapped_column(Integer)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    analysis: Mapped[Optional["AnalysisResult"]] = relationship(
        back_populates="content", uselist=False
    )

    __table_args__ = (
        Index("ix_platform_scraped", "platform", "scraped_at"),
    )


class AnalysisResult(Base):
    """Sentiment, topic, and emotion analysis results."""

    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content_id: Mapped[int] = mapped_column(
        ForeignKey("scraped_content.id"), index=True
    )
    sentiment_label: Mapped[Optional[str]] = mapped_column(String(20))
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float)
    emotion_label: Mapped[Optional[str]] = mapped_column(String(50))
    emotion_scores: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    topic_id: Mapped[Optional[int]] = mapped_column(Integer)
    topic_label: Mapped[Optional[str]] = mapped_column(String(255))
    keywords: Mapped[Optional[str]] = mapped_column(Text)  # JSON list
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    content: Mapped["ScrapedContent"] = relationship(back_populates="analysis")

    __table_args__ = (
        Index("ix_sentiment_analyzed", "sentiment_label", "analyzed_at"),
        Index("ix_topic_analyzed", "topic_label", "analyzed_at"),
        Index("ix_emotion_analyzed", "emotion_label", "analyzed_at"),
    )


class Campaign(Base):
    """Generated campaign briefs from the agent council."""

    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(
        String(20), default=CampaignStatus.DRAFT.value, index=True
    )
    summary: Mapped[Optional[str]] = mapped_column(Text)
    target_audience: Mapped[Optional[str]] = mapped_column(Text)
    key_messages: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    social_copy: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    visual_direction: Mapped[Optional[str]] = mapped_column(Text)
    posting_schedule: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    trend_data: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    strategy: Mapped[Optional[str]] = mapped_column(Text)
    quality_score: Mapped[Optional[float]] = mapped_column(Float)
    critic_feedback: Mapped[Optional[str]] = mapped_column(Text)
    raw_scraped_data: Mapped[Optional[str]] = mapped_column(Text)
    debate_logs: Mapped[Optional[str]] = mapped_column(Text)
    video_script: Mapped[Optional[str]] = mapped_column(Text)
    run_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    brief_markdown: Mapped[Optional[str]] = mapped_column(Text)
    brief_pdf_path: Mapped[Optional[str]] = mapped_column(String(500))
    slides_json: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    assets: Mapped[list["CreativeAsset"]] = relationship(back_populates="campaign")


class CreativeAsset(Base):
    """Generated images, videos, and documents."""

    __tablename__ = "creative_assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    campaign_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("campaigns.id"), index=True
    )
    asset_type: Mapped[str] = mapped_column(String(20))  # image, video, pdf
    file_path: Mapped[str] = mapped_column(String(500))
    prompt: Mapped[Optional[str]] = mapped_column(Text)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    campaign: Mapped[Optional["Campaign"]] = relationship(back_populates="assets")


class AgentLog(Base):
    """Execution logs for agent council runs."""

    __tablename__ = "agent_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(50), index=True)
    agent_role: Mapped[str] = mapped_column(String(30))
    llm_provider: Mapped[str] = mapped_column(String(20))
    input_summary: Mapped[Optional[str]] = mapped_column(Text)
    output_summary: Mapped[Optional[str]] = mapped_column(Text)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    quality_score: Mapped[Optional[float]] = mapped_column(Float)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    error: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


class APIBudget(Base):
    """Daily API usage tracking per provider."""

    __tablename__ = "api_budget"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(20), index=True)
    date: Mapped[str] = mapped_column(String(10), index=True)  # YYYY-MM-DD
    requests_used: Mapped[int] = mapped_column(Integer, default=0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_provider_date", "provider", "date", unique=True),
    )


class PipelineRun(Base):
    """Tracks each full pipeline execution."""

    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(50), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="running")
    started_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    items_scraped: Mapped[int] = mapped_column(Integer, default=0)
    items_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    campaigns_generated: Mapped[int] = mapped_column(Integer, default=0)
    assets_created: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[Optional[str]] = mapped_column(Text)


# ── Database Engine & Session ─────────────────────────────

_engine = None
_session_factory = None


async def init_db(database_url: str = "sqlite+aiosqlite:///./data/marketing.db"):
    """Initialize the database engine and create all tables."""
    global _engine, _session_factory

    _engine = create_async_engine(database_url, echo=False)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get a database session."""
    if _session_factory is None:
        await init_db()
    async with _session_factory() as session:
        yield session


async def get_session_direct() -> AsyncSession:
    """Get a database session directly (not as a generator)."""
    if _session_factory is None:
        await init_db()
    return _session_factory()
