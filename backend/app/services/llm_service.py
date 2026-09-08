"""
LLM integration service using the official Google GenAI SDK (Gemini 2.5 Flash),
with offline deterministic fallback for testing and development.
"""

from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger

SYSTEM_INSTRUCTION = """You are a professional, evidence-grounded Drug Information Assistant.
Your mission is to provide accurate, strictly factual information based ONLY on the provided official regulatory drug documentation snippets.

MANDATORY RULES:
1. GROUNDING: Base your answer EXCLUSIVELY on the provided Context Documents. Do NOT extrapolate or assume clinical facts not stated in the text.
2. CITATIONS: Cite your sources inline using bracketed tags like [Source 1], [Source 2] corresponding to the numbered context snippets provided.
3. UNCERTAINTY: If the provided documents do not contain the answer, explicitly state: "The provided official drug documentation does not contain information to answer this question." Do NOT guess or hallucinate.
4. DOSAGE & PRESCRIBING SAFETY: Never advise a patient to change, increase, or decrease their medication dosage. Quote the official general label dosage if available, and state that dosage adjustments must be determined solely by their licensed physician.
5. NO DIAGNOSING: Do not diagnose conditions or tell the user what disease they have.
6. TONE: Objective, clear, professional, empathetic, and easily understandable by both patients and clinicians.
"""


class LLMService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._client = None

    def _get_client(self):
        """Lazy load Google GenAI Client."""
        if not self.api_key:
            return None
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Google GenAI client: {e}")
                return None
        return self._client

    def generate_grounded_answer(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]],
        safety_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a strictly grounded answer to the question using retrieved context snippets.
        Uses Gemini API if key is present; otherwise falls back to intelligent offline synthesis.
        """
        formatted_context = self._format_context(context_chunks)

        user_prompt = (
            f"USER QUESTION:\n{question}\n\n"
            f"CONTEXT DOCUMENTS:\n{formatted_context}\n\n"
        )

        if safety_context and safety_context.get("classification") == "DOSAGE_ADVISORY":
            user_prompt += (
                "NOTE ON SAFETY: The user may be inquiring about dosage modification or personal use. "
                "Quote official label indications and dosing ranges if present, but emphatically advise "
                "consulting a doctor before any dose modification.\n\n"
            )

        user_prompt += "Provide a clear, evidence-grounded answer with inline [Source X] citations:"

        client = self._get_client()
        if client:
            try:
                from google.genai import types
                logger.info(f"Calling Gemini API ({self.model_name}) for grounded response...")

                response = client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,  # Low temperature for strict adherence to facts
                        top_p=0.8,
                        max_output_tokens=1024,
                        system_instruction=SYSTEM_INSTRUCTION
                    )
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini generation call failed ({e}), falling back to offline grounded generator.")

        # Offline grounded fallback (active when no API key or during offline demo/testing)
        return self._offline_grounded_generator(question, context_chunks, safety_context)

    def _format_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Format chunks into numbered context blocks for prompt injection."""
        if not context_chunks:
            return "No matching official document snippets found."

        blocks = []
        for idx, chunk in enumerate(context_chunks, 1):
            meta = chunk.get("metadata", {})
            title = meta.get("source_title", "Drug Label")
            page = meta.get("page_number", 1)
            section = meta.get("section_name", "GENERAL")
            doc_text = chunk.get("document", "")

            block = (
                f"--- [Source {idx}] ---\n"
                f"Document: {title} | Section: {section} | Page: {page}\n"
                f"Content:\n{doc_text}\n"
            )
            blocks.append(block)

        return "\n".join(blocks)

    def _offline_grounded_generator(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]],
        safety_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Deterministic, offline extraction that synthesizes relevant excerpts
        from context chunks with [Source X] citations.
        """
        if not context_chunks:
            return "The provided official drug documentation does not contain information to answer this question."

        lines = [
            f"Based on the official regulatory documentation in the library:\n"
        ]

        for idx, chunk in enumerate(context_chunks, 1):
            meta = chunk.get("metadata", {})
            title = meta.get("source_title", "Package Insert")
            page = meta.get("page_number", 1)
            section = meta.get("section_name", "Information")
            raw = chunk.get("document", "")

            # Strip the bracketed header if present
            body = raw
            if "]\n\n" in raw:
                body = raw.split("]\n\n", 1)[1]
            elif "]\n" in raw:
                body = raw.split("]\n", 1)[1]

            # Grab key sentences
            clean_body = " ".join(body.split())
            if len(clean_body) > 350:
                clean_body = clean_body[:350] + "..."

            lines.append(
                f"- **{section}** (from *{title}*, Page {page}) [Source {idx}]:\n"
                f"  \"{clean_body}\"\n"
            )

        if safety_context and safety_context.get("classification") == "DOSAGE_ADVISORY":
            lines.append(
                "\n*Clinical Note: Dosage adjustments must only be made under the direct guidance "
                "of your prescribing physician or pharmacist based on your specific medical profile.*"
            )

        return "\n".join(lines)


llm_service = LLMService()
