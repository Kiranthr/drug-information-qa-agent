"""
Unit tests for the Medical Safety Guardrail and Triage Engine.
"""

import pytest
from app.services.safety_service import safety_service


def test_emergency_detection_overdose(db_session):
    """Verify that acute overdose queries trigger emergency triage protocol."""
    query = "I accidentally took an overdose of paracetamol, swallowed a whole bottle"
    meta, emergency_text = safety_service.evaluate_query(query, db_session)

    assert meta.emergency_detected is True
    assert meta.classification == "EMERGENCY"
    assert emergency_text is not None
    assert "CRITICAL MEDICAL ALERT" in emergency_text
    assert "Poison Control" in emergency_text


def test_emergency_detection_severe_symptoms(db_session):
    """Verify that severe respiratory distress or anaphylaxis triggers emergency triage."""
    query = "My throat is closing up and I can't breathe after taking amoxicillin"
    meta, emergency_text = safety_service.evaluate_query(query, db_session)

    assert meta.emergency_detected is True
    assert meta.classification == "EMERGENCY"
    assert emergency_text is not None
    assert "911" in emergency_text


def test_dosage_modification_guard(db_session):
    """Verify that requests to alter dosages are flagged for clinical advisory enforcement."""
    query = "Can I double my dose of Metformin to 1000mg if my blood sugar is high?"
    meta, immediate_text = safety_service.evaluate_query(query, db_session)

    assert meta.classification == "DOSAGE_ADVISORY"
    assert meta.emergency_detected is False
    assert immediate_text is None  # Goes to RAG with advisory context


def test_safe_informational_query(db_session):
    """Verify that standard factual questions pass through as SAFE_INFORMATIONAL."""
    query = "What are the common adverse reactions of Atorvastatin?"
    meta, immediate_text = safety_service.evaluate_query(query, db_session)

    assert meta.classification == "SAFE_INFORMATIONAL"
    assert meta.emergency_detected is False
    assert immediate_text is None


def test_disclaimer_appending():
    """Verify that standard medical disclaimer is always appended."""
    text = "Amoxicillin is an antibacterial drug."
    final_text = safety_service.append_disclaimer(text)

    assert "Medical Disclaimer" in final_text
    assert "licensed healthcare provider" in final_text
