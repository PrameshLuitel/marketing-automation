"""
ChromaDB vector store for semantic search over scraped content.
Runs fully embedded (no server needed).
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import Optional
from loguru import logger
import os


class EmbeddingStore:
    """Manages ChromaDB for semantic search over marketing content."""

    def __init__(self, persist_dir: str = "./data/chroma"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        # Initialize ChromaDB in persistent embedded mode
        self.client = chromadb.PersistentClient(path=persist_dir)

        # Sentence transformer for embeddings (384-dim, lightweight)
        self._model = None

        # Collections
        self.content_collection = self.client.get_or_create_collection(
            name="scraped_content",
            metadata={"description": "Scraped marketing content embeddings"},
        )
        self.campaign_collection = self.client.get_or_create_collection(
            name="campaigns",
            metadata={"description": "Generated campaign brief embeddings"},
        )

        logger.info(
            f"ChromaDB initialized | Content: {self.content_collection.count()} docs | "
            f"Campaigns: {self.campaign_collection.count()} docs"
        )

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the sentence transformer model."""
        if self._model is None:
            logger.info("Loading sentence-transformers model: all-MiniLM-L6-v2")
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def add_content(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[dict] = None,
    ) -> None:
        """Add or update a content document in the vector store."""
        try:
            embeddings = self._embed([text])
            self.content_collection.upsert(
                ids=[doc_id],
                embeddings=embeddings,
                documents=[text],
                metadatas=[metadata or {}],
            )
        except Exception as e:
            logger.error(f"Failed to add content {doc_id}: {e}")

    def add_content_batch(
        self,
        doc_ids: list[str],
        texts: list[str],
        metadatas: Optional[list[dict]] = None,
    ) -> None:
        """Batch add/update content documents."""
        if not doc_ids:
            return

        try:
            embeddings = self._embed(texts)
            self.content_collection.upsert(
                ids=doc_ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas or [{} for _ in doc_ids],
            )
            logger.info(f"Added {len(doc_ids)} documents to content collection")
        except Exception as e:
            logger.error(f"Batch add failed: {e}")

    def search_content(
        self,
        query: str,
        n_results: int = 10,
        platform_filter: Optional[str] = None,
    ) -> list[dict]:
        """Search for similar content using semantic search."""
        query_embedding = self._embed([query])

        where_filter = None
        if platform_filter:
            where_filter = {"platform": platform_filter}

        results = self.content_collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "similarity": 1 - results["distances"][0][i],
            })

        return output

    def add_campaign(
        self,
        campaign_id: str,
        text: str,
        metadata: Optional[dict] = None,
    ) -> None:
        """Add a campaign brief to the vector store."""
        try:
            embeddings = self._embed([text])
            self.campaign_collection.upsert(
                ids=[campaign_id],
                embeddings=embeddings,
                documents=[text],
                metadatas=[metadata or {}],
            )
        except Exception as e:
            logger.error(f"Failed to add campaign {campaign_id}: {e}")

    def search_campaigns(
        self,
        query: str,
        n_results: int = 5,
    ) -> list[dict]:
        """Search similar past campaigns."""
        query_embedding = self._embed([query])
        results = self.campaign_collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "similarity": 1 - results["distances"][0][i],
            })

        return output

    def get_stats(self) -> dict:
        """Get vector store statistics."""
        return {
            "content_count": self.content_collection.count(),
            "campaign_count": self.campaign_collection.count(),
            "persist_dir": self.persist_dir,
        }
