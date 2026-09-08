"""
Document ingestion orchestrator: PDF parsing, chunking, embedding, and dual storage (SQLite + ChromaDB).
"""

import hashlib
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models.sql_models import Document, Medicine, DocumentStatus
from app.services.pdf_parser import pdf_parser
from app.services.chunking import chunker
from app.services.embedding_service import embedding_service
from app.db.vector_store import vector_store


class IngestionService:
    def process_pdf(
        self,
        db: Session,
        file_path: str,
        medicine_id: str,
        title: Optional[str] = None,
        source: str = "Official FDA Package Insert",
        original_filename: Optional[str] = None
    ) -> Document:
        """
        Process a PDF file through parsing, chunking, embedding generation,
        and indexing into ChromaDB and SQLite.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Verify medicine exists in DB
        medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not medicine:
            raise ValueError(f"Medicine '{medicine_id}' does not exist in the database.")

        filename = original_filename or path.name
        doc_title = title or path.stem.replace("_", " ").title()

        # Compute SHA-256 hash of file
        file_hash = self._compute_sha256(path)
        file_size = path.stat().st_size

        # Check if already ingested
        existing_doc = db.query(Document).filter(
            Document.file_hash == file_hash,
            Document.medicine_id == medicine_id
        ).first()

        if existing_doc and existing_doc.status == DocumentStatus.INDEXED:
            logger.info(f"Document '{filename}' already indexed for medicine '{medicine_id}'. Returning existing.")
            return existing_doc

        # Create or update document record in DB
        doc_record = existing_doc or Document(
            medicine_id=medicine_id,
            title=doc_title,
            source=source,
            filename=filename,
            file_path=str(path.resolve()),
            file_hash=file_hash,
            file_size_bytes=file_size,
            status=DocumentStatus.PROCESSING
        )
        if not existing_doc:
            db.add(doc_record)
        else:
            doc_record.status = DocumentStatus.PROCESSING
        db.commit()
        db.refresh(doc_record)

        try:
            logger.info(f"Starting extraction for document: {doc_record.id} ({filename})...")
            # Step 1: Extract pages & sections
            pages_data = pdf_parser.extract_pages(str(path))
            total_pages = len(pages_data)

            # Step 2: Chunk pages into semantic segments
            chunks = chunker.chunk_pages(
                pages_data=pages_data,
                document_id=doc_record.id,
                medicine_id=medicine_id,
                medicine_name=medicine.generic_name,
                source_title=doc_title
            )

            if not chunks:
                raise ValueError("No extractable text or chunks produced from this document.")

            logger.info(f"Generated {len(chunks)} chunks for '{filename}'. Computing embeddings...")

            # Step 3: Compute embeddings
            chunk_texts = [c["text"] for c in chunks]
            embeddings = embedding_service.embed_texts(chunk_texts)

            # Step 4: Index into ChromaDB
            chunk_ids = [c["id"] for c in chunks]
            metadatas = [c["metadata"] for c in chunks]
            vector_store.add_chunks(
                chunk_ids=chunk_ids,
                documents=chunk_texts,
                embeddings=embeddings,
                metadatas=metadatas
            )

            # Step 5: Mark document as INDEXED
            doc_record.total_pages = total_pages
            doc_record.total_chunks = len(chunks)
            doc_record.status = DocumentStatus.INDEXED
            doc_record.error_message = None
            db.commit()
            db.refresh(doc_record)

            logger.info(f"Document '{filename}' successfully indexed with {len(chunks)} chunks.")
            return doc_record

        except Exception as e:
            logger.error(f"Failed to process document '{filename}': {e}", exc_info=True)
            doc_record.status = DocumentStatus.FAILED
            doc_record.error_message = str(e)
            db.commit()
            raise

    def delete_document(self, db: Session, document_id: str) -> bool:
        """Remove a document from SQLite, ChromaDB, and disk."""
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return False

        # Delete chunks from ChromaDB
        vector_store.delete_document_chunks(document_id)

        # Remove physical file if in upload directory
        try:
            file_path = Path(doc.file_path)
            if file_path.exists() and "uploads" in str(file_path):
                file_path.unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Failed to delete physical file {doc.file_path}: {e}")

        # Delete from SQLite
        db.delete(doc)
        db.commit()
        return True

    def _compute_sha256(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()


ingestion_service = IngestionService()
