"""Chunking strategy for RAG indexing."""

import re
from dataclasses import dataclass

from authora.config import get_settings


@dataclass
class Chunk:
    """A chunk of content for embedding."""

    text: str
    source_type: str
    source_id: str
    chunk_index: int
    metadata: dict


def _chunk_by_size(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks by character size."""
    if not text or not text.strip():
        return []
    text = text.strip()
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if end < len(text):
            last_break = max(
                chunk.rfind("\n\n"),
                chunk.rfind(". "),
                chunk.rfind("! "),
                chunk.rfind("? "),
            )
            if last_break > chunk_size // 2:
                chunk = chunk[: last_break + 1]
                end = start + last_break + 1
        chunks.append(chunk.strip())
        start = end - overlap if overlap < chunk_size else end
    return [c for c in chunks if c]


def chunk_note(
    title: str,
    content: str,
    note_id: str,
    project_id: str,
    book_id: str | None = None,
    chapter_id: str | None = None,
) -> list[Chunk]:
    """Chunk a note for indexing."""
    s = get_settings()
    size = s.rag_chunk_size
    overlap = s.rag_chunk_overlap
    full = f"{title}\n\n{content}" if title else content
    texts = _chunk_by_size(full, size, overlap)
    return [
        Chunk(
            text=t,
            source_type="note",
            source_id=note_id,
            chunk_index=i,
            metadata={"project_id": project_id, "book_id": book_id, "chapter_id": chapter_id, "title": title},
        )
        for i, t in enumerate(texts)
    ]


def chunk_chapter(title: str, content_plain: str, chapter_id: str, book_id: str, project_id: str) -> list[Chunk]:
    """Chunk a chapter for indexing."""
    s = get_settings()
    size = s.rag_chunk_size
    overlap = s.rag_chunk_overlap
    full = f"# {title}\n\n{content_plain}" if title else content_plain
    texts = _chunk_by_size(full, size, overlap)
    return [
        Chunk(
            text=t,
            source_type="chapter",
            source_id=chapter_id,
            chunk_index=i,
            metadata={"project_id": project_id, "book_id": book_id, "title": title},
        )
        for i, t in enumerate(texts)
    ]


def chunk_chapter_brief(brief_text: str, brief_id: str, chapter_id: str, book_id: str, project_id: str) -> list[Chunk]:
    """Chunk a chapter brief."""
    s = get_settings()
    size = s.rag_chunk_size
    overlap = s.rag_chunk_overlap
    texts = _chunk_by_size(brief_text, size, overlap)
    return [
        Chunk(
            text=t,
            source_type="chapter_brief",
            source_id=brief_id,
            chunk_index=i,
            metadata={"project_id": project_id, "book_id": book_id, "chapter_id": chapter_id},
        )
        for i, t in enumerate(texts)
    ]


def chunk_outline(outline: dict, book_id: str, project_id: str) -> list[Chunk]:
    """Chunk outline chapters as individual chunks."""
    chapters = outline.get("chapters") or []
    chunks = []
    for i, ch in enumerate(chapters):
        title = ch.get("title", "Untitled")
        summary = ch.get("summary", "")
        text = f"Chapter: {title}\n\n{summary}"
        if not text.strip():
            continue
        chunks.append(
            Chunk(
                text=text,
                source_type="outline_chapter",
                source_id=book_id,
                chunk_index=i,
                metadata={"project_id": project_id, "book_id": book_id, "chapter_title": title},
            )
        )
    return chunks
