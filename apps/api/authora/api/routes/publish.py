"""Publish and release routes.

Everything here reads or writes the author's own records. Nothing is sent to a
retailer or distributor: a release is a stored record of intent.
"""

from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authora.api.dependencies import CurrentUser
from authora.database import get_db
from authora.infrastructure.storage import get_storage_provider
from authora.models import Book, BookPublication, Project, PublishingAsset
from authora.models.publication import DEFAULT_IMPRINT
from authora.schemas.publication import (
    CoverInfo,
    PublicationResponse,
    PublicationUpdate,
    ReleaseRecord,
    ReleaseRequest,
)
from authora.services.imprint import ANEMA_HOUSE_NAME, build_imprint_page
from authora.services.publishing import build_readiness, normalise_isbn

router = APIRouter(prefix="/publish", tags=["publish"])

MAX_COVER_BYTES = 10 * 1024 * 1024
ALLOWED_COVER_TYPES = {"image/jpeg", "image/png", "image/webp"}

# Dimensions are the ones the retail channels actually ask for. Print covers are
# supplied as a separate front-cover asset by the production house.
COVER_SPECS = {
    "ebook": {
        "recommended_width": 1600,
        "recommended_height": 2560,
        "minimum_width": 1000,
        "minimum_height": 1600,
        "ratio": "1:1.6",
        "max_file_mb": 10,
        "formats": ["image/jpeg", "image/png", "image/webp"],
        "note": "Ebook front cover, no spine or bleed.",
    },
    "print": {
        "recommended_width": 1800,
        "recommended_height": 2700,
        "minimum_width": 1800,
        "minimum_height": 2700,
        "dpi": 300,
        "max_file_mb": 10,
        "formats": ["image/jpeg", "image/png"],
        "note": "Print front cover at 300 DPI. Full wraparound artwork with spine and bleed is produced outside Authora.",
    },
}


