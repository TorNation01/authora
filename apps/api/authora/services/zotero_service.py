"""Zotero integration: sync items, map to vault sources, handle failures."""

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from pyzotero import zotero
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Source, ZoteroConnection

logger = logging.getLogger(__name__)


def _zotero_client(conn: ZoteroConnection) -> zotero.Zotero:
    """Create pyzotero client from connection."""
    lib_type = "user" if conn.library_type == "user" else "group"
    return zotero.Zotero(conn.library_id, lib_type, conn.api_key)


def _zotero_item_to_csl(item: dict) -> dict[str, Any] | None:
    """Convert Zotero API item to CSL JSON format."""
    data = item.get("data", {})
    if not data:
        return None
    # Zotero items have 'key', 'itemType', 'creators', 'title', etc.
    # Map to CSL: id, type, author (from creators), title, issued, etc.
    item_type = data.get("itemType", "journalArticle")
    csl_type_map = {
        "journalArticle": "article-journal",
        "book": "book",
        "bookSection": "chapter",
        "conferencePaper": "paper-conference",
        "thesis": "thesis",
        "report": "report",
        "webpage": "webpage",
        "blogPost": "post",
        "document": "document",
        "other": "article",
    }
    csl_type = csl_type_map.get(item_type, "article")

    creators = data.get("creators", [])
    author = []
    for c in creators:
        if c.get("creatorType") in ("author", "editor", "contributor"):
            name = {}
            if c.get("name"):
                name["literal"] = c["name"]
            else:
                if c.get("lastName"):
                    name["family"] = c["lastName"]
                if c.get("firstName"):
                    name["given"] = c["firstName"]
            if name:
                author.append(name)

    date_parts = []
    date_str = data.get("date", "")
    if date_str:
        try:
            year = int(date_str[:4]) if len(date_str) >= 4 else 0
            date_parts.append([year])
        except (ValueError, TypeError):
            date_parts.append([0])

    csl = {
        "id": data.get("key", "").lower(),
        "type": csl_type,
        "title": data.get("title", ""),
        "author": author if author else [{"literal": "Unknown"}],
        "issued": {"date-parts": date_parts} if date_parts else None,
        "publisher": data.get("publisher"),
        "volume": data.get("volume"),
        "issue": data.get("issue"),
        "page": data.get("pages"),
        "DOI": data.get("DOI"),
        "URL": data.get("url"),
        "abstract": data.get("abstractNote"),
    }
    return {k: v for k, v in csl.items() if v is not None}


def _zotero_item_to_source_attrs(item: dict, project_id: UUID, zotero_connection_id: UUID) -> dict[str, Any]:
    """Map Zotero item to vault Source attributes."""
    data = item.get("data", {})
    csl = _zotero_item_to_csl(item)
    creators = data.get("creators", [])
    author_parts = []
    for c in creators:
        if c.get("creatorType") == "author":
            if c.get("name"):
                author_parts.append(c["name"])
            elif c.get("lastName"):
                author_parts.append(c.get("firstName", "") + " " + c["lastName"] if c.get("firstName") else c["lastName"])
    author = ", ".join(author_parts) if author_parts else None
    return {
        "project_id": project_id,
        "zotero_connection_id": zotero_connection_id,
        "zotero_item_key": data.get("key"),
        "zotero_version": data.get("version", 0),
        "csl_json": csl,
        "title": data.get("title", "Untitled"),
        "author": author,
        "source_type": _map_zotero_type(data.get("itemType", "journalArticle")),
        "publication_date": data.get("date"),
        "url": data.get("url"),
        "topic_tags": data.get("tags", []),
        "status": "verified",
    }


def _map_zotero_type(zotero_type: str) -> str:
    """Map Zotero item type to vault source_type."""
    m = {
        "journalArticle": "article",
        "book": "book",
        "bookSection": "book",
        "conferencePaper": "document",
        "thesis": "document",
        "report": "document",
        "webpage": "website",
        "blogPost": "website",
        "document": "document",
    }
    return m.get(zotero_type, "other")


async def verify_zotero_connection(conn: ZoteroConnection) -> tuple[bool, str]:
    """Verify Zotero API key and library access. Returns (ok, message)."""
    try:
        zot = _zotero_client(conn)
        zot.num_items()
        return True, "Connected"
    except Exception as e:
        logger.warning("Zotero verify failed: %s", e)
        return False, str(e)


async def sync_zotero_to_project(
    db: AsyncSession,
    conn: ZoteroConnection,
    project_id: UUID,
    *,
    since_version: int | None = None,
) -> tuple[int, str]:
    """
    Sync Zotero items to project vault sources.
    Returns (items_synced, error_message or empty).
    """
    conn.sync_status = "syncing"
    conn.sync_error = None
    await db.flush()

    try:
        zot = _zotero_client(conn)
        items = zot.everything(zot.top())
        synced = 0

        for item in items:
            data = item.get("data", {})
            key = data.get("key")
            if not key:
                continue
            existing = await db.execute(
                select(Source).where(
                    Source.project_id == project_id,
                    Source.zotero_item_key == key,
                )
            )
            src = existing.scalar_one_or_none()
            attrs = _zotero_item_to_source_attrs(item, project_id, conn.id)
            if src:
                for k, v in attrs.items():
                    if k != "project_id":
                        setattr(src, k, v)
            else:
                src = Source(**attrs)
                db.add(src)
            synced += 1

        conn.last_synced_at = datetime.now(timezone.utc)
        conn.last_sync_version = max((d.get("version", 0) for d in (i.get("data", {}) for i in items) if d), default=conn.last_sync_version or 0)
        conn.sync_status = "synced"
        conn.sync_error = None
        await db.flush()
        return synced, ""
    except Exception as e:
        conn.sync_status = "error"
        conn.sync_error = str(e)
        await db.flush()
        logger.exception("Zotero sync failed: %s", e)
        return 0, str(e)
