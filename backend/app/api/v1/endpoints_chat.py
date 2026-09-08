"""
Chat and Q&A endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.sql_models import ChatSession
from app.models.schemas import (
    ChatQueryRequest,
    ChatQueryResponse,
    ChatSessionResponse
)
from app.services.rag_service import rag_service

router = APIRouter(prefix="/chat", tags=["Chat & RAG Q&A"])


@router.post("/query", response_model=ChatQueryResponse)
def ask_drug_question(payload: ChatQueryRequest, db: Session = Depends(get_db)):
    """
    Ask a question about a medicine and receive an evidence-grounded answer with citations.
    """
    try:
        response = rag_service.answer_query(
            db=db,
            question=payload.question,
            medicine_id=payload.medicine_id,
            session_id=payload.session_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.get("/history/{session_id}", response_model=ChatSessionResponse)
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """
    Retrieve conversation message history for a specific chat session.
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session
