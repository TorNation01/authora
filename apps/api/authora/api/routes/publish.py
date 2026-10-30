"""Publish and release routes.

Everything here reads or writes the author's own records. Nothing is sent to a
retailer or distributor: a release is a stored record of intent.
"""

from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authora.api.dependencies import CurrentUser
from authora.database import get_db
from authora.infrastructure.storage import get_storage_provider
from authora.models import Book, BookPublication, Project, PublishingAsset, PublisherSubmission
from authora.models.publication import DEFAULT_IMPRINT
from authora.schemas.publication import (
    CoverInfo,
    PublicationResponse,
    PublicationUpdate,
    ReleaseRecord,
    ReleaseRequest,
)
from authora.services.imprint import ANEMA_HOUSE_NAME, ANEMA_HOUSE_URL, build_imprint_page
from authora.services.publishing import build_readiness, normalise_isbn
from authora.config import get_settings
from authora.schemas.submission import SubmissionRequest
from authora.services.submission import (
    PackFile,
    SubmissionError,
    build_manuscript,
    fetch_status,
    guess_type,
    submit_pack,
    word_count,
)

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


# --------------------------------------------------------------------------- publishing house


def _serialise_submission(record: PublisherSubmission) -> dict:
    return {
        "id": record.id,
        "book_id": record.book_id,
        "publisher_name": record.publisher_name,
        "publisher_url": record.publisher_url,
        "ref": record.ref,
        "status": record.status,
        "message": record.message,
        "submitted_at": record.submitted_at,
        "checked_at": record.checked_at,
        "files": record.files or [],
    }


