"""
BERTopic local topic modeling.
Discovers trending topic clusters from scraped content.
"""

from typing import Optional
from loguru import logger


class TopicModeler:
    """Topic modeling using BERTopic (runs locally)."""

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            logger.info("Initializing BERTopic model")
            from bertopic import BERTopic
            self._model = BERTopic(
                embedding_model="all-MiniLM-L6-v2",
                min_topic_size=3,
                nr_topics="auto",
                verbose=False,
            )
            logger.success("BERTopic model initialized")
        return self._model

    def fit_and_extract(self, texts: list[str]) -> dict:
        """Fit BERTopic on texts and extract topic information."""
        if len(texts) < 5:
            logger.warning("Not enough texts for topic modeling (need >= 5)")
            return {"topics": [], "topic_info": []}

        try:
            topics, probs = self.model.fit_transform(texts)

            # Get topic info
            topic_info = self.model.get_topic_info()
            topic_details = []

            for _, row in topic_info.iterrows():
                topic_id = row["Topic"]
                if topic_id == -1:  # Skip outlier topic
                    continue

                topic_words = self.model.get_topic(topic_id)
                topic_details.append({
                    "topic_id": int(topic_id),
                    "name": row.get("Name", f"Topic {topic_id}"),
                    "count": int(row.get("Count", 0)),
                    "keywords": [word for word, _ in (topic_words or [])[:10]],
                    "keyword_scores": {
                        word: round(score, 4) for word, score in (topic_words or [])[:10]
                    },
                })

            # Map each text to its topic
            text_topics = []
            for i, (topic_id, prob) in enumerate(zip(topics, probs)):
                text_topics.append({
                    "text_index": i,
                    "topic_id": int(topic_id),
                    "probability": float(prob) if not hasattr(prob, '__len__') else float(max(prob)),
                })

            return {
                "topics": topic_details,
                "text_topics": text_topics,
                "num_topics": len(topic_details),
            }

        except Exception as e:
            logger.error(f"Topic modeling failed: {e}")
            return {"topics": [], "text_topics": [], "num_topics": 0}
