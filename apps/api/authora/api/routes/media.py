"""Media served by the API - character portraits.

Portraits are stored under the API's own uploads directory and served through
this route so they work behind the Next.js /api proxy. Filenames are UUIDs, so
a link is unguessable; no auth header is required for an <img src>.
"""

import os
import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(tags=["media"])

PORTRAIT_DIR = "/opt/authora-v2/uploads/portraits"
SAFE_NAME = re.compile(r"^[0-9a-fA-F-]{36}\.(png|jpg|jpeg|webp|gif)$")
CONTENT_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "gif": "image/gif",
}


@router.get("/media/portraits/{filename}")
async def get_portrait(filename: str):
    if not SAFE_NAME.match(filename):
        raise HTTPException(status_code=404, detail="Not found")
    path = os.path.join(PORTRAIT_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Not found")
    ext = filename.rsplit(".", 1)[-1].lower()
    return FileResponse(
        path,
        media_type=CONTENT_TYPES.get(ext, "application/octet-stream"),
        headers={"Cache-Control": "public, max-age=604800"},
    )