async def _latest_submission(db: AsyncSession, book_id: uuid.UUID) -> PublisherSubmission | None:
    result = await db.execute(
        select(PublisherSubmission)
        .where(PublisherSubmission.book_id == book_id)
        .order_by(PublisherSubmission.submitted_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.get("/publishers")
async def list_publishers(current_user: CurrentUser):
    """The houses Authora can actually reach. Anema House is the default."""
    return {
        "default": ANEMA_HOUSE_NAME,
        "publishers": [
            {
                "name": ANEMA_HOUSE_NAME,
                "url": ANEMA_HOUSE_URL,
                "connected": True,
                "note": "Submissions arrive in the house's review queue with a reference number.",
            }
        ],
    }


async def _cover_is_readable(db: AsyncSession, book_id: uuid.UUID) -> bool:
    """True only when a cover row exists *and* its bytes are still in storage."""
    asset = await _latest_cover(db, book_id)
    if asset is None or not asset.file_key:
        return False
    try:
        await get_storage_provider().get(asset.file_key)
        return True
    except Exception:  # noqa: BLE001
        return False


@router.get("/books/{book_id}/submission")
async def get_submission(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """The last pack sent for this book, plus the values to prefill the form."""
    book = await get_book_for_user(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    record = await _latest_submission(db, book_id)
    publication = book.publication
    chapters = [c for c in book.chapters if c.deleted_at is None]
    pitch = (publication.blurb if publication else None) or (publication.short_description if publication else None) or ""

    return {
        "submission": _serialise_submission(record) if record else None,
        "defaults": {
            "publisher_name": ANEMA_HOUSE_NAME,
            "author_name": (publication.author_name if publication and publication.author_name else current_user.display_name) or "",
            "email": current_user.email,
            "title": (publication.title if publication and publication.title else book.title) or "",
            "series": "",
            "genre": (book.genre or ""),
            "word_count": sum(int(c.word_count or 0) for c in chapters),
            "pitch": pitch,
        },
        "pack": {
            "chapters": len(chapters),
            "has_cover": await _cover_is_readable(db, book_id),
        },
    }


@router.post("/books/{book_id}/submission", status_code=status.HTTP_201_CREATED)
async def create_submission(
    book_id: uuid.UUID,
    body: SubmissionRequest,
    background: BackgroundTasks,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Pack the book and hand it to the publishing house.

    The author sees exactly what was sent and the reference the house returned.
    A refusal from the house is reported as-is; nothing is retried silently.
    """
    book = await get_book_for_user(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if body.publisher_name.strip() != ANEMA_HOUSE_NAME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {ANEMA_HOUSE_NAME} is connected. Other houses have no submission channel yet.",
        )

    chapters = [c for c in book.chapters if c.deleted_at is None]
    if not chapters:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This book has no chapters to send.")

    pack = build_manuscript(book, chapters, body.author_name)
    if len(pack.content) < 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The manuscript is empty — write something before sending it to a house.",
        )

    files = [pack]
    attached = [{"name": pack.filename, "kind": "manuscript", "bytes": len(pack.content)}]

    cover_asset = await _latest_cover(db, book_id) if body.include_cover else None
    cover_skipped = False
    if cover_asset and cover_asset.file_key:
        try:
            cover_bytes = await get_storage_provider().get(cover_asset.file_key)
            cover_type = (cover_asset.asset_metadata or {}).get("content_type") or guess_type(cover_asset.file_key)
            suffix = "." + cover_asset.file_key.rsplit(".", 1)[-1] if "." in cover_asset.file_key else ".jpg"
            cover_name = pack.filename.rsplit(" - manuscript.md", 1)[0] + " - cover" + suffix
            files.append(PackFile(filename=cover_name, content=cover_bytes, content_type=cover_type))
            attached.append({"name": cover_name, "kind": "cover", "bytes": len(cover_bytes)})
        except Exception:  # noqa: BLE001 - a missing cover must not block the submission
            # The record in the database points at a file that is no longer in
            # storage. Send the manuscript alone and tell the author plainly.
            cover_skipped = True

    payload = {
        "name": body.author_name.strip()[:120],
        "email": body.email.strip()[:200],
        "title": body.title.strip()[:200],
        "series": body.series.strip()[:160],
        "genre": body.genre.strip()[:80],
        # An author who leaves the word-count box blank still has a manuscript
        # with a length. Send the manuscript's own count, never a bare zero.
        "word_count": str(body.word_count or word_count(chapters) or 0),
        "pitch": body.pitch.strip()[:4000],
        "source": "authora",
    }

    received = None
    try:
        received = await submit_pack(
            base_url=get_settings().anema_intake_url,
            payload=payload,
            files=files,
        )
    except SubmissionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    ref = (received or {}).get("ref") or ""
    if not ref:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The house did not return a reference number — the pack may not have been stored.",
        )

    record = PublisherSubmission(
        book_id=book.id,
        user_id=current_user.id,
        publisher_name=ANEMA_HOUSE_NAME,
        publisher_url=ANEMA_HOUSE_URL,
        ref=ref,
        status=(received or {}).get("status") or "received",
        message=(received or {}).get("message"),
        payload=payload,
        files=attached,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    # The house reference is the customer's only handle on the submission.
    # Send it to them; do not make them hunt for it in the UI.
    from authora.services.transactional_email import send_submission_received

    background.add_task(
        send_submission_received,
        current_user.email,
        book_title=book.title,
        reference=ref,
    )

    return {
        "submission": _serialise_submission(record),
        "receipt": received,
        "sent": attached,
        "cover_skipped": cover_skipped,
    }


@router.post("/books/{book_id}/submission/refresh")
async def refresh_submission(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Ask the house what it thinks of the pack now."""
    book = await get_book_for_user(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    record = await _latest_submission(db, book_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nothing has been sent for this book yet.")

    try:
        answer = await fetch_status(
            base_url=get_settings().anema_intake_url,
            ref=record.ref,
            email=(record.payload or {}).get("email") or current_user.email,
        )
    except SubmissionError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    record.status = answer.get("status") or record.status
    record.checked_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(record)

    return {"submission": _serialise_submission(record), "answer": answer}
