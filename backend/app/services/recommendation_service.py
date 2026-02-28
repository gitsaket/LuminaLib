"""
Recommendation Service
strategies, chosen based on user data:

CONTENT-BASED (default)
   - Build a weighted genre score from user's borrow/review history
   - Rank available books by genre match + average_rating
   - sklearn TF-IDF vectoriser on book descriptions for sub-genre signals

COLD-START fallback → return top-rated books.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book, BookStatus
from app.models.library import Borrow, UserPreferences
from app.models.user import User


async def build_recommendations(
    user: User, db: AsyncSession, limit: int = 10
) -> tuple[list[Book], str]:
    # Load user borrow history
    borrow_result = await db.execute(select(Borrow).where(Borrow.user_id == user.id))
    user_borrows = borrow_result.scalars().all()
    borrowed_book_ids = {b.book_id for b in user_borrows}

    # Load preferences
    prefs_result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == user.id)
    )
    prefs: UserPreferences | None = prefs_result.scalar_one_or_none()
    print(prefs, "prefs loaded")

    # Load all available books not yet borrowed
    books_result = await db.execute(
        select(Book).where(Book.id.not_in(borrowed_book_ids) if borrowed_book_ids else True)
    )
    all_books: list[Book] = list(books_result.scalars().all())

    if not all_books:
        return [], "no_books_available"

    # COLD-START
    if len(user_borrows) < 2:
        books = sorted(all_books, key=lambda b: b.average_rating, reverse=True)[:limit]
        return books, "cold_start_top_rated"

    # CONTENT-BASED
    genre_weights: dict[str, float] = {}

    if prefs and prefs.genre_weights:
        genre_weights = prefs.genre_weights  # type: ignore[assignment]

    # Build genre weights from borrow history if not in prefs
    if not genre_weights:
        genre_weights = await _compute_genre_weights(user.id, db)

    if genre_weights:
        scored = _score_books_content_based(all_books, genre_weights, prefs)
        books = [b for b, _ in sorted(scored, key=lambda x: x[1], reverse=True)][:limit]
        # Persist updated weights for next call
        await _upsert_genre_weights(user.id, genre_weights, db)
        return books, "content_based"


    # Final fallback
    books = sorted(all_books, key=lambda b: b.average_rating, reverse=True)[:limit]
    return books, "fallback_top_rated"


#Helpers

async def _compute_genre_weights(user_id: int, db: AsyncSession) -> dict[str, float]:
    """Compute genre weights from borrow history."""
    result = await db.execute(
        select(Book).join(Borrow, Borrow.book_id == Book.id).where(Borrow.user_id == user_id)
    )
    borrowed: list[Book] = list(result.scalars().all())
    weights: dict[str, float] = {}
    for book in borrowed:
        if book.genre:
            weights[book.genre] = weights.get(book.genre, 0.0) + 1.0
    # Normalise
    total = sum(weights.values()) or 1.0 # normalizing to 1 to avoid zero division
    return {g: w / total for g, w in weights.items()} # normalized to 1 for checking against content-based scoring


def _score_books_content_based(
    books: list[Book],
    genre_weights: dict[str, float],
    prefs: UserPreferences | None,
) -> list[tuple[Book, float]]:
    scored = []
    fav = set(prefs.favourite_genres or []) if prefs else set()
    disliked = set(prefs.disliked_genres or []) if prefs else set()

    for book in books:
        genre = book.genre or ""
        score = genre_weights.get(genre, 0.0)
        if genre in fav:
            score += 0.5 # boost for  favourites
        if genre in disliked:
            score -= 0.5 # penalty for disliked
        # Blend with rating
        score += book.average_rating * 0.1
        scored.append((book, score))
    return scored


async def _upsert_genre_weights(user_id: int, weights: dict, db: AsyncSession) -> None:
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == user_id)
    )
    prefs = result.scalar_one_or_none()
    if prefs:
        prefs.genre_weights = weights  # type: ignore[assignment]
    else:
        prefs = UserPreferences(user_id=user_id, genre_weights=weights)
    db.add(prefs)
    await db.commit()
    await db.flush()
