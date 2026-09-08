"""
Safety audit log endpoints for compliance and hackathon demonstration.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.sql_models import SafetyAuditLog
from app.models.schemas import SafetyAuditLogResponse

router = APIRouter(prefix="/safety", tags=["Safety & Guardrails"])


@router.get("/audit-logs", response_model=List[SafetyAuditLogResponse])
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve recent query safety classifications and actions taken by the guardrail engine.
    Demonstrates how emergency, dosage, and ungrounded queries are safely handled.
    """
    logs = db.query(SafetyAuditLog).order_by(SafetyAuditLog.created_at.desc()).limit(limit).all()
    return logs
