"""
Local sentiment analysis using HuggingFace transformers.
Runs entirely on CPU — no API calls, no costs.
"""

from typing import Optional
from loguru import logger


class SentimentAnalyzer:
    """Sentiment analysis using a local transformer model."""

    def __init__(self, model_name: str = "tabularisai/multilingual-sentiment-analysis"):
        self.model_name = model_name
        self._pipeline = None

    @property
    def pipeline(self):
        """Lazy load the sentiment pipeline."""
        if self._pipeline is None:
            logger.info(f"Loading sentiment model: {self.model_name}")
            from transformers import pipeline
            self._pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                top_k=None,
                truncation=True,
                max_length=512,
            )
            logger.success("Sentiment model loaded")
        return self._pipeline

    def analyze(self, text: str) -> dict:
        """Analyze sentiment of a single text."""
        try:
            # Truncate long texts
            truncated = text[:512]
            results = self.pipeline(truncated)

            if results and isinstance(results[0], list):
                scores = {r["label"].lower(): round(r["score"], 4) for r in results[0]}
            elif results:
                scores = {r["label"].lower(): round(r["score"], 4) for r in results}
            else:
                scores = {"neutral": 1.0}

            # Determine primary label
            primary = max(scores, key=scores.get)

            return {
                "label": primary,
                "score": scores[primary],
                "all_scores": scores,
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"label": "neutral", "score": 0.5, "all_scores": {}}

    def analyze_batch(self, texts: list[str]) -> list[dict]:
        """Analyze sentiment for a batch of texts."""
        results = []
        for text in texts:
            results.append(self.analyze(text))
        return results
