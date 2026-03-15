"""Default export engine implementation."""

from typing import Any

from authora.infrastructure.export_engine.base import ExportEngine, ExportFormat
from authora.services.export import (
    export_docx,
    export_epub,
    export_pdf,
    export_txt,
)


class DefaultExportEngine(ExportEngine):
    """Default export engine using python-docx, reportlab, ebooklib."""

    def export(
        self,
        format: ExportFormat,
        chapters: list[dict[str, Any]],
        book_title: str,
        author: str = "Author",
    ) -> bytes:
        if format == "txt":
            return export_txt(chapters)
        if format == "docx":
            return export_docx(chapters, book_title)
        if format == "pdf":
            return export_pdf(chapters, book_title)
        if format == "epub":
            return export_epub(chapters, book_title, author)
        raise ValueError(f"Unsupported format: {format}")
