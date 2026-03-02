"""Pure unit tests for the recommendation service (no real DB)."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.book import Book, BookStatus
from app.models.library import Borrow, UserPreferences
from app.models.user import User
from app.services.recommendation_service import (
    _compute_genre_weights,
    _score_books_content_based,
    build_recommendations,
)

def _make_book(id: int, genre: str = "Fiction", rating: float = 3.0) -> Book:
    b = Book()
    b.id = id
    b.title = f"Book {id}"
    b.author = "Author"
    b.genre = genre
    b.average_rating = rating
    b.status = BookStatus.AVAILABLE
    b.review_count = 0
    b.summary_status = "pending"  # type: ignore[assignment]
    return b


def _make_db(borrows: list, books_result: list) -> AsyncMock:
    """Build a minimal async DB mock."""
    db = AsyncMock()

    borrow_scalars = MagicMock()
    borrow_scalars.all.return_value = borrows

    borrow_execute_result = MagicMock()
    borrow_execute_result.scalars.return_value = borrow_scalars

    prefs_execute_result = MagicMock()
    prefs_execute_result.scalar_one_or_none.return_value = None

    books_scalars = MagicMock()
    books_scalars.all.return_value = books_result

    books_execute_result = MagicMock()
    books_execute_result.scalars.return_value = books_scalars

    # execute is called three times: borrows, prefs, available books
    db.execute = AsyncMock(
        side_effect=[
            borrow_execute_result,
            prefs_execute_result,
            books_execute_result,
        ]
    )
    return db



async def test_compute_genre_weights_empty_history():
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=result)

    weights = await _compute_genre_weights(1, db)
    assert weights == {}


async def test_compute_genre_weights_normalises():
    # 2 Fiction, 1 History → Fiction=2/3, History=1/3
    books = [
        _make_book(1, "Fiction"),
        _make_book(2, "Fiction"),
        _make_book(3, "History"),
    ]
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = books
    db.execute = AsyncMock(return_value=result)

    weights = await _compute_genre_weights(1, db)
    assert abs(weights["Fiction"] - 2 / 3) < 1e-9
    assert abs(weights["History"] - 1 / 3) < 1e-9
    assert abs(sum(weights.values()) - 1.0) < 1e-9


def test_score_applies_genre_weight():
    books = [_make_book(1, "Fiction", rating=0.0)]
    weights = {"Fiction": 0.7}
    scored = _score_books_content_based(books, weights, None)
    assert abs(scored[0][1] - 0.7) < 1e-9


def test_score_favourite_genre_boost():
    books = [_make_book(1, "Fantasy", rating=0.0)]
    weights = {"Fantasy": 0.0}
    prefs = MagicMock(spec=UserPreferences)
    prefs.favourite_genres = ["Fantasy"]
    prefs.disliked_genres = []
    scored = _score_books_content_based(books, weights, prefs)
    assert abs(scored[0][1] - 0.5) < 1e-9  # 0.0 weight + 0.5 boost


def test_score_disliked_genre_penalty():
    books = [_make_book(1, "Horror", rating=0.0)]
    weights = {"Horror": 0.0}
    prefs = MagicMock(spec=UserPreferences)
    prefs.favourite_genres = []
    prefs.disliked_genres = ["Horror"]
    scored = _score_books_content_based(books, weights, prefs)
    assert abs(scored[0][1] - (-0.5)) < 1e-9


def test_score_rating_blended():
    books = [_make_book(1, "Science", rating=5.0)]
    weights = {"Science": 0.0}
    scored = _score_books_content_based(books, weights, None)
    assert abs(scored[0][1] - 0.5) < 1e-9  # 5.0 * 0.1


async def test_build_recommendations_cold_start():
    """< 2 borrows → cold start strategy, sorted by rating."""
    user = MagicMock(spec=User)
    user.id = 1

    books = [
        _make_book(1, "Fiction", rating=4.5),
        _make_book(2, "History", rating=2.0),
        _make_book(3, "Science", rating=5.0),
    ]
    db = _make_db(borrows=[], books_result=books)

    result_books, strategy = await build_recommendations(user, db, limit=10)
    assert strategy == "cold_start_top_rated"
    assert result_books[0].average_rating >= result_books[-1].average_rating


async def test_build_recommendations_content_based():
    """≥ 2 borrows → content-based strategy."""
    user = MagicMock(spec=User)
    user.id = 1

    borrow1 = MagicMock(spec=Borrow)
    borrow1.user_id = 1
    borrow1.book_id = 10

    borrow2 = MagicMock(spec=Borrow)
    borrow2.user_id = 1
    borrow2.book_id = 11

    available_books = [
        _make_book(20, "Fiction", rating=3.0),
        _make_book(21, "History", rating=4.0),
    ]

    db = AsyncMock()

    borrow_scalars = MagicMock()
    borrow_scalars.all.return_value = [borrow1, borrow2]
    borrow_result = MagicMock()
    borrow_result.scalars.return_value = borrow_scalars

    prefs_result = MagicMock()
    prefs_result.scalar_one_or_none.return_value = None

    avail_scalars = MagicMock()
    avail_scalars.all.return_value = available_books
    avail_result = MagicMock()
    avail_result.scalars.return_value = avail_scalars

    # For _compute_genre_weights: books joined with borrows
    genre_books_scalars = MagicMock()
    genre_books_scalars.all.return_value = [
        _make_book(10, "Fiction"),
        _make_book(11, "Fiction"),
    ]
    genre_result = MagicMock()
    genre_result.scalars.return_value = genre_books_scalars

    # _upsert_genre_weights also calls execute
    upsert_prefs_result = MagicMock()
    upsert_prefs_result.scalar_one_or_none.return_value = None

    db.execute = AsyncMock(
        side_effect=[
            borrow_result,
            prefs_result,
            avail_result,
            genre_result,
            upsert_prefs_result,
        ]
    )
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.flush = AsyncMock()

    result_books, strategy = await build_recommendations(user, db, limit=10)
    assert strategy == "content_based"
    assert len(result_books) > 0
