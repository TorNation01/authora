"""Submission to a publishing house — pack the manuscript and hand it over.

This is the Authora side of the same connection Fliss uses: a multipart POST to
Anema House's intake endpoint, which answers with a reference such as
``AH-2026-0007``. The browser never talks to the house; the API does, and only
when the author presses the button.

Pack rules
----------
* One manuscript file, not one file per chapter. Chapters are concatenated in
  reading order with their headings.
* The cover is attached when the author has uploaded one.
* Nothing is inferred about acceptance. The house's reply is stored verbatim.
"""

from __future__ import annotations

import mimetypes
import re
from dataclasses import dataclass
from typing import Any

import httpx

from authora.models import Book, Chapter
from authora.services.export import tiptap_to_plain_text

DEFAULT_INTAKE_URL = "https://anemahouse.com/intake"
HOUSE_NAME = "Anema House Publishing"
HOUSE_URL = "https://anemahouse.com"

MAX_ATTACH_BYTES = 40 * 1024 * 1024


class SubmissionError(RuntimeError):
    """Raised when the house cannot be reached or refuses the pack."""


@dataclass
class PackFile:
    filename: str
    content: bytes
    content_type: str


def _safe(value: str, fallback: str = "untitled") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._ -]+", "", (value or "").strip())[:120].strip()
    return cleaned or fallback


def build_manuscript(book: Book, chapters: list[Chapter], author_name: str | None) -> PackFile:
    """Concatenate the book into a single Markdown manuscript."""
    title = (book.title or "Untitled").strip()
    parts: list[str] = [f"# {title}"]
    if author_name:
        parts += ["", f"by {author_name}"]
    parts.append("")

    for chapter in chapters:
        body = tiptap_to_plain_text(chapter.content or {}).strip()
        if not body:
            continue
        parts += [f"## {chapter.title or 'Untitled chapter'}", "", body, ""]

    text = "\n".join(parts).strip() + "\n"
    return PackFile(
        filename=f"{_safe(title)} - manuscript.md",
        content=text.encode("utf-8"),
        content_type="text/markdown",
    )


def word_count(chapters: list[Chapter]) -> int:
    total = 0
    for chapter in chapters:
        total += int(chapter.word_count or 0)
    return total


async def submit_pack(
    *,
    base_url: str,
    payload: dict[str, Any],
    files: list[PackFile],
    timeout: float = 180.0,
) -> dict[str, Any]:
    """POST the pack to the house. Returns the house receipt."""
    for f in files:
        if len(f.content) > MAX_ATTACH_BYTES:
            raise SubmissionError(f"{f.filename} is larger than the house will accept (40 MB).")

    multipart: list[tuple[str, tuple[str, bytes, str]]] = [
        ("files", (f.filename, f.content, f.content_type or "application/octet-stream")) for f in files
    ]

    url = f"{base_url.rstrip('/')}/submit"
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.post(url, data=payload, files=multipart)
    except httpx.HTTPError as exc:
        raise SubmissionError(f"could not reach {url}: {exc}") from exc

    if response.status_code == 429:
        raise SubmissionError("The house is receiving too many submissions right now — try again later.")
    if response.status_code >= 400:
        detail = ""
        try:
            body = response.json()
            detail = body.get("detail") or ""
            if isinstance(detail, list):
                detail = "; ".join(str(d.get("msg", d)) if isinstance(d, dict) else str(d) for d in detail)
        except Exception:  # noqa: BLE001
            detail = response.text[:200]
        raise SubmissionError(f"Anema House refused the pack ({response.status_code}): {detail}")

    try:
        return response.json()
    except Exception as exc:  # noqa: BLE001
        raise SubmissionError("The house answered with something that was not a receipt.") from exc


async def fetch_status(*, base_url: str, ref: str, email: str, timeout: float = 20.0) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/status/{ref}"
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, params={"email": email})
    except httpx.HTTPError as exc:
        raise SubmissionError(f"could not reach {url}: {exc}") from exc

    if response.status_code == 404:
        raise SubmissionError("The house has no submission under that reference and email.")
    if response.status_code >= 400:
        raise SubmissionError(f"The house could not answer the status check ({response.status_code}).")
    return response.json()


def guess_type(filename: str) -> str:
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"
