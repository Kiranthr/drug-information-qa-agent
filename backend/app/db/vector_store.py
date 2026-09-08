"""
ChromaDB Vector Store management for drug document chunk embeddings.
"""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.core.logging import logger

COLLECTION_NAME = "drug_documents"


class VectorStore:
    def __init__(self):
        settings.ensure_directories()
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        logger.info(f"Connecting to ChromaDB at: {self.persist_dir}")

        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Drug label and clinical documentation chunks for RAG"}
        )

    def count_chunks(self) -> int:
        """Return total indexed vector chunks in the collection."""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error counting ChromaDB chunks: {e}")
            return 0

    def add_chunks(
        self,
        chunk_ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """Add chunks, their embeddings, and metadata to ChromaDB."""
        if not chunk_ids:
            return

        self.collection.upsert(
            ids=chunk_ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        logger.info(f"Indexed {len(chunk_ids)} chunks into ChromaDB collection '{COLLECTION_NAME}'")

    def query_similar(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        medicine_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query for the most similar chunks.
        Optionally filter by medicine_id.
        Returns a list of dicts with: id, document, metadata, distance.
        """
        where_filter = None
        if medicine_id:
            where_filter = {"medicine_id": medicine_id}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []
        if results and "ids" in results and results["ids"] and len(results["ids"][0]) > 0:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            for i in range(len(ids)):
                # Convert distance to a similarity score (for cosine distance, similarity ~ 1 - distance)
                dist = distances[i]
                sim_score = max(0.0, 1.0 - (dist / 2.0))
                formatted_results.append({
                    "id": ids[i],
                    "document": docs[i],
                    "metadata": metas[i],
                    "distance": dist,
                    "similarity": round(sim_score, 4)
                })

        return formatted_results

    def delete_document_chunks(self, document_id: str) -> int:
        """Delete all chunks belonging to a specific document."""
        try:
            # First find matching chunks
            items = self.collection.get(where={"document_id": document_id})
            if items and items["ids"]:
                self.collection.delete(ids=items["ids"])
                deleted_count = len(items["ids"])
                logger.info(f"Deleted {deleted_count} chunks for document_id={document_id}")
                return deleted_count
            return 0
        except Exception as e:
            logger.error(f"Error deleting chunks for document {document_id}: {e}")
            return 0


# Global singleton instance
vector_store = VectorStore()
