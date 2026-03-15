"""Export engine interface."""

from abc import ABC, abstractmethod
from typing import Any, Literal


ExportFormat = Literal["docx", "pdf", "epub", "txt"]


class ExportEngine(ABC):
    """Abstract export engine for document formats."""

    @abstractmethod
    def export(
        self,
        format: ExportFormat,
        chapters: list[dict[str, Any]],
        book_title: str,
        author: str = "Author",
    ) -> bytes:
        """Export chapters to format. Returns raw bytes."""
        ...
