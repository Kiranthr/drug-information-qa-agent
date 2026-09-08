"""
Medical Safety Guardrails and Policy Enforcement Service.
Enforces multi-shield defense against emergencies, hallucinations, and unsafe medical advice.
"""

import re
from typing import Tuple, Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.sql_models import SafetyAuditLog
from app.models.schemas import SafetyMetadata

# Emergency keywords indicating acute intoxication, overdose, or life-threatening distress
EMERGENCY_PATTERNS = [
    r"\boverdose[sd]?\b",
    r"\bswallowed\s+(?:a\s+whole\s+bottle|too\s+many|all\s+(?:the\s+)?pills)\b",
    r"\btook\s+(?:\d{2,}|\btoo\s+many\b)\s+pills\b",
    r"\bpoison(?:ing|ed)?\b",
    r"\bsuicid(?:e|al)\b",
    r"\bkill\s+myself\b",
    r"\bend\s+my\s+life\b",
    r"\bchest\s+pain\b",
    r"\bcan'?t\s+breathe\b",
    r"\bstopped\s+breathing\b",
    r"\bsevere\s+allergic\s+reaction\b",
    r"\banaphylax(?:is|ic)\b",
    r"\bloss\s+of\s+consciousness\b",
    r"\bpassed\s+out\b",
    r"\bseizure[s]?\b",
    r"\bunconscious\b"
]

# Dosage change / self-prescription query patterns
DOSAGE_ALTERATION_PATTERNS = [
    r"\b(?:can|should|may)\s+i\s+(?:increase|double|triple|lower|decrease|stop|change)\s+(?:my|the)\s+dos(?:e|age)\b",
    r"\bhow\s+much\s+(?:should|can)\s+i\s+(?:take|give)\s+my\s+(?:baby|infant|toddler|child|kid|son|daughter)\b",
    r"\bprescribe\s+(?:me|for)\b",
    r"\bcan\s+i\s+take\s+(?:\d+)\s+mg\s+instead\s+of\b",
    r"\bwhat\s+happens\s+if\s+i\s+take\s+(?:double|extra|3|4|5)\s+pills\b"
]

# Diagnostic query patterns
DIAGNOSTIC_PATTERNS = [
    r"\bdo\s+i\s+have\b",
    r"\bdiagnose\s+(?:me|my\s+symptoms)\b",
    r"\bi\s+have\s+(?:a\s+fever|cough|pain|lump|rash)\b.*what\s+disease\b"
]

STANDARD_DISCLAIMER = (
    "\n\n---\n"
    "⚠️ **Medical Disclaimer**: *This information is retrieved strictly from official regulatory package inserts "
    "for educational and informational purposes only. It is NOT clinical medical advice, diagnosis, or personalized treatment. "
    "Never alter your medication regimen without consulting your licensed healthcare provider or pharmacist.*"
)

EMERGENCY_RESPONSE_TEXT = (
    "🚨 **CRITICAL MEDICAL ALERT: IMMEDIATE ACTION REQUIRED**\n\n"
    "Your query indicates a potential **medical emergency, overdose, or acute adverse event**.\n\n"
    "**DO NOT WAIT FOR AN AI RESPONSE. SEEK IMMEDIATE EMERGENCY CARE:**\n\n"
    "1. **Call 911** (United States / Canada) or **112** (Europe / India / International emergency number) right now.\n"
    "2. **Poison Control Center Hotline:**\n"
    "   - **US Poison Help:** [1-800-222-1222](tel:18002221222) (Toll-free, 24/7 confidential)\n"
    "   - **National Poison Information Centre (India):** [1800-116-117](tel:1800116117) / [011-26589391](tel:01126589391)\n"
    "   - **UK NHS Emergency:** Call **999** (or 111 for urgent advice)\n"
    "3. If someone is unconscious, has collapsed, has a seizure, or is having trouble breathing, call emergency services immediately.\n"
    "4. Have the medication packaging or pill bottle ready to show emergency responders.\n\n"
    "This AI assistant is an informational reference tool and cannot provide emergency medical intervention."
)


