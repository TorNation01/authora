"""Imprint back-matter page.

One short page, written in the imprint's voice, included in generated
EPUB/PDF/DOCX files when the author leaves it switched on. It states how the
book was produced and where production/build continue - nothing else.

No addresses, phone numbers or contact details are invented here.
"""

from dataclasses import dataclass, field
import os

ANEMA_HOUSE_NAME = "Anema House Publishing"
ANEMA_HOUSE_URL = "https://anemahouse.com"
BOOKFORGE_NAME = "Bookforge"
# BookForge is an internal build pipeline. It has no public address, so the
# imprint must not invent one. Set BOOKFORGE_PUBLIC_URL only when a real,
# publicly reachable endpoint exists.
BOOKFORGE_URL = os.environ.get("BOOKFORGE_PUBLIC_URL", "").strip()

HEADING = "A Note on This Edition"


@dataclass
class ImprintPage:
    """Structured imprint page: heading, paragraphs, and reference links."""

    heading: str
    paragraphs: list[str] = field(default_factory=list)
    links: list[tuple[str, str]] = field(default_factory=list)

    def as_text(self) -> str:
        """Plain-text rendering (used by TXT export and previews)."""
        lines = [self.heading, ""]
        lines.extend(self.paragraphs)
        if self.links:
            lines.append("")
            lines.extend(f"{label}: {url}" for label, url in self.links)
        return "\n\n".join(p for p in lines if p is not None)


def build_imprint_page(
    *,
    book_title: str | None = None,
    author_name: str | None = None,
    imprint: str | None = None,
) -> ImprintPage:
    """Build the imprint page for a book.

    The wording is deliberately plain: it credits Authora for production and
    points to the publisher and the build pipeline. It makes no claim that a
    manuscript was submitted anywhere.
    """
    publisher = (imprint or "").strip() or ANEMA_HOUSE_NAME
    title = (book_title or "").strip()

    paragraphs = [
        (
            f"This edition of {title} was produced with Authora, from first draft "
            "through to the finished files."
            if title
            else "This edition was produced with Authora, from first draft through to the finished files."
        ),
        f"Production and publishing: {ANEMA_HOUSE_NAME}.",
        f"Print and ebook build pipeline: {BOOKFORGE_NAME}.",
    ]
    if publisher != ANEMA_HOUSE_NAME:
        paragraphs.insert(1, f"Imprint: {publisher}.")

    links = [
        (f"{ANEMA_HOUSE_NAME} - production and publishing", ANEMA_HOUSE_URL),
    ]
    if BOOKFORGE_URL:
        links.append((f"{BOOKFORGE_NAME} - build pipeline", BOOKFORGE_URL))

    return ImprintPage(heading=HEADING, paragraphs=paragraphs, links=links)
