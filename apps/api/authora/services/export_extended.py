"""Extended export service - front/back matter, TOC, structure, publishing prep."""

import io
import zipfile
from dataclasses import dataclass
from typing import Any

from authora.services.export import tiptap_to_plain_text


@dataclass
class ExportParams:
    """Parameters for export."""

    book_title: str
    author_name: str = "Author"
    include_title_page: bool = True
    include_toc: bool = True
    include_acknowledgements: bool = False
    front_matter: str | None = None
    back_matter: str | None = None
    acknowledgements: str | None = None
    format_style: str = "manuscript"  # manuscript | print | ebook


def _get_node_text(n: dict) -> str:
    """Extract text from a TipTap node."""
    parts = []
    for c in n.get("content", []):
        if isinstance(c, dict):
            if "text" in c:
                parts.append(c["text"])
            elif "content" in c:
                parts.append(_get_node_text(c))
    return "".join(parts)


def _extract_blocks(content: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract structured blocks from TipTap (headings, paragraphs, lists)."""
    blocks = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            t = node.get("type")
            if t == "heading":
                level = node.get("attrs", {}).get("level", 1)
                text = _get_node_text(node)
                if text:
                    blocks.append({"type": "heading", "level": level, "text": text})
            elif t == "paragraph":
                text = _get_node_text(node)
                if text or not blocks:
                    blocks.append({"type": "paragraph", "text": text})
            elif t == "blockquote":
                text = _get_node_text(node)
                if text:
                    blocks.append({"type": "blockquote", "text": text})
            elif t == "bulletList":
                for c in node.get("content", []):
                    walk(c)
            elif t == "orderedList":
                for c in node.get("content", []):
                    walk(c)
            elif t == "listItem":
                text = _get_node_text(node)
                if text:
                    blocks.append({"type": "list_item", "text": text})
            elif t == "hardBreak":
                pass
            elif "content" in node:
                for c in node["content"]:
                    walk(c)
        elif isinstance(node, list):
            for n in node:
                walk(n)

    if isinstance(content, dict) and "content" in content:
        for node in content["content"]:
            walk(node)
    return blocks


def _blocks_to_plain_text(blocks: list[dict]) -> str:
    """Convert structured blocks to plain text with heading markers."""
    lines = []
    for b in blocks:
        t = b.get("type", "")
        text = b.get("text", "").strip()
        if not text and t != "paragraph":
            continue
        if t == "heading":
            level = b.get("level", 1)
            prefix = "#" * level + " "
            lines.append(f"{prefix}{text}")
        elif t == "blockquote":
            lines.append(f"> {text}")
        elif t == "list_item":
            lines.append(f"- {text}")
        else:
            lines.append(text)
        if lines:
            lines.append("")
    return "\n".join(lines).replace("\n\n\n", "\n\n")


def tiptap_to_structured_text(content: dict[str, Any]) -> str:
    """Convert TipTap to plain text preserving headings and structure."""
    blocks = _extract_blocks(content)
    return _blocks_to_plain_text(blocks)


def export_outline(chapters: list[dict]) -> bytes:
    """Export chapter outline only (titles + optional summaries)."""
    parts = []
    for i, ch in enumerate(chapters, 1):
        title = ch.get("title", "Untitled")
        content = ch.get("content", {})
        text = tiptap_to_plain_text(content)
        summary = text[:200] + "..." if len(text) > 200 else text
        parts.append(f"{i}. {title}\n   {summary.strip() or '(no content)'}")
    return "\n\n".join(parts).encode("utf-8")


def export_notes_txt(notes: list[dict]) -> bytes:
    """Export notes as plain text."""
    parts = []
    for n in notes:
        title = n.get("title", "Untitled")
        content = n.get("content", "")
        note_type = n.get("note_type", "general")
        source = n.get("source", "")
        tags = n.get("tags", [])
        header = f"# {title} [{note_type}]"
        if source:
            header += f" (Source: {source})"
        if tags:
            header += f" Tags: {', '.join(tags)}"
        parts.append(f"{header}\n\n{content}")
    return "\n\n---\n\n".join(parts).encode("utf-8")


def _build_chapters_data(chapters: list[dict], use_structured: bool = False) -> list[dict]:
    """Build chapters data with optional structured text."""
    out = []
    for ch in chapters:
        title = ch.get("title", "Untitled")
        content = ch.get("content", {})
        if use_structured:
            text = tiptap_to_structured_text(content)
        else:
            text = tiptap_to_plain_text(content)
        out.append({"title": title, "content": content, "text": text})
    return out


def export_full_docx(
    chapters: list[dict],
    params: ExportParams,
) -> bytes:
    """Export to DOCX with front/back matter and TOC."""
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    chapters_data = _build_chapters_data(chapters, use_structured=True)

    if params.include_title_page:
        title_para = doc.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title_para.add_run(params.book_title)
        run.bold = True
        run.font.size = Pt(24)
        doc.add_paragraph()
        doc.add_paragraph(params.author_name, style="Normal")
        doc.add_page_break()

    if params.include_toc and len(chapters_data) > 0:
        doc.add_heading("Table of Contents", level=0)
        for i, ch in enumerate(chapters_data, 1):
            doc.add_paragraph(f"{i}. {ch['title']}", style="List Number")
        doc.add_page_break()

    if params.front_matter:
        doc.add_heading("Front Matter", level=0)
        for p in params.front_matter.split("\n\n"):
            if p.strip():
                doc.add_paragraph(p.strip())
        doc.add_page_break()

    for ch in chapters_data:
        doc.add_heading(ch["title"], level=1)
        for block in ch["text"].split("\n\n"):
            block = block.strip()
            if not block:
                continue
            if block.startswith("#"):
                level = len(block) - len(block.lstrip("#"))
                text = block.lstrip("#").strip()
                doc.add_heading(text, level=min(level, 3))
            elif block.startswith(">"):
                p = doc.add_paragraph(block[1:].strip())
                p.paragraph_format.left_indent = Inches(0.5)
            else:
                p = doc.add_paragraph(block)
                p.paragraph_format.space_after = Pt(12)
        doc.add_paragraph()

    if params.include_acknowledgements and params.acknowledgements:
        doc.add_page_break()
        doc.add_heading("Acknowledgements", level=0)
        for p in params.acknowledgements.split("\n\n"):
            if p.strip():
                doc.add_paragraph(p.strip())
        doc.add_page_break()

    if params.back_matter:
        doc.add_heading("Back Matter", level=0)
        for p in params.back_matter.split("\n\n"):
            if p.strip():
                doc.add_paragraph(p.strip())

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def export_full_txt(chapters: list[dict], params: ExportParams) -> bytes:
    """Export to TXT with front/back matter."""
    parts = []
    if params.include_title_page:
        parts.append(params.book_title)
        parts.append("")
        parts.append(params.author_name)
        parts.append("")
        parts.append("=" * 40)
        parts.append("")

    if params.include_toc:
        parts.append("TABLE OF CONTENTS")
        parts.append("")
        for i, ch in enumerate(chapters, 1):
            parts.append(f"  {i}. {ch.get('title', 'Untitled')}")
        parts.append("")
        parts.append("=" * 40)
        parts.append("")

    if params.front_matter:
        parts.append("FRONT MATTER")
        parts.append("")
        parts.append(params.front_matter)
        parts.append("")
        parts.append("=" * 40)
        parts.append("")

    chapters_data = _build_chapters_data(chapters, use_structured=True)
    for ch in chapters_data:
        parts.append(f"# {ch['title']}")
        parts.append("")
        parts.append(ch["text"])
        parts.append("")

    if params.include_acknowledgements and params.acknowledgements:
        parts.append("=" * 40)
        parts.append("ACKNOWLEDGEMENTS")
        parts.append("")
        parts.append(params.acknowledgements)
        parts.append("")

    if params.back_matter:
        parts.append("=" * 40)
        parts.append("BACK MATTER")
        parts.append("")
        parts.append(params.back_matter)

    return "\n".join(parts).encode("utf-8")


def export_full_pdf(chapters: list[dict], params: ExportParams) -> bytes:
    """Export to PDF with front/back matter."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    from authora.services.export import export_pdf

    chapters_data = _build_chapters_data(chapters, use_structured=False)
    return export_pdf(
        [{"title": ch["title"], "content": ch["content"]} for ch in chapters_data],
        params.book_title,
    )


def export_full_epub(chapters: list[dict], params: ExportParams) -> bytes:
    """Export to EPUB with metadata."""
    from authora.services.export import export_epub

    chapters_data = [{"title": ch.get("title", ""), "content": ch.get("content", {})} for ch in chapters]
    return export_epub(chapters_data, params.book_title, params.author_name)


def export_chapter_single(chapter: dict, format: str, book_title: str) -> bytes:
    """Export single chapter."""
    chapters_data = [{"title": chapter.get("title", "Untitled"), "content": chapter.get("content", {})}]
    from authora.services.export import export_txt, export_docx, export_pdf, export_epub

    if format == "txt":
        return export_txt(chapters_data)
    if format == "docx":
        return export_docx(chapters_data, f"{book_title} - {chapter.get('title', 'Chapter')}")
    if format == "pdf":
        return export_pdf(chapters_data, f"{book_title} - {chapter.get('title', 'Chapter')}")
    if format == "epub":
        return export_epub(chapters_data, f"{book_title} - {chapter.get('title', 'Chapter')}")
    raise ValueError(f"Unknown format: {format}")


def export_chapters_zip(chapters: list[dict], book_title: str, format: str = "docx") -> bytes:
    """Export each chapter as separate file in a ZIP."""
    from authora.services.export import export_txt, export_docx, export_pdf

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, ch in enumerate(chapters):
            single = [{"title": ch.get("title", f"Chapter {i+1}"), "content": ch.get("content", {})}]
            if format == "txt":
                data = export_txt(single)
            elif format == "docx":
                data = export_docx(single, f"{book_title}_{i+1}")
            elif format == "pdf":
                data = export_pdf(single, f"{book_title}_{i+1}")
            else:
                data = export_txt(single)
            safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in ch.get("title", f"ch{i+1}"))[:40]
            zf.writestr(f"{safe_title}.{format}", data)
    buffer.seek(0)
    return buffer.getvalue()
