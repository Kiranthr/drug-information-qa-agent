"""
Semantic chunking engine for medical drug information documents.
"""

from typing import List, Dict, Any
import uuid


class DocumentChunker:
    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(
        self,
        pages_data: List[Dict[str, Any]],
        document_id: str,
        medicine_id: str,
        medicine_name: str,
        source_title: str
    ) -> List[Dict[str, Any]]:
        """
        Split extracted pages into overlapping chunks with contextual medical metadata.
        Returns a list of chunk dicts:
        {
            "id": str,
            "document_id": str,
            "medicine_id": str,
            "medicine_name": str,
            "source_title": str,
            "page_number": int,
            "section_name": str,
            "text": str,
            "metadata": dict
        }
        """
        chunks = []
        global_chunk_index = 0

        for page_item in pages_data:
            page_number = page_item["page_number"]
            page_text = page_item["text"]
            section = page_item.get("section", "GENERAL INFORMATION")

            if not page_text or len(page_text.strip()) < 30:
                continue

            # Split text on paragraph boundaries first
            paragraphs = page_text.split("\n\n")
            current_buffer = ""

            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue

                # If adding this paragraph exceeds chunk_size, process the current buffer
                if len(current_buffer) + len(paragraph) + 1 > self.chunk_size:
                    if current_buffer:
                        chunk_id = f"{document_id}_c{global_chunk_index}"
                        chunk_entry = self._create_chunk_entry(
                            chunk_id=chunk_id,
                            raw_content=current_buffer,
                            document_id=document_id,
                            medicine_id=medicine_id,
                            medicine_name=medicine_name,
                            source_title=source_title,
                            page_number=page_number,
                            section_name=section,
                            chunk_index=global_chunk_index
                        )
                        chunks.append(chunk_entry)
                        global_chunk_index += 1

                        # Keep overlap from the end of current buffer
                        overlap_start = max(0, len(current_buffer) - self.chunk_overlap)
                        current_buffer = current_buffer[overlap_start:].strip() + " " + paragraph
                    else:
                        # Single paragraph is larger than chunk_size, split by sentences/subchunks
                        sub_chunks = self._split_large_text(paragraph, self.chunk_size, self.chunk_overlap)
                        for sub_text in sub_chunks:
                            chunk_id = f"{document_id}_c{global_chunk_index}"
                            chunk_entry = self._create_chunk_entry(
                                chunk_id=chunk_id,
                                raw_content=sub_text,
                                document_id=document_id,
                                medicine_id=medicine_id,
                                medicine_name=medicine_name,
                                source_title=source_title,
                                page_number=page_number,
                                section_name=section,
                                chunk_index=global_chunk_index
                            )
                            chunks.append(chunk_entry)
                            global_chunk_index += 1
                        current_buffer = ""
                else:
                    if current_buffer:
                        current_buffer += "\n\n" + paragraph
                    else:
                        current_buffer = paragraph

            # Flush remaining buffer for this page
            if current_buffer and len(current_buffer.strip()) >= 30:
                chunk_id = f"{document_id}_c{global_chunk_index}"
                chunk_entry = self._create_chunk_entry(
                    chunk_id=chunk_id,
                    raw_content=current_buffer,
                    document_id=document_id,
                    medicine_id=medicine_id,
                    medicine_name=medicine_name,
                    source_title=source_title,
                    page_number=page_number,
                    section_name=section,
                    chunk_index=global_chunk_index
                )
                chunks.append(chunk_entry)
                global_chunk_index += 1

        return chunks

    def _split_large_text(self, text: str, max_size: int, overlap: int) -> List[str]:
        """Split text exceeding max_size into subchunks using sentence or space boundaries."""
        results = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + max_size, text_len)
            # Try to break at a period or space
            if end < text_len:
                last_space = text.rfind(" ", start, end)
                if last_space > start + (max_size // 2):
                    end = last_space

            sub_piece = text[start:end].strip()
            if sub_piece:
                results.append(sub_piece)

            if end >= text_len:
                break
            start = max(start + 1, end - overlap)

        return results

    def _create_chunk_entry(
        self,
        chunk_id: str,
        raw_content: str,
        document_id: str,
        medicine_id: str,
        medicine_name: str,
        source_title: str,
        page_number: int,
        section_name: str,
        chunk_index: int
    ) -> Dict[str, Any]:
        """Format chunk with header prefix and metadata."""
        # Include metadata breadcrumb header in the indexed chunk text
        breadcrumb = (
            f"[Medicine: {medicine_name} | Document: {source_title} | "
            f"Section: {section_name} | Page: {page_number}]\n"
        )
        full_text = f"{breadcrumb}\n{raw_content}"

        return {
            "id": chunk_id,
            "text": full_text,
            "raw_content": raw_content,
            "metadata": {
                "document_id": document_id,
                "medicine_id": medicine_id,
                "medicine_name": medicine_name,
                "source_title": source_title,
                "page_number": int(page_number),
                "section_name": section_name,
                "chunk_index": int(chunk_index)
            }
        }


chunker = DocumentChunker()
