"""Book type reference model."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from authora.database import Base


class BookType(Base):
    """Reference: fiction, nonfiction, etc."""

    __tablename__ = "book_types"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