async def get_book_for_user(db: AsyncSession, book_id: uuid.UUID, user_id: uuid.UUID) -> Book | None:
    result = await db.execute(
        select(Book)
        .options(selectinload(Book.chapters), selectinload(Book.publication))
        .join(Project)
        .where(Book.id == book_id, Project.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_or_create_publication(db: AsyncSession, book: Book) -> BookPublication:
    publication = book.publication
    if publication is None:
        result = await db.execute(select(BookPublication).where(BookPublication.book_id == book.id))
        publication = result.scalar_one_or_none()
    if publication is None:
        publication = BookPublication(
            book_id=book.id,
            title=book.title,
            imprint=DEFAULT_IMPRINT,
            keywords=[],
            categories=[],
            include_imprint_page=True,
            status="draft",
            release_formats=[],
        )
        db.add(publication)
        await db.flush()
    return publication


async def _latest_cover(db: AsyncSession, book_id: uuid.UUID) -> PublishingAsset | None:
    result = await db.execute(
        select(PublishingAsset)
        .where(PublishingAsset.book_id == book_id, PublishingAsset.asset_type == "cover")
        .order_by(PublishingAsset.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


def _cover_info(asset: PublishingAsset | None) -> CoverInfo | None:
    if asset is None:
        return None
    meta = asset.asset_metadata or {}
    return CoverInfo(
        id=asset.id,
        content_type=meta.get("content_type"),
        width=meta.get("width"),
        height=meta.get("height"),
        size_bytes=meta.get("size_bytes"),
        uploaded_at=asset.created_at,
        url=f"/api/v1/publish/books/{asset.book_id}/cover",
    )


def _serialise(book: Book, publication: BookPublication | None, cover: PublishingAsset | None) -> PublicationResponse:
    release = None
    if publication and publication.is_released and publication.released_at:
        release = ReleaseRecord(
            released_at=publication.released_at,
            formats=list(publication.release_formats or []),
            imprint=publication.release_imprint,
            isbn=publication.release_isbn,
        )
    return PublicationResponse(
        book_id=book.id,
        book_title=book.title,
        book_type=book.type or "fiction",
        exists=publication is not None,
        title=(publication.title if publication else None) or book.title,
        subtitle=publication.subtitle if publication else None,
        author_name=publication.author_name if publication else None,
        blurb=publication.blurb if publication else None,
        short_description=publication.short_description if publication else None,
        keywords=list(publication.keywords or []) if publication else [],
        categories=list(publication.categories or []) if publication else [],
        language=(publication.language if publication else None) or "en",
        isbn=publication.isbn if publication else None,
        publication_date=publication.publication_date if publication else None,
        imprint=(publication.imprint if publication else None) or DEFAULT_IMPRINT,
        copyright_notice=publication.copyright_notice if publication else None,
        dedication=publication.dedication if publication else None,
        front_matter=publication.front_matter if publication else None,
        acknowledgements=publication.acknowledgements if publication else None,
        author_bio=publication.author_bio if publication else None,
        back_matter=publication.back_matter if publication else None,
        include_imprint_page=publication.include_imprint_page if publication else True,
        status=(publication.status if publication else "draft") or "draft",
        release=release,
        cover=_cover_info(cover),
        cover_specs=COVER_SPECS,
        updated_at=publication.updated_at if publication else None,
    )


@router.get("/books/{book_id}/publication", response_model=PublicationResponse)
async def get_publication(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Publication metadata for a book, creating nothing on read."""
    book = await get_book_for_user(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    publication = book.publication
    if publication is None:
        result = await db.execute(select(BookPublication).where(BookPublication.book_id == book.id))
        publication = result.scalar_one_or_none()
    cover = await _latest_cover(db, book_id)
    return _serialise(book, publication, cover)


@router.put("/books/{book_id}/publication", response_model=PublicationResponse)
async def update_publication(
    book_id: uuid.UUID,
    body: PublicationUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Save publishing metadata. Unknown or invalid ISBNs are rejected, never stored."""
    book = await get_book_for_user(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    publication = await get_or_create_publication(db, book)
    payload = body.model_dump(exclude_unset=True)
    if "isbn" in payload:
        normalised, error = normalise_isbn(payload["isbn"])
        if error:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error)
        payload["isbn"] = normalised

    for field, value in payload.items():
        setattr(publication, field, value)

    if not (publication.title or "").strip():
        publication.title = book.title
    publication.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(publication)

    book.publication = publication
    cover = await _latest_cover(db, book_id)
    return _serialise(book, publication, cover)


@router.post("/books/{book_id}/cover", response_model=PublicationResponse)
async def upload_cover(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
):
    """Upload a cover image. Authora stores it; it does not create artwork."""
    book = await get_book_for_user(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_COVER_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Cover must be a JPEG, PNG or WebP image.",
        )

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded file is empty.")
    if len(raw) > MAX_COVER_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Cover must be under {MAX_COVER_BYTES // (1024 * 1024)} MB.",
        )

    width = height = None
    try:
        from PIL import Image

        with Image.open(io.BytesIO(raw)) as image:
            width, height = image.size
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The file could not be read as an image.")

    ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}[content_type]
    key = f"covers/{book_id}/{uuid.uuid4().hex}.{ext}"
    provider = get_storage_provider()
    await provider.put(key, raw, content_type=content_type)

    asset = PublishingAsset(
        book_id=book_id,
        asset_type="cover",
        file_key=key,
        asset_metadata={
            "content_type": content_type,
            "width": width,
            "height": height,
            "size_bytes": len(raw),
            "original_filename": file.filename,
        },
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    publication = book.publication
    if publication is None:
        result = await db.execute(select(BookPublication).where(BookPublication.book_id == book_id))
        publication = result.scalar_one_or_none()
    return _serialise(book, publication, asset)


@router.get("/books/{book_id}/cover")
async def get_cover(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Stream the latest cover image for this book."""
    book = await get_book_for_user(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    asset = await _latest_cover(db, book_id)
    if asset is None or not asset.file_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cover uploaded")
    provider = get_storage_provider()
    try:
        content = await provider.get(asset.file_key)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cover file is no longer in storage")
    meta = asset.asset_metadata or {}
    return Response(
        content=content,
        media_type=meta.get("content_type") or "application/octet-stream",
        headers={"Cache-Control": "private, max-age=60"},
    )


@router.get("/books/{book_id}/readiness")
async def get_readiness(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """The readiness checklist, computed from the book, its metadata and the export validator."""
    book = await get_book_for_user(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    publication = book.publication
    if publication is None:
        result = await db.execute(select(BookPublication).where(BookPublication.book_id == book_id))
        publication = result.scalar_one_or_none()
    return await build_readiness(db, book, publication)


@router.get("/books/{book_id}/imprint-page")
async def preview_imprint_page(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """The exact back-matter page that generated files will contain."""
    book = await get_book_for_user(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    publication = book.publication
    page = build_imprint_page(
        book_title=(publication.title if publication and publication.title else book.title),
        author_name=publication.author_name if publication else None,
        imprint=(publication.imprint if publication else None) or ANEMA_HOUSE_NAME,
    )
    return {
        "heading": page.heading,
        "paragraphs": page.paragraphs,
        "links": [{"label": label, "url": url} for label, url in page.links],
        "enabled": bool(publication.include_imprint_page) if publication else True,
        "text": page.as_text(),
    }


@router.post("/books/{book_id}/release", response_model=PublicationResponse)
async def record_release(
    book_id: uuid.UUID,
    body: ReleaseRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Record that the author considers this book released.

    This writes a row in Authora. It does not transmit anything to Amazon KDP,
    IngramSpark, or any other retailer or distributor.
    """
    book = await get_book_for_user(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    readiness = await build_readiness(db, book, book.publication)
    if readiness["summary"]["blocking_failures"]:
        blockers = [item["reason"] for item in readiness["items"] if item["id"] in readiness["summary"]["blocking_failures"]]
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Not ready to record a release: " + " ".join(blockers),
        )
    if not body.formats:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Select at least one format for the release record.")

    publication = await get_or_create_publication(db, book)
    publication.status = "released"
    publication.released_at = body.released_at or datetime.now(timezone.utc)
    publication.release_formats = list(body.formats)
    publication.release_imprint = (body.imprint or publication.imprint or DEFAULT_IMPRINT).strip()
    publication.release_isbn = body.isbn or publication.isbn
    publication.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(publication)

    book.publication = publication
    cover = await _latest_cover(db, book_id)
    return _serialise(book, publication, cover)
