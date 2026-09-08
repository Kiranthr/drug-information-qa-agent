"""
PDF parsing and medical section extraction using PyMuPDF (fitz).
"""

import re
from typing import List, Dict, Any
from pathlib import Path
import fitz  # PyMuPDF
from app.core.logging import logger

# Recognized standard FDA/EMA drug package insert section headings
DRUG_LABEL_SECTIONS = [
    "INDICATIONS AND USAGE",
    "DOSAGE AND ADMINISTRATION",
    "DOSAGE FORMS AND STRENGTHS",
    "CONTRAINDICATIONS",
    "WARNINGS AND PRECAUTIONS",
    "ADVERSE REACTIONS",
    "SIDE EFFECTS",
    "DRUG INTERACTIONS",
    "USE IN SPECIFIC POPULATIONS",
    "PREGNANCY AND LACTATION",
    "PEDIATRIC USE",
    "GERIATRIC USE",
    "OVERDOSAGE",
    "CLINICAL PHARMACOLOGY",
    "MECHANISM OF ACTION",
    "PHARMACOKINETICS",
    "DESCRIPTION",
    "HOW SUPPLIED",
    "STORAGE AND HANDLING",
    "PATIENT COUNSELING INFORMATION"
]


class PDFParser:
    def extract_pages(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from each page of a PDF file, tracking page numbers and detected sections.
        Returns a list of dicts: {"page_number": int, "text": str, "sections": List[str]}
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

        pages_data = []
        doc = fitz.open(str(path))

        try:
            logger.info(f"Parsing PDF '{path.name}' with {len(doc)} pages...")
            current_section = "GENERAL INFORMATION"

            for page_idx in range(len(doc)):
                page = doc[page_idx]
                page_number = page_idx + 1
                text = page.get_text("text")

                # Clean up whitespace while preserving paragraphs
                cleaned_text = self._clean_text(text)

                # Look for section headings on this page
                detected_section = self._detect_section(cleaned_text)
                if detected_section:
                    current_section = detected_section

                pages_data.append({
                    "page_number": page_number,
                    "text": cleaned_text,
                    "section": current_section
                })

            logger.info(f"Successfully parsed {len(pages_data)} pages from '{path.name}'")
            return pages_data

        finally:
            doc.close()

    def _detect_section(self, text: str) -> str | None:
        """Check if any standard drug label section header appears prominently in the page text."""
        for section in DRUG_LABEL_SECTIONS:
            # Match heading as a standalone line or with numbering (e.g. "4 CONTRAINDICATIONS")
            pattern = rf"(?:^|\n)(?:\d+[\.\s]+)?{re.escape(section)}(?:\s*[:\n]|$)"
            if re.search(pattern, text, re.IGNORECASE):
                return section
        return None

    def _clean_text(self, text: str) -> str:
        """Clean excessive whitespace and hyphens from word wraps."""
        if not text:
            return ""
        # Remove hyphenation at line breaks (e.g., "medi-\ncation" -> "medication")
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        # Normalize carriage returns and line feeds
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace 3 or more newlines with double newline
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


pdf_parser = PDFParser()
