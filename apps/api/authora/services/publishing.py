"""Publishing readiness: the checklist that stands between a manuscript and a book.

Every item is computed from the book's own records and the same validation
functions the export endpoints use (``validate_export_content``), so a reason
shown in the UI is a reason the exporter would actually have produced.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, BookPublication, Chapter, PublishingAsset
from authora.models.fiction import FictionChapterPlan
from authora.models.nonfiction import NFChapterPlan
from authora.services.export import tiptap_to_plain_text
from authora.services.export_extended import PLACEHOLDER_PATTERNS, validate_export_content

PASS = "pass"
WARN = "warn"
FAIL = "fail"

_ISBN10_RE = re.compile(r"^[0-9]{9}[0-9X]$")
_ISBN13_RE = re.compile(r"^[0-9]{13}$")


def normalise_isbn(raw: str | None) -> tuple[str | None, str | None]:
    """Validate an ISBN for length and checksum only.

    Returns ``(normalised, error)``. A blank value is valid (``None``, ``None``).
    This does not check registration with any agency and does not claim the
    number belongs to this book.
    """
    if raw is None:
        return None, None
    compact = re.sub(r"[\s-]", "", raw).upper()
    if not compact:
        return None, None

    if len(compact) == 10:
        if not _ISBN10_RE.match(compact):
            return None, "ISBN-10 must be nine digits followed by a digit or X."
        digits = [int(c) if c.isdigit() else 10 for c in compact]
        total = sum((10 - i) * d for i, d in enumerate(digits))
        if total % 11 != 0:
            return None, "ISBN-10 checksum is invalid."
        return compact, None

    if len(compact) == 13:
        if not _ISBN13_RE.match(compact):
            return None, "ISBN-13 must be thirteen digits."
        total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(compact))
        if total % 10 != 0:
            return None, "ISBN-13 checksum is invalid."
        return compact, None

    return None, "An ISBN must be 10 or 13 digits (hyphens and spaces are ignored)."


def _item(
    item_id: str,
    label: str,
    group: str,
    status: str,
    reason: str,
    *,
    source: str,
    blocking: bool = False,
) -> dict[str, Any]:
    return {
        "id": item_id,
        "label": label,
        "group": group,
        "status": status,
        "reason": reason,
        "source": source,
        "blocking": blocking,
    }


def _chapter_text(chapter: Chapter) -> str:
    return tiptap_to_plain_text(chapter.content).strip() if chapter.content else ""


async def build_readiness(
    db: AsyncSession,
    book: Book,
    publication: BookPublication | None,
) -> dict[str, Any]:
    """Build the readiness checklist for a book."""
    chapters = sorted(
        [c for c in book.chapters if c.deleted_at is None],
        key=lambda c: c.sort_order,
    )
    texts = {c.id: _chapter_text(c) for c in chapters}
    total_words = sum(len(t.split()) for t in texts.values())
    chapter_count = len(chapters)
    items: list[dict[str, Any]] = []

    title = (publication.title if publication and publication.title else book.title) or ""
    subtitle = (publication.subtitle if publication else None) or ""
    author_name = ((publication.author_name if publication else None) or "").strip()
    imprint = ((publication.imprint if publication else None) or "").strip()

    # ---------------------------------------------------------------- front matter
    if title.strip():
        reason = f'The title page will read "{title.strip()}"'
        reason += f' with subtitle "{subtitle.strip()}".' if subtitle.strip() else "."
        items.append(_item("title_page", "Title page", "Front matter", PASS, reason, source="book record"))
    else:
        items.append(
            _item(
                "title_page",
                "Title page",
                "Front matter",
                FAIL,
                "The book has no title, so a title page cannot be set.",
                source="book record",
                blocking=True,
            )
        )

    if author_name:
        items.append(
            _item("author_name", "Author name", "Front matter", PASS, f'Byline will read "{author_name}".', source="publication metadata")
        )
    else:
        items.append(
            _item(
                "author_name",
                "Author name",
                "Front matter",
                FAIL,
                "No author name saved. Exports fall back to the word \"Author\" on the title page and byline.",
                source="publication metadata",
            )
        )

    if publication and (publication.copyright_notice or "").strip():
        items.append(
            _item("copyright", "Copyright page", "Front matter", PASS, "A copyright notice is saved and will be printed on the copyright page.", source="publication metadata")
        )
    else:
        items.append(
            _item(
                "copyright",
                "Copyright page",
                "Front matter",
                WARN,
                "No copyright notice saved, so the copyright page is omitted from the export.",
                source="publication metadata",
            )
        )

    if publication and (publication.dedication or "").strip():
        items.append(_item("dedication", "Dedication", "Front matter", PASS, "A dedication is saved and will be printed.", source="publication metadata"))
    else:
        items.append(
            _item("dedication", "Dedication", "Front matter", WARN, "No dedication saved - optional, and omitted from the export.", source="publication metadata")
        )

    if chapter_count:
        items.append(
            _item(
                "contents",
                "Contents page",
                "Front matter",
                PASS,
                f"A contents page will list all {chapter_count} chapters in reading order.",
                source="export structure",
            )
        )
    else:
        items.append(
            _item(
                "contents",
                "Contents page",
                "Front matter",
                FAIL,
                "There are no chapters, so there is nothing to list on a contents page.",
                source="export structure",
                blocking=True,
            )
        )

    # ------------------------------------------------------------------ manuscript
    plan_model = FictionChapterPlan if (book.type or "fiction") == "fiction" else NFChapterPlan
    plan_count = (
        await db.execute(select(func.count(plan_model.id)).where(plan_model.book_id == book.id))
    ).scalar() or 0
    if plan_count == 0:
        items.append(
            _item(
                "chapter_count_vs_outline",
                "Chapter count vs outline",
                "Manuscript",
                WARN,
                f"The manuscript has {chapter_count} chapter(s) and no chapter plan exists for this book, so there is nothing to compare against. Build the outline in the Plan workspace to close this.",
                source="chapter plan",
            )
        )
    elif plan_count == chapter_count:
        items.append(
            _item(
                "chapter_count_vs_outline",
                "Chapter count vs outline",
                "Manuscript",
                PASS,
                f"{chapter_count} chapters written against {plan_count} planned.",
                source="chapter plan",
            )
        )
    else:
        items.append(
            _item(
                "chapter_count_vs_outline",
                "Chapter count vs outline",
                "Manuscript",
                WARN,
                f"The manuscript has {chapter_count} chapter(s); the outline plans {plan_count}. Merged or dropped chapters are fine - confirm this is intended.",
                source="chapter plan",
            )
        )

    if total_words == 0:
        items.append(
            _item(
                "word_count",
                "Word count",
                "Manuscript",
                FAIL,
                "The manuscript has no words yet, so there is nothing to export.",
                source="chapter content",
                blocking=True,
            )
        )
    elif total_words < 1000:
        items.append(
            _item(
                "word_count",
                "Word count",
                "Manuscript",
                WARN,
                f"{total_words:,} words across {chapter_count} chapter(s) - short for a finished book.",
                source="chapter content",
            )
        )
    else:
        items.append(
            _item(
                "word_count",
                "Word count",
                "Manuscript",
                PASS,
                f"{total_words:,} words across {chapter_count} chapter(s).",
                source="chapter content",
            )
        )

    untitled: list[str] = []
    for i, c in enumerate(chapters, start=1):
        t = (c.title or "").strip()
        if not t or t.lower() in {"untitled", "untitled chapter"}:
            untitled.append(f"#{i}")
    if untitled:
        items.append(
            _item(
                "chapter_titles",
                "Chapter titles",
                "Manuscript",
                FAIL,
                f"{len(untitled)} chapter(s) have no real title and will export as \"Chapter N\": "
                + ", ".join(untitled)
                + ".",
                source="chapter records",
            )
        )
    else:
        items.append(
            _item("chapter_titles", "Chapter titles", "Manuscript", PASS, f"All {chapter_count} chapter(s) have titles.", source="chapter records")
        )

    empty = [c.title or f"Chapter {i + 1}" for i, c in enumerate(chapters) if not texts[c.id]]
    if empty:
        items.append(
            _item(
                "empty_chapters",
                "Empty chapters",
                "Manuscript",
                FAIL,
                "These chapters have no body text: " + ", ".join(empty) + ".",
                source="validate",
            )
        )
    else:
        items.append(_item("empty_chapters", "Empty chapters", "Manuscript", PASS, "Every chapter has body text.", source="validate"))

    placeholder_hits: list[str] = []
    for c in chapters:
        lower = texts[c.id].lower()
        if any(pat in lower for pat in PLACEHOLDER_PATTERNS):
            placeholder_hits.append(c.title or "Untitled chapter")
    if placeholder_hits:
        items.append(
            _item(
                "placeholders",
                "Unresolved placeholders",
                "Manuscript",
                FAIL,
                "Placeholder text is still in the manuscript: "
                + ", ".join(placeholder_hits)
                + ".",
                source="validate",
            )
        )
    else:
        items.append(
            _item("placeholders", "Unresolved placeholders", "Manuscript", PASS, "No placeholder markers found in any chapter.", source="validate")
        )

    seen: dict[str, int] = {}
    for c in chapters:
        key = (c.title or "").strip().lower()
        if key:
            seen[key] = seen.get(key, 0) + 1
    duplicates = [k for k, v in seen.items() if v > 1]
    if duplicates:
        items.append(
            _item(
                "duplicate_titles",
                "Duplicate chapter titles",
                "Manuscript",
                WARN,
                "Repeated chapter titles: " + ", ".join(duplicates[:5]) + ".",
                source="validate",
            )
        )
    else:
        items.append(_item("duplicate_titles", "Duplicate chapter titles", "Manuscript", PASS, "No duplicate chapter titles.", source="validate"))

    # ------------------------------------------------------------------- back matter
    has_front = bool(
        publication
        and ((publication.front_matter or "").strip() or (publication.dedication or "").strip() or (publication.copyright_notice or "").strip())
    )
    items.append(
        _item(
            "front_matter",
            "Front matter",
            "Front matter",
            PASS if has_front else WARN,
            "Front matter is set (copyright, dedication or front matter text)." if has_front else "No front matter saved yet - the export will start at the title page.",
            source="publication metadata",
        )
    )

    back_fields = []
    if publication:
        if (publication.acknowledgements or "").strip():
            back_fields.append("acknowledgements")
        if (publication.author_bio or "").strip():
            back_fields.append("author bio")
        if (publication.back_matter or "").strip():
            back_fields.append("back matter")
    items.append(
        _item(
            "back_matter",
            "Back matter",
            "Back matter",
            PASS if back_fields else WARN,
            ("Back matter set: " + ", ".join(back_fields) + ".") if back_fields else "No back matter saved yet - acknowledgements, author bio or closing pages are omitted.",
            source="publication metadata",
        )
    )

    blurb = ((publication.blurb if publication else None) or "").strip()
    items.append(
        _item(
            "blurb",
            "Back-cover copy",
            "Back matter",
            PASS if blurb else WARN,
            f"A {len(blurb.split())}-word blurb is saved." if blurb else "No blurb saved. You can generate one from the manuscript with the blurb publishing-prep endpoint.",
            source="publication metadata / publishing-prep",
        )
    )

    # --------------------------------------------------------------- cover & identity
    cover = (
        await db.execute(
            select(PublishingAsset)
            .where(PublishingAsset.book_id == book.id, PublishingAsset.asset_type == "cover")
            .order_by(PublishingAsset.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if cover:
        meta = cover.asset_metadata or {}
        dims = f"{meta.get('width')}x{meta.get('height')}" if meta.get("width") and meta.get("height") else "dimensions unknown"
        items.append(_item("cover", "Cover image", "Cover & identifiers", PASS, f"A cover is uploaded ({dims}, {meta.get('content_type', 'image')}).", source="publishing assets"))
    else:
        items.append(
            _item("cover", "Cover image", "Cover & identifiers", WARN, "No cover uploaded. Retailers require one; Authora does not generate cover art.", source="publishing assets")
        )

    isbn = (publication.isbn if publication else None) or ""
    if isbn:
        _, isbn_error = normalise_isbn(isbn)
        items.append(
            _item(
                "isbn",
                "ISBN",
                "Cover & identifiers",
                FAIL if isbn_error else PASS,
                isbn_error or f"ISBN {isbn} stored (checksum valid). Authora stores the number only - it does not register it.",
                source="publication metadata",
            )
        )
    else:
        items.append(
            _item(
                "isbn",
                "ISBN",
                "Cover & identifiers",
                WARN,
                "No ISBN recorded. ISBNs are issued by your national ISBN agency; Authora validates and stores a number, it does not assign or register one.",
                source="publication metadata",
            )
        )

    pub_date = publication.publication_date if publication else None
    items.append(
        _item(
            "publication_date",
            "Publication date",
            "Cover & identifiers",
            PASS if pub_date else WARN,
            f"Publication date set to {pub_date.isoformat()}." if pub_date else "No publication date set.",
            source="publication metadata",
        )
    )

    # -------------------------------------------------------------------------- release
    released = bool(publication and publication.is_released)
    items.append(
        _item(
            "release",
            "Release recorded",
            "Release",
            PASS if released else WARN,
            (
                f"Release recorded on {publication.released_at.date().isoformat()} for {', '.join(publication.release_formats or []) or 'no formats listed'}."
                if released and publication
                else "No release recorded yet. Recording a release stores your intent here; it does not send anything to a retailer."
            ),
            source="release record",
        )
    )

    # Raw validation output, exactly as the export endpoint returns it.
    validation = validate_export_content(
        [{"title": c.title, "content": c.content} for c in chapters],
        book_title=title,
        author_name=author_name or None,
        require_author=True,
        check_placeholders=True,
    )

    counts = {PASS: 0, WARN: 0, FAIL: 0}
    for it in items:
        counts[it["status"]] = counts.get(it["status"], 0) + 1
    blocking = [it for it in items if it["blocking"] and it["status"] == FAIL]

    return {
        "book_id": str(book.id),
        "book_title": title,
        "chapter_count": chapter_count,
        "total_words": total_words,
        "imprint": imprint or None,
        "outline_chapter_count": plan_count,
        "items": items,
        "summary": {
            "pass": counts[PASS],
            "warn": counts[WARN],
            "fail": counts[FAIL],
            "export_ready": not blocking and validation["valid"],
            "release_ready": not blocking,
            "blocking_failures": [it["id"] for it in blocking],
        },
        "validation": validation,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
