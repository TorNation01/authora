"""File upload validation and protection."""

import mimetypes
from pathlib import Path

# Allowed MIME types for uploads
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "text/plain", "text/markdown"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES

# Max file sizes (bytes)
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_FILE_SIZE = max(MAX_IMAGE_SIZE, MAX_DOCUMENT_SIZE)

# Dangerous extensions
BLOCKED_EXTENSIONS = {".exe", ".bat", ".cmd", ".sh", ".ps1", ".js", ".vbs", ".jar", ".dll"}


def _is_path_traversal_safe(filename: str) -> bool:
    """Reject path traversal attempts (.., absolute paths)."""
    p = Path(filename)
    if p.is_absolute():
        return False
    parts = p.parts
    if ".." in parts or (parts and parts[0] == ".."):
        return False
    return True


def validate_file_upload(
    filename: str,
    content_type: str | None,
    content_length: int,
    allowed_types: set[str] | None = None,
    max_size: int | None = None,
) -> tuple[bool, str | None]:
    """
    Validate file upload. Returns (valid, error_message).
    """
    allowed = allowed_types or ALLOWED_TYPES
    max_sz = max_size or MAX_FILE_SIZE

    if not filename or not _is_path_traversal_safe(filename):
        return False, "Invalid filename"

    ext = Path(filename).suffix.lower()
    if ext in BLOCKED_EXTENSIONS:
        return False, "File type not allowed"

    if content_length > max_sz:
        return False, f"File too large (max {max_sz // (1024 * 1024)} MB)"

    guessed = mimetypes.guess_type(filename)[0]
    effective_type = (content_type or "").split(";")[0].strip() or guessed
    if not effective_type or effective_type not in allowed:
        return False, "File type not allowed"

    return True, None
