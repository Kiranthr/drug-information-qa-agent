"""
Core RAG (Retrieval-Augmented Generation) Orchestration Pipeline.
Integrates Safety Guardrails, Vector Similarity Search, Gemini Generation, and Citation Binding.
"""

import re
import uuid
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models.sql_models import Medicine, ChatSession, ChatMessage
from app.models.schemas import (
    ChatQueryResponse,
    Citation,
    SafetyMetadata
)
from app.services.safety_service import safety_service
from app.services.embedding_service import embedding_service
from app.db.vector_store import vector_store
from app.services.llm_service import llm_service


class RAGService:
    def answer_query(
        self,
        db: Session,
        question: str,
        medicine_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> ChatQueryResponse:
        """
        Complete end-to-end RAG workflow with multi-shield medical safety.
        """
        now = datetime.now(timezone.utc)

        # Ensure or create chat session
        session = self._get_or_create_session(db, session_id)

        # Store user query message
        user_msg = ChatMessage(
            session_id=session.id,
            role="user",
            content=question,
            created_at=now
        )
        db.add(user_msg)
        db.commit()

        # =======================================================
        # Step 1: Safety Pre-Evaluation (Emergency / Overdose Shield)
        # =======================================================
        safety_meta, immediate_emergency_text = safety_service.evaluate_query(question, db)

        if immediate_emergency_text:
            # Immediate Emergency Intervention: bypass vector search and LLM
            logger.warning(f"Bypassing RAG for emergency response on query: {question}")
            bot_msg = ChatMessage(
                session_id=session.id,
                role="assistant",
                content=immediate_emergency_text,
                citations_json="[]",
                safety_flags_json=json.dumps(safety_meta.model_dump()),
                created_at=datetime.now(timezone.utc)
            )
            db.add(bot_msg)
            db.commit()

            return ChatQueryResponse(
                answer=immediate_emergency_text,
                citations=[],
                safety_metadata=safety_meta,
                session_id=session.id,
                message_id=bot_msg.id,
                created_at=bot_msg.created_at
            )

        # =======================================================
        # Step 2: Medicine / Entity Resolution
        # =======================================================
        resolved_medicine = self._resolve_target_medicine(db, question, medicine_id)
        target_med_id = resolved_medicine.id if resolved_medicine else None
        target_med_name = resolved_medicine.generic_name if resolved_medicine else None

        # =======================================================
        # Step 3: Embed Query & Vector Search
        # =======================================================
        query_embedding = embedding_service.embed_query(question)
        retrieved_chunks = vector_store.query_similar(
            query_embedding=query_embedding,
            top_k=settings.MAX_RETRIEVAL_CHUNKS,
            medicine_id=target_med_id
        )

        # =======================================================
        # Step 4: Relevance & Grounding Gate
        # =======================================================
        # Filter chunks by minimum similarity threshold
        relevant_chunks = [
            c for c in retrieved_chunks
            if c.get("similarity", 0.0) >= 0.25 or c.get("distance", 1.0) <= settings.SIMILARITY_THRESHOLD
        ]

        if not relevant_chunks:
            logger.info(f"No sufficiently relevant chunks found for question: '{question}'")
            uncertainty_text = safety_service.build_uncertainty_response(target_med_name)
            final_answer = safety_service.append_disclaimer(uncertainty_text)

            safety_meta.classification = "UNCERTAIN_ABSENT_FROM_DOCS"
            safety_meta.action_taken = "REFUSED_UNGROUNDED"

            bot_msg = ChatMessage(
                session_id=session.id,
                role="assistant",
                content=final_answer,
                citations_json="[]",
                safety_flags_json=json.dumps(safety_meta.model_dump()),
                created_at=datetime.now(timezone.utc)
            )
            db.add(bot_msg)
            db.commit()

            return ChatQueryResponse(
                answer=final_answer,
                citations=[],
                safety_metadata=safety_meta,
                session_id=session.id,
                message_id=bot_msg.id,
                created_at=bot_msg.created_at
            )

        # =======================================================
        # Step 5: Grounded LLM Generation (Gemini 2.5 Flash)
        # =======================================================
        generated_answer = llm_service.generate_grounded_answer(
            question=question,
            context_chunks=relevant_chunks,
            safety_context=safety_meta.model_dump()
        )

        # =======================================================
        # Step 6: Citations Extraction & Verification
        # =======================================================
        citations = self._bind_citations(generated_answer, relevant_chunks)

        # =======================================================
        # Step 7: Disclaimer Append & Persistence
        # =======================================================
        final_answer = safety_service.append_disclaimer(generated_answer)

        citations_payload = [c.model_dump() for c in citations]
        bot_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=final_answer,
            citations_json=json.dumps(citations_payload),
            safety_flags_json=json.dumps(safety_meta.model_dump()),
            created_at=datetime.now(timezone.utc)
        )
        db.add(bot_msg)
        db.commit()

        return ChatQueryResponse(
            answer=final_answer,
            citations=citations,
            safety_metadata=safety_meta,
            session_id=session.id,
            message_id=bot_msg.id,
            created_at=bot_msg.created_at
        )

    def _get_or_create_session(self, db: Session, session_id: Optional[str]) -> ChatSession:
        """Fetch existing session or create a new one."""
        if session_id:
            existing = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if existing:
                return existing

        new_session = ChatSession(
            id=str(uuid.uuid4()),
            title="Drug Consultation"
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session

    def _resolve_target_medicine(
        self,
        db: Session,
        question: str,
        explicit_medicine_id: Optional[str]
    ) -> Optional[Medicine]:
        """Resolve target medicine either from parameter or question text matching."""
        if explicit_medicine_id:
            med = db.query(Medicine).filter(Medicine.id == explicit_medicine_id).first()
            if med:
                return med

        # Scan database medicines
        medicines = db.query(Medicine).all()
        q_lower = question.lower()
        for med in medicines:
            if med.generic_name.lower() in q_lower or med.id.lower() in q_lower:
                return med
            if med.brand_names:
                brands = [b.strip().lower() for b in med.brand_names.split(",")]
                if any(b in q_lower for b in brands):
                    return med

        return None

    def _bind_citations(
        self,
        answer: str,
        relevant_chunks: List[Dict[str, Any]]
    ) -> List[Citation]:
        """
        Identify which [Source X] references are in the answer and bind them
        to their exact document metadata, page numbers, and excerpts.
        """
        citations = []
        cited_indices = set(re.findall(r"\[Source\s+(\d+)\]", answer, re.IGNORECASE))

        # If specific sources were cited, attach those
        if cited_indices:
            for idx_str in sorted(cited_indices, key=int):
                idx = int(idx_str) - 1
                if 0 <= idx < len(relevant_chunks):
                    chunk = relevant_chunks[idx]
                    meta = chunk.get("metadata", {})
                    excerpt = chunk.get("document", "")
                    if "]\n\n" in excerpt:
                        excerpt = excerpt.split("]\n\n", 1)[1]
                    elif "]\n" in excerpt:
                        excerpt = excerpt.split("]\n", 1)[1]

                    citations.append(Citation(
                        source_title=meta.get("source_title", "Official Drug Label"),
                        medicine_name=meta.get("medicine_name", "General"),
                        page_number=meta.get("page_number", 1),
                        section_name=meta.get("section_name", "General"),
                        excerpt=excerpt[:280].strip() + ("..." if len(excerpt) > 280 else ""),
                        relevance_score=chunk.get("similarity")
                    ))

        # Fallback: if model didn't output [Source X] tags, attach top 2 chunks as references
        if not citations and relevant_chunks:
            for chunk in relevant_chunks[:2]:
                meta = chunk.get("metadata", {})
                excerpt = chunk.get("document", "")
                if "]\n\n" in excerpt:
                    excerpt = excerpt.split("]\n\n", 1)[1]
                citations.append(Citation(
                    source_title=meta.get("source_title", "Official Drug Label"),
                    medicine_name=meta.get("medicine_name", "General"),
                    page_number=meta.get("page_number", 1),
                    section_name=meta.get("section_name", "General"),
                    excerpt=excerpt[:280].strip() + ("..." if len(excerpt) > 280 else ""),
                    relevance_score=chunk.get("similarity")
                ))

        return citations


rag_service = RAGService()