class SafetyService:
    def evaluate_query(self, query: str, db: Optional[Session] = None) -> Tuple[SafetyMetadata, Optional[str]]:
        """
        Evaluate user question against medical safety rules.
        Returns:
            Tuple of (SafetyMetadata, optional_immediate_response_string)
            If optional_immediate_response_string is provided, bypasses LLM immediately.
        """
        query_lower = query.lower().strip()

        # 1. Check for Emergency / Overdose / Poisoning
        for pattern in EMERGENCY_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                detected = match.group(0)
                logger.warning(f"SAFETY GUARD TRIGGERED: Emergency pattern '{detected}' in query: '{query}'")
                
                metadata = SafetyMetadata(
                    classification="EMERGENCY",
                    emergency_detected=True,
                    refusal_reason="Acute emergency or overdose detected. Triage protocol activated.",
                    disclaimer_included=True,
                    action_taken="REFUSED_EMERGENCY"
                )
                self._record_audit_log(db, query, "EMERGENCY", "REFUSED_EMERGENCY", detected)
                return metadata, EMERGENCY_RESPONSE_TEXT

        # 2. Check for Dosage Alteration / Self-Prescribing
        for pattern in DOSAGE_ALTERATION_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                detected = match.group(0)
                logger.info(f"SAFETY GUARD TRIGGERED: Dosage alteration pattern '{detected}' in query: '{query}'")
                
                metadata = SafetyMetadata(
                    classification="DOSAGE_ADVISORY",
                    emergency_detected=False,
                    refusal_reason="Direct dosage modification or personal prescription advice requested.",
                    disclaimer_included=True,
                    action_taken="ADVISORY_ENFORCED"
                )
                self._record_audit_log(db, query, "DOSAGE_ADVISORY", "ADVISORY_ENFORCED", detected)
                # Does not bypass RAG completely; instead alerts RAG pipeline to enforce dosage constraints
                return metadata, None

        # 3. Check for Diagnostic queries
        for pattern in DIAGNOSTIC_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                detected = match.group(0)
                logger.info(f"SAFETY GUARD TRIGGERED: Diagnostic pattern '{detected}' in query: '{query}'")
                
                metadata = SafetyMetadata(
                    classification="DIAGNOSTIC_REQUEST",
                    emergency_detected=False,
                    refusal_reason="Personal medical diagnosis requested.",
                    disclaimer_included=True,
                    action_taken="DIAGNOSTIC_REFUSAL_ENFORCED"
                )
                self._record_audit_log(db, query, "DIAGNOSTIC_REQUEST", "DIAGNOSTIC_REFUSAL_ENFORCED", detected)
                return metadata, None

        # 4. Standard Informational Query
        metadata = SafetyMetadata(
            classification="SAFE_INFORMATIONAL",
            emergency_detected=False,
            refusal_reason=None,
            disclaimer_included=True,
            action_taken="ANSWERED"
        )
        self._record_audit_log(db, query, "SAFE_INFORMATIONAL", "ANSWERED", None)
        return metadata, None

    def append_disclaimer(self, text: str) -> str:
        """Ensure standard medical disclaimer is attached."""
        if "Medical Disclaimer" in text:
            return text
        return f"{text.rstrip()}{STANDARD_DISCLAIMER}"

    def build_uncertainty_response(self, medicine_name: Optional[str] = None) -> str:
        """Standard evidence-grounded uncertainty response when no reliable chunks are found."""
        med_clause = f" for '{medicine_name}'" if medicine_name else ""
        return (
            f"I could not locate verified, evidence-grounded information{med_clause} regarding your question "
            f"in the official regulatory drug documents currently available in my library.\n\n"
            f"To protect your health and safety, I do not invent or extrapolate medical facts.\n\n"
            f"**Recommended Next Steps:**\n"
            f"- Consult a licensed pharmacist or your prescribing physician.\n"
            f"- Check the official FDA package insert or DailyMed database.\n"
            f"- If you are an administrator, you may upload the official package insert PDF into the Document Library."
        )

    def _record_audit_log(
        self,
        db: Optional[Session],
        query: str,
        classification: str,
        action: str,
        keywords: Optional[str]
    ) -> None:
        """Record query evaluation in the safety audit table."""
        if not db:
            return
        try:
            log_entry = SafetyAuditLog(
                query_text=query,
                classification=classification,
                action_taken=action,
                detected_keywords=keywords
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to record safety audit log: {e}")


safety_service = SafetyService()
