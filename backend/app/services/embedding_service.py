"""
Embedding service supporting local SentenceTransformers and Google Gemini embeddings.
"""

from typing import List
from app.core.config import settings
from app.core.logging import logger

_local_model = None


def get_local_model():
    """Lazy load SentenceTransformer to optimize memory and startup time."""
    global _local_model
    if _local_model is None:
        logger.info(f"Loading local embedding model: {settings.EMBEDDING_MODEL}...")
        from sentence_transformers import SentenceTransformer
        _local_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Local embedding model loaded successfully.")
    return _local_model


class EmbeddingService:
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER.lower()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a list of text strings."""
        if not texts:
            return []

        if self.provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                return self._embed_gemini(texts)
            except Exception as e:
                logger.warning(f"Gemini embedding failed ({e}), falling back to local SentenceTransformer")
                return self._embed_local(texts)
        else:
            return self._embed_local(texts)

    def embed_query(self, query: str) -> List[float]:
        """Generate vector embedding for a single search query."""
        results = self.embed_texts([query])
        return results[0] if results else []

    def _embed_local(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local sentence-transformers."""
        model = get_local_model()
        embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return embeddings.tolist()

    def _embed_gemini(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using official Google GenAI SDK."""
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        results = []
        # Process in batches of 20
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = client.models.embed_content(
                model="text-embedding-004",
                contents=batch,
            )
            for embedding in response.embeddings:
                results.append(embedding.values)

        return results


# Global singleton
embedding_service = EmbeddingService()
