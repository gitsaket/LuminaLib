from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BookStatus(str, PyEnum):
    AVAILABLE = "available"
    BORROWED = "borrowed"


class SummaryStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    genre: Mapped[str | None] = mapped_column(String(100))
    published_year: Mapped[int | None] = mapped_column(Integer)

    # File storage
    file_key: Mapped[str | None] = mapped_column(String(500))  # storage object key
    file_url: Mapped[str | None] = mapped_column(String(1000))  # presigned / public URL

    # AI-generated fields
    ai_summary: Mapped[str | None] = mapped_column(Text)
    ai_review_consensus: Mapped[str | None] = mapped_column(Text)

    summary_status: Mapped[SummaryStatus] = mapped_column(
        Enum(SummaryStatus, values_callable=lambda x: [e.value for e in x]),
        default=SummaryStatus.PENDING,
    )
    average_rating: Mapped[float] = mapped_column(Float, default=0.0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[BookStatus] = mapped_column(
        Enum(BookStatus, values_callable=lambda x: [e.value for e in x]),
        default=BookStatus.AVAILABLE,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ────────────────────────────────────────────
    borrows: Mapped[list["Borrow"]] = relationship(
        back_populates="book", lazy="selectin"
    )  # noqa: F821
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="book", lazy="selectin"
    )  # noqa: F821
