"""
Recommendation API endpoint.

Strategy: Hybrid Content-Based + Collaborative Filtering
- Content-based: match books to user's genre_weights and favourite_genres
- Collaborative: find users with similar borrow history, surface their reads
- Falls back to top-rated books for cold-start users
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DBSession
from app.models.book import Book, BookStatus
from app.models.library import Borrow, UserPreferences
from app.schemas.books import BookResponse, RecommendationResponse

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationResponse)
async def get_recommendations(current_user: CurrentUser, db: DBSession) -> RecommendationResponse:
    from app.services.recommendation_service import build_recommendations

    books, strategy = await build_recommendations(current_user, db)
    return RecommendationResponse(
        books=[BookResponse.model_validate(b) for b in books],
        strategy=strategy,
    )
