from datetime import datetime

from pydantic import BaseModel, Field


class BookCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    author: str = Field(min_length=1, max_length=255)
    description: str | None = None
    genre: str | None = None
    published_year: int | None = None


class BookUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    author: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    genre: str | None = None
    published_year: int | None = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: str | None
    genre: str | None
    published_year: int | None
    file_url: str | None
    ai_summary: str | None
    ai_review_consensus: str | None
    summary_status: str
    average_rating: float
    review_count: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedBooksResponse(BaseModel):
    items: list[BookResponse]
    total: int
    page: int
    page_size: int


# Review Schemas

class ReviewCreateRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    body: str = Field(min_length=10)


class ReviewResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    rating: int
    body: str
    sentiment_score: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


# Borrow Schemas

class BorrowResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    status: str
    borrowed_at: datetime
    returned_at: datetime | None

    model_config = {"from_attributes": True}


# Analysis Schema

class BookAnalysisResponse(BaseModel):
    book_id: int
    ai_summary: str | None
    ai_review_consensus: str | None
    average_rating: float
    review_count: int


# Recommendation Schema

class RecommendationResponse(BaseModel):
    books: list[BookResponse]
    strategy: str

