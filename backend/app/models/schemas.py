"""
Pydantic v2 schemas for API validation and serialization.
"""

from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# Health & Status Schemas
# ==========================================

class HealthCheckResponse(BaseModel):
    status: str = "ok"
    app_name: str
    app_env: str
    database_connected: bool
    total_medicines: int
    total_documents: int
    vector_chunks_indexed: int
    llm_provider: str
    embedding_provider: str


# ==========================================
# Medicine Schemas
# ==========================================

class MedicineBase(BaseModel):
    id: str = Field(..., description="Unique slug ID, e.g., 'amoxicillin'")
    generic_name: str = Field(..., description="Generic name of the medicine")
    brand_names: Optional[str] = Field(None, description="Known brand names, comma separated")
    drug_class: Optional[str] = Field(None, description="Pharmacological class")
    description: Optional[str] = Field(None, description="Clinical summary/description")


class MedicineCreate(MedicineBase):
    pass


class MedicineResponse(MedicineBase):
    document_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Document Schemas
# ==========================================

class DocumentResponse(BaseModel):
    id: str
    medicine_id: str
    medicine_name: Optional[str] = None
    title: str
    source: str
    filename: str
    file_size_bytes: int
    total_pages: int
    total_chunks: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    document: DocumentResponse
    message: str


# ==========================================
# Citation & Safety Schemas
# ==========================================

class Citation(BaseModel):
    source_title: str
    medicine_name: str
    page_number: int
    section_name: Optional[str] = "GENERAL"
    excerpt: str
    relevance_score: Optional[float] = None


class SafetyMetadata(BaseModel):
    classification: str  # SAFE_INFORMATIONAL, EMERGENCY, DOSAGE_ADVISORY, OFF_TOPIC, UNCERTAIN
    emergency_detected: bool = False
    refusal_reason: Optional[str] = None
    disclaimer_included: bool = True
    action_taken: str = "ANSWERED"


# ==========================================
# Chat & Q&A Schemas
# ==========================================

class ChatQueryRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1500, description="User question about a medicine")
    session_id: Optional[str] = Field(None, description="UUID of existing conversation session")
    medicine_id: Optional[str] = Field(None, description="Optional target medicine filter")


class ChatQueryResponse(BaseModel):
    answer: str
    citations: List[Citation] = []
    safety_metadata: SafetyMetadata
    session_id: str
    message_id: str
    created_at: datetime


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: List[Dict[str, Any]] = []
    safety_flags: Dict[str, Any] = {}
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    messages: List[ChatMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Safety Audit Schemas
# ==========================================

class SafetyAuditLogResponse(BaseModel):
    id: str
    query_text: str
    classification: str
    action_taken: str
    detected_keywords: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
