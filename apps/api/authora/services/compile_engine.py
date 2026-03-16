"""Manuscript compile engine - assemble content for export.

Assembles title page, front matter, TOC, chapters, sections, back matter
with full control over inclusion, order, and exclusions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from authora.services.export import tiptap_to_plain_text
from authora.services.export_extended import tiptap_to_structured_text


class CompileType(str, Enum):
    """Type of manuscript compile."""

    FULL = "full"
    CHAPTER_ONLY = "chapter_only"
    PARTIAL = "partial"
    REVIEW_COPY = "review_copy"
    SUBMISSION_COPY = "submission_copy"
    WORKING_DRAFT = "working_draft"


@dataclass
class CompileOptions:
    """Options for manuscript compilation."""

    # Content inclusion
    include_title_page: bool = True
    include_toc: bool = True
    include_headings: bool = True
    include_section_titles: bool = True
    exclude_notes_comments: bool = True
    exclude_highlights: bool = True
    exclude_revision_marks: bool = True

    # Chapter selection
    chapter_ids: list[str] | None = None  # None = all
    include_archived: bool = False
    include_unfinished: bool = True
    chapter_order: list[int] | None = None  # sort_order values; None = natural order

    # Section selection (within chapters)
    include_sections: bool = True
    section_ids: list[str] | None = None  # None = all sections
    include_archived_sections: bool = False

    # Front matter
    front_matter_blocks: list[dict[str, Any]] = field(default_factory=list)

    # Back matter
    back_matter_blocks: list[dict[str, Any]] = field(default_factory=list)

    # Compile type presets
    compile_type: CompileType = CompileType.FULL

    def apply_preset(self, preset: str) -> None:
        """Apply preset behavior by compile type."""
        if preset == CompileType.REVIEW_COPY.value:
            self.exclude_notes_comments = False
            self.exclude_revision_marks = False
            self.include_unfinished = True
        elif preset == CompileType.SUBMISSION_COPY.value:
            self.exclude_notes_comments = True
            self.exclude_highlights = True
            self.exclude_revision_marks = True
            self.include_unfinished = False
        elif preset == CompileType.WORKING_DRAFT.value:
            self.exclude_notes_comments = False
            self.exclude_revision_marks = False
            self.include_unfinished = True


def _strip_annotations_from_tiptap(content: dict[str, Any] | None) -> dict[str, Any]:
    """Remove comment/highlight marks from TipTap content. Returns clean doc."""
    if not content or not isinstance(content, dict):
        return {"type": "doc", "content": [{"type": "paragraph"}]}

    def walk(node: Any) -> Any:
        if isinstance(node, dict):
            if node.get("type") in ("comment", "highlight", "revisionMark"):
                return None
            if "content" in node:
                new_content = []
                for c in node["content"]:
                    result = walk(c)
                    if result is not None:
                        new_content.append(result)
                return {**node, "content": new_content}
            return node
        return node

    return walk(content) or {"type": "doc", "content": [{"type": "paragraph"}]}


def _content_to_clean_text(
    content: dict[str, Any] | None,
    *,
    strip_annotations: bool = True,
    use_structured: bool = True,
) -> str:
    """Convert TipTap content to plain text, optionally stripping annotations."""
    if not content:
        return ""
    if strip_annotations:
        content = _strip_annotations_from_tiptap(content)
    if use_structured:
        return tiptap_to_structured_text(content)
    return tiptap_to_plain_text(content)


@dataclass
class CompiledChapter:
    """A chapter in the compiled manuscript."""

    id: str
    title: str
    sort_order: int
    text: str
    word_count: int
    included: bool
    reason_excluded: str | None = None


@dataclass
class CompileResult:
    """Result of manuscript compilation."""

    chapters: list[CompiledChapter]
    total_words: int
    total_pages_estimate: int
    front_matter_text: str
    back_matter_text: str
    toc_entries: list[dict[str, Any]]
    warnings: list[str]
    structure_preview: list[dict[str, Any]]


def _estimate_pages(word_count: int) -> int:
    """Rough page estimate: ~250 words per page for manuscript."""
    return max(1, (word_count + 249) // 250)


def _build_front_matter_text(blocks: list[dict[str, Any]]) -> str:
    """Build front matter from ordered blocks."""
    parts = []
    for b in blocks:
        kind = b.get("kind", "")
        text = (b.get("content") or "").strip()
        if not text:
            continue
        if kind == "title_page":
            parts.append(text)
        elif kind == "copyright":
            parts.append(text)
        elif kind == "dedication":
            parts.append(text)
        elif kind == "epigraph":
            parts.append(f"> {text}")
        else:
            parts.append(text)
        parts.append("")
    return "\n\n".join(parts).strip()


def _build_back_matter_text(blocks: list[dict[str, Any]]) -> str:
    """Build back matter from ordered blocks."""
    parts = []
    for b in blocks:
        kind = b.get("kind", "")
        text = (b.get("content") or "").strip()
        if not text:
            continue
        title = b.get("title") or kind.replace("_", " ").title()
        parts.append(f"# {title}")
        parts.append("")
        parts.append(text)
        parts.append("")
    return "\n\n".join(parts).strip()


def compile_manuscript(
    chapters_data: list[dict[str, Any]],
    options: CompileOptions,
    *,
    book_title: str = "",
    author_name: str = "Author",
    front_matter_override: list[dict[str, Any]] | None = None,
    back_matter_override: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], CompileResult]:
    """
    Compile manuscript from chapters and options.

    Returns:
        (chapters_for_export, compile_result)
        chapters_for_export: list of {"title", "content", "text"} for export functions
    """
    warnings: list[str] = []
    front_blocks = front_matter_override or options.front_matter_blocks
    back_blocks = back_matter_override or options.back_matter_blocks

    # Filter and order chapters
    all_chapters = []
    for i, ch in enumerate(chapters_data):
        ch_id = str(ch.get("id", i))
        title = ch.get("title", "Untitled")
        sort_order = ch.get("sort_order", i)
        content = ch.get("content", {})
        section_status = ch.get("section_status", "draft")
        deleted_at = ch.get("deleted_at")

        # Apply filters
        if options.chapter_ids and ch_id not in options.chapter_ids:
            all_chapters.append(
                CompiledChapter(
                    id=ch_id,
                    title=title,
                    sort_order=sort_order,
                    text="",
                    word_count=0,
                    included=False,
                    reason_excluded="Not in selected chapters",
                )
            )
            continue

        if deleted_at and not options.include_archived:
            all_chapters.append(
                CompiledChapter(
                    id=ch_id,
                    title=title,
                    sort_order=sort_order,
                    text="",
                    word_count=0,
                    included=False,
                    reason_excluded="Archived",
                )
            )
            continue

        if section_status in ("outline", "placeholder") and not options.include_unfinished:
            all_chapters.append(
                CompiledChapter(
                    id=ch_id,
                    title=title,
                    sort_order=sort_order,
                    text="",
                    word_count=0,
                    included=False,
                    reason_excluded="Unfinished",
                )
            )
            continue

        # Build clean text
        strip = options.exclude_notes_comments or options.exclude_highlights or options.exclude_revision_marks
        text = _content_to_clean_text(content, strip_annotations=strip, use_structured=True)

        if not options.include_headings:
            text = tiptap_to_plain_text(content) if content else ""

        word_count = len(text.split())
        if word_count == 0:
            warnings.append(f"Empty chapter: {title}")

        all_chapters.append(
            CompiledChapter(
                id=ch_id,
                title=title,
                sort_order=sort_order,
                text=text,
                word_count=word_count,
                included=True,
                reason_excluded=None,
            )
        )

    # Apply custom chapter order if provided
    if options.chapter_order is not None:
        order_map = {so: ch for ch in all_chapters for so in [ch.sort_order]}
        all_chapters = [order_map[so] for so in options.chapter_order if so in order_map]

    # Sort included chapters by sort_order
    included = [c for c in all_chapters if c.included]
    included.sort(key=lambda x: x.sort_order)

    # Build lookup: id or index -> chapter data
    ch_by_id = {str(ch.get("id", i)): ch for i, ch in enumerate(chapters_data)}
    ch_by_idx = {i: ch for i, ch in enumerate(chapters_data)}

    # Build export-ready chapters
    chapters_for_export = []
    for c in included:
        ch_data = ch_by_id.get(c.id) or ch_by_idx.get(int(c.id) if c.id.isdigit() else -1)
        content = (ch_data or {}).get("content", {})
        if options.exclude_notes_comments or options.exclude_highlights or options.exclude_revision_marks:
            content = _strip_annotations_from_tiptap(content)
        chapters_for_export.append({
            "title": c.title,
            "content": content,
            "text": c.text,
        })

    # Front/back matter
    front_text = _build_front_matter_text(front_blocks)
    back_text = _build_back_matter_text(back_blocks)

    total_words = sum(c.word_count for c in included)
    total_pages = _estimate_pages(total_words)

    toc_entries = [{"title": c.title, "sort_order": c.sort_order} for c in included]

    structure = []
    if options.include_title_page and book_title:
        structure.append({"type": "title_page", "label": "Title Page"})
    for b in front_blocks:
        if b.get("content", "").strip():
            structure.append({"type": "front_matter", "kind": b.get("kind", ""), "label": b.get("title", b.get("kind", ""))})
    if options.include_toc and included:
        structure.append({"type": "toc", "label": "Table of Contents"})
    for c in included:
        structure.append({"type": "chapter", "title": c.title, "word_count": c.word_count})
    for b in back_blocks:
        if b.get("content", "").strip():
            structure.append({"type": "back_matter", "kind": b.get("kind", ""), "label": b.get("title", b.get("kind", ""))})

    result = CompileResult(
        chapters=all_chapters,
        total_words=total_words,
        total_pages_estimate=total_pages,
        front_matter_text=front_text,
        back_matter_text=back_text,
        toc_entries=toc_entries,
        warnings=warnings,
        structure_preview=structure,
    )

    return chapters_for_export, result


def chapters_data_from_book(book: Any, db: Any = None) -> list[dict[str, Any]]:
    """
    Build chapters_data list from Book model for compile_manuscript.
    Optionally loads sections if ChapterSection is used.
    """
    chapters = sorted(book.chapters, key=lambda x: x.sort_order)
    out = []
    for ch in chapters:
        data = {
            "id": str(ch.id),
            "title": ch.title,
            "sort_order": ch.sort_order,
            "content": ch.content or {},
            "section_status": ch.section_status,
            "deleted_at": ch.deleted_at.isoformat() if ch.deleted_at else None,
        }
        out.append(data)
    return out
