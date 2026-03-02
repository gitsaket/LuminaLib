from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BorrowStatus(str, PyEnum):
    ACTIVE = "active"
    RETURNED = "returned"


class Borrow(Base):
    __tablename__ = "borrows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[BorrowStatus] = mapped_column(
        Enum(BorrowStatus, values_callable=lambda x: [e.value for e in x]),
        default=BorrowStatus.ACTIVE,
    )
    borrowed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    returned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="borrows")  
    book: Mapped["Book"] = relationship(back_populates="borrows")  


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"), index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    body: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment_score: Mapped[float | None] = mapped_column(Float)  # -1 to 1
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="reviews")  
    book: Mapped["Book"] = relationship(back_populates="reviews")  


class UserPreferences(Base):
    """
    Stores per-user signals used by the recommendation engine.

    Design rationale (explained in ARCHITECTURE.md):
    - favourite_genres / disliked_genres: explicit user signals
    - genre_weights (JSONB): ML-updated map of {genre: score} derived from
      borrow/review history; allows fine-grained preference modelling
    - min_rating_threshold: collaborative filter lower bound
    """

    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )

    # Explicit preferences (user-set)
    favourite_genres: Mapped[list[str] | None] = mapped_column(JSONB, default=list)
    disliked_genres: Mapped[list[str] | None] = mapped_column(JSONB, default=list)

    # ML-derived preferences
    genre_weights: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    min_rating_threshold: Mapped[float] = mapped_column(Float, default=3.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="preferences")  # noqa: F821
