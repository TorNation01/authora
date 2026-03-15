"""Phase reference model for journey."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from authora.database import Base


class Phase(Base):
    """Reference: idea, concept, outline, drafting, revision, etc."""

    __tablename__ = "phases"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
