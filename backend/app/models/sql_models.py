"""
SQLAlchemy database models for the Drug Information Q&A Agent.
"""

import uuid
from datetime import datetime, timezone
import json
from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class DocumentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    INDEXED = "INDEXED"
    FAILED = "FAILED"


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(String(64), primary_key=True, index=True)  # e.g., "amoxicillin"
    generic_name = Column(String(128), nullable=False, unique=True, index=True)
    brand_names = Column(String(256), nullable=True)  # Comma-separated or JSON string
    drug_class = Column(String(128), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    documents = relationship("Document", back_populates="medicine", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    medicine_id = Column(String(64), ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    source = Column(String(128), default="FDA Package Insert")
    filename = Column(String(256), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256
    file_size_bytes = Column(Integer, default=0)
    total_pages = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, index=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    medicine = relationship("Medicine", back_populates="documents")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(256), default="Drug Information Consultation")
    created_at = Column(DateTime, default=get_utc_now)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(32), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=True)  # Serialized JSON list of citations
    safety_flags_json = Column(Text, nullable=True)  # Serialized JSON safety metadata
    created_at = Column(DateTime, default=get_utc_now)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    @property
    def citations(self):
        if self.citations_json:
            try:
                return json.loads(self.citations_json)
            except Exception:
                return []
        return []

    @property
    def safety_flags(self):
        if self.safety_flags_json:
            try:
                return json.loads(self.safety_flags_json)
            except Exception:
                return {}
        return {}


class SafetyAuditLog(Base):
    __tablename__ = "safety_audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_text = Column(Text, nullable=False)
    classification = Column(String(64), nullable=False, index=True)  # SAFE, EMERGENCY, DOSAGE_ADVISORY, REFUSED
    action_taken = Column(String(64), nullable=False)  # ANSWERED, REFUSED_EMERGENCY, REFUSED_DOSAGE
    detected_keywords = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
