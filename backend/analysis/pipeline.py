"""
Analysis pipeline orchestrator.
Runs: Sentiment → Topics → Emotions and produces structured JSON briefs.
"""

import json
from datetime import datetime
from typing import Optional
from loguru import logger

from .sentiment import SentimentAnalyzer
from .emotions import EmotionAnalyzer
from .topics import TopicModeler


class AnalysisPipeline:
    """Orchestrates the full analysis pipeline across all scraped content."""

    def __init__(self):
        self.sentiment = SentimentAnalyzer()
        self.emotions = EmotionAnalyzer()
        self.topics = TopicModeler()

    async def run(self, items: list[dict]) -> dict:
        """
        Run the full analysis pipeline on scraped items.

        Args:
            items: List of dicts with at least 'text' and 'content_id' keys

        Returns:
            Structured analysis brief as a dict
        """
        if not items:
            return self._empty_brief()

        texts = [item["text"] for item in items]
        logger.info(f"Running analysis pipeline on {len(texts)} items")

        # ── Step 1: Sentiment Analysis ────────────────────
        logger.info("Step 1/3: Sentiment analysis")
        sentiment_results = self.sentiment.analyze_batch(texts)

        # ── Step 2: Topic Modeling ────────────────────────
        logger.info("Step 2/3: Topic modeling")
        topic_results = self.topics.fit_and_extract(texts)

        # ── Step 3: Emotion Detection ─────────────────────
        logger.info("Step 3/3: Emotion detection")
        emotion_results = self.emotions.analyze_batch(texts)

        # ── Compile Results ───────────────────────────────
        # Per-item results
        item_analyses = []
        for i, item in enumerate(items):
            item_analyses.append({
                "content_id": item.get("content_id", f"item_{i}"),
                "platform": item.get("platform", "unknown"),
                "title": item.get("title", ""),
                "sentiment": sentiment_results[i] if i < len(sentiment_results) else None,
                "emotion": emotion_results[i] if i < len(emotion_results) else None,
                "topic_id": (
                    topic_results["text_topics"][i]["topic_id"]
                    if i < len(topic_results.get("text_topics", []))
                    else -1
                ),
            })

        # Aggregate statistics
        sentiment_summary = self._aggregate_sentiments(sentiment_results)
        emotion_summary = self._aggregate_emotions(emotion_results)
        top_trends = self._extract_top_trends(topic_results, items)
        emotional_hooks = self._extract_emotional_hooks(emotion_results, items)

        brief = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_items_analyzed": len(items),
            "top_trends": top_trends,
            "sentiment_scores": sentiment_summary,
            "emotion_summary": emotion_summary,
            "emotional_hooks": emotional_hooks,
            "topic_clusters": topic_results.get("topics", []),
            "competitive_gaps": self._identify_gaps(topic_results, sentiment_results),
            "item_analyses": item_analyses,
            "platforms_covered": list(set(item.get("platform", "") for item in items)),
        }

        logger.success(
            f"Analysis complete: {len(top_trends)} trends, "
            f"{topic_results.get('num_topics', 0)} topics, "
            f"sentiment={sentiment_summary.get('overall', 'n/a')}"
        )

        return brief

    def _aggregate_sentiments(self, results: list[dict]) -> dict:
        """Aggregate sentiment scores across all items."""
        if not results:
            return {"overall": "neutral", "positive_pct": 0, "negative_pct": 0, "neutral_pct": 100}

        counts = {"positive": 0, "negative": 0, "neutral": 0}
        for r in results:
            label = r.get("label", "neutral").lower()
            if "pos" in label:
                counts["positive"] += 1
            elif "neg" in label:
                counts["negative"] += 1
            else:
                counts["neutral"] += 1

        total = len(results)
        return {
            "overall": max(counts, key=counts.get),
            "positive_pct": round(counts["positive"] / total * 100, 1),
            "negative_pct": round(counts["negative"] / total * 100, 1),
            "neutral_pct": round(counts["neutral"] / total * 100, 1),
            "total_analyzed": total,
        }

    def _aggregate_emotions(self, results: list[dict]) -> dict:
        """Aggregate emotion distribution."""
        if not results:
            return {}

        emotion_counts = {}
        for r in results:
            label = r.get("label", "neutral")
            emotion_counts[label] = emotion_counts.get(label, 0) + 1

        total = len(results)
        return {
            emotion: {
                "count": count,
                "percentage": round(count / total * 100, 1),
            }
            for emotion, count in sorted(emotion_counts.items(), key=lambda x: -x[1])
        }

    def _extract_top_trends(self, topic_results: dict, items: list[dict]) -> list[dict]:
        """Extract top trends from topic modeling results."""
        trends = []
        for topic in topic_results.get("topics", [])[:10]:
            # Find representative items for this topic
            topic_items = [
                tt for tt in topic_results.get("text_topics", [])
                if tt["topic_id"] == topic["topic_id"]
            ]

            trends.append({
                "topic_id": topic["topic_id"],
                "name": topic.get("name", ""),
                "keywords": topic.get("keywords", [])[:5],
                "volume": topic.get("count", 0),
                "relevance_score": round(
                    topic.get("count", 0) / max(len(items), 1), 3
                ),
            })

        return sorted(trends, key=lambda x: -x["volume"])

    def _extract_emotional_hooks(self, emotion_results: list[dict], items: list[dict]) -> list[dict]:
        """Find content with strong emotional signals for campaign hooks."""
        hooks = []
        for i, (result, item) in enumerate(zip(emotion_results, items)):
            score = result.get("score", 0)
            label = result.get("label", "neutral")

            # Only include strong emotional signals
            if score > 0.7 and label != "neutral":
                hooks.append({
                    "emotion": label,
                    "score": score,
                    "title": item.get("title", "")[:100],
                    "text_preview": item.get("text", "")[:200],
                    "platform": item.get("platform", ""),
                })

        return sorted(hooks, key=lambda x: -x["score"])[:10]

    def _identify_gaps(self, topic_results: dict, sentiment_results: list[dict]) -> list[str]:
        """Identify potential competitive gaps based on topic/sentiment analysis."""
        gaps = []

        # Topics with negative sentiment = opportunity
        negative_count = sum(1 for r in sentiment_results if "neg" in r.get("label", "").lower())
        if negative_count > len(sentiment_results) * 0.3:
            gaps.append("High negative sentiment detected — opportunity to provide positive counter-narrative")

        # Low-volume topics that are emerging
        for topic in topic_results.get("topics", []):
            if topic.get("count", 0) <= 3:
                keywords = ", ".join(topic.get("keywords", [])[:3])
                gaps.append(f"Emerging topic ({keywords}) — early mover advantage possible")

        return gaps[:5]

    def _empty_brief(self) -> dict:
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "total_items_analyzed": 0,
            "top_trends": [],
            "sentiment_scores": {},
            "emotion_summary": {},
            "emotional_hooks": [],
            "topic_clusters": [],
            "competitive_gaps": [],
            "item_analyses": [],
            "platforms_covered": [],
        }
