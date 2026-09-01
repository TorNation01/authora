"""Document import — docx, pdf, txt, rtf, odt → Authora chapters.

POST /api/v1/projects/{project_id}/books/{book_id}/import
  - Accepts multipart file upload
  - Extracts text from docx, pdf, txt, rtf, odt
  - Creates chapters from the extracted content
  - Returns list of created chapters
"""

import io
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_with_access_or_404
from authora.database import get_db
from authora.models import Chapter
from authora.schemas.book import ChapterResponse
from authora.services.export import plain_text_to_tiptap

router = APIRouter(prefix="/projects/{project_id}/books/{book_id}", tags=["import"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
SUPPORTED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
    "text/markdown",
    "text/rtf",
    "application/rtf",
    "application/vnd.oasis.opendocument.text",
}


def _extract_text(file_bytes: bytes, filename: str, content_type: str) -> str:
    """Extract text from uploaded file. Returns plain text."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    # PDF
    if ext == "pdf" or content_type == "application/pdf":
        try:
            import pymupdf
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
            pages = [page.get_text() for page in doc]
            doc.close()
            return "\n\n".join(pages)
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="PDF import requires pymupdf. Install with: pip install pymupdf",
            )

    # DOCX
    if ext == "docx" or content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="DOCX import requires python-docx. Install with: pip install python-docx",
            )

    # ODT
    if ext == "odt" or content_type == "application/vnd.oasis.opendocument.text":
        try:
            from odf.opendocument import load
            from odf import text as odf_text
            doc = load(io.BytesIO(file_bytes))
            paragraphs = []
            for elem in doc.getElementsByType(odf_text.P):
                text_content = ""
                for node in elem.childNodes:
                    if hasattr(node, "data"):
                        text_content += node.data
                if text_content.strip():
                    paragraphs.append(text_content.strip())
            return "\n\n".join(paragraphs)
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="ODT import requires odfpy. Install with: pip install odfpy",
            )

    # RTF
    if ext == "rtf" or content_type in ("text/rtf", "application/rtf"):
        try:
            from striprtf.striprtf import rtf_to_text
            return rtf_to_text(file_bytes.decode("utf-8", errors="replace"))
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="RTF import requires striprtf. Install with: pip install striprtf",
            )

    # Plain text / markdown — fallback
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1", errors="replace")


def _split_into_chapters(text: str, max_chars_per_chapter: int = 15000) -> list[str]:
    """Split text into chapter-sized chunks. Tries to split on double newlines first,
    then on single newlines, then falls back to character-based splitting."""
    if len(text) <= max_chars_per_chapter:
        return [text]

    # Try splitting on double newlines (paragraph groups)
    sections = text.split("\n\n")
    chapters: list[str] = []
    current = ""

    for section in sections:
        if len(current) + len(section) + 2 <= max_chars_per_chapter:
            current = (current + "\n\n" + section) if current else section
        else:
            if current:
                chapters.append(current)
            # If a single section is too long, split it further
            if len(section) > max_chars_per_chapter:
                # Split on single newlines
                lines = section.split("\n")
                sub = ""
                for line in lines:
                    if len(sub) + len(line) + 1 <= max_chars_per_chapter:
                        sub = (sub + "\n" + line) if sub else line
                    else:
                        if sub:
                            chapters.append(sub)
                        sub = line
                if sub:
                    current = sub
                else:
                    current = ""
            else:
                current = section

    if current:
        chapters.append(current)

    return chapters


@router.post("/import", response_model=list[ChapterResponse])
async def import_document(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
    split_chapters: bool = True,
    chapter_prefix: str = "Chapter",
):
    """Import a document (docx, pdf, txt, rtf, odt) into a book.

    Extracts text and creates chapters. Set split_chapters=false to create
    a single chapter with all content.
    """
    book = await get_book_with_access_or_404(db, book_id, project_id, current_user.id)

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    # Validate content type
    content_type = file.content_type or ""
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if content_type not in SUPPORTED_TYPES and ext not in {"pdf", "docx", "doc", "txt", "md", "rtf", "odt"}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {content_type or ext}. Supported: PDF, DOCX, TXT, MD, RTF, ODT",
        )

    # Read file
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum: {MAX_FILE_SIZE // (1024*1024)} MB",
        )

    # Extract text
    try:
        text = _extract_text(file_bytes, file.filename, content_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to extract text: {str(e)}",
        )

    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No text content found in the uploaded file",
        )

    # Split into chapters
    if split_chapters:
        chapter_texts = _split_into_chapters(text)
    else:
        chapter_texts = [text]

    # Get current max sort_order
    from sqlalchemy import select, func as sqlfunc
    result = await db.execute(
        select(sqlfunc.coalesce(sqlfunc.max(Chapter.sort_order), -1)).where(
            Chapter.book_id == book_id
        )
    )
    max_order = result.scalar() or -1

    # Create chapters
    created: list[Chapter] = []
    for i, ch_text in enumerate(chapter_texts):
        ch = Chapter(
            book_id=book_id,
            title=f"{chapter_prefix} {max_order + i + 2}" if len(chapter_texts) > 1 else file.filename.rsplit(".", 1)[0],
            sort_order=max_order + i + 1,
            content=plain_text_to_tiptap(ch_text),
            word_count=len(ch_text.split()),
            content_source="user_written",
        )
        db.add(ch)
        await db.flush()
        await db.refresh(ch)
        created.append(ch)

    return [ChapterResponse.model_validate(ch) for ch in created]
