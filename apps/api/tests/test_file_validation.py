"""Tests for file upload validation."""

import pytest

from authora.services.file_validation import (
    validate_file_upload,
    BLOCKED_EXTENSIONS,
    ALLOWED_TYPES,
    MAX_FILE_SIZE,
)


def test_allows_valid_image():
    valid, err = validate_file_upload(
        filename="cover.jpg",
        content_type="image/jpeg",
        content_length=1024,
    )
    assert valid is True
    assert err is None


def test_allows_valid_pdf():
    valid, err = validate_file_upload(
        filename="notes.pdf",
        content_type="application/pdf",
        content_length=2 * 1024 * 1024,
    )
    assert valid is True
    assert err is None


def test_rejects_blocked_extension():
    for ext in BLOCKED_EXTENSIONS:
        valid, err = validate_file_upload(
            filename=f"malware{ext}",
            content_type="application/octet-stream",
            content_length=100,
        )
        assert valid is False
        assert "not allowed" in (err or "")


def test_rejects_oversized_file():
    valid, err = validate_file_upload(
        filename="huge.pdf",
        content_type="application/pdf",
        content_length=MAX_FILE_SIZE + 1,
    )
    assert valid is False
    assert "too large" in (err or "")


def test_rejects_disallowed_content_type():
    valid, err = validate_file_upload(
        filename="script.js",
        content_type="application/javascript",
        content_length=100,
    )
    assert valid is False
    assert "not allowed" in (err or "")


def test_allows_none_content_type_with_safe_extension():
    valid, err = validate_file_upload(
        filename="notes.txt",
        content_type=None,
        content_length=100,
    )
    # mimetypes.guess_type("notes.txt") -> ("text/plain", None)
    assert valid is True
    assert err is None


def test_custom_allowed_types():
    valid, err = validate_file_upload(
        filename="doc.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        content_length=100,
        allowed_types={"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    )
    assert valid is True
    assert err is None
