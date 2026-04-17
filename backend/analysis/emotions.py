"""
Local emotion detection using distilroberta.
Detects: anger, disgust, fear, joy, neutral, sadness, surprise.
Runs entirely local — no API calls.
"""

from loguru import logger


class EmotionAnalyzer:
    """Emotion detection using j-hartmann/emotion-english-distilroberta-base."""

    def __init__(self, model_name: str = "j-hartmann/emotion-english-distilroberta-base"):
        self.model_name = model_name
        self._pipeline = None

    @property
    def pipeline(self):
        if self._pipeline is None:
            logger.info(f"Loading emotion model: {self.model_name}")
            from transformers import pipeline
            self._pipeline = pipeline(
                "text-classification",
                model=self.model_name,
                top_k=None,
                truncation=True,
                max_length=512,
            )
            logger.success("Emotion model loaded")
        return self._pipeline

    def analyze(self, text: str) -> dict:
        """Analyze emotions in a single text."""
        try:
            truncated = text[:512]
            results = self.pipeline(truncated)

            if results and isinstance(results[0], list):
                scores = {r["label"]: round(r["score"], 4) for r in results[0]}
            elif results:
                scores = {r["label"]: round(r["score"], 4) for r in results}
            else:
                scores = {"neutral": 1.0}

            primary = max(scores, key=scores.get)

            return {
                "label": primary,
                "score": scores[primary],
                "all_scores": scores,
            }
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return {"label": "neutral", "score": 0.5, "all_scores": {}}

    def analyze_batch(self, texts: list[str]) -> list[dict]:
        results = []
        for text in texts:
            results.append(self.analyze(text))
        return results
