import json
from typing import Annotated

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
    BackgroundTasks,
)
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DBSession
from app.models.book import Book, BookStatus
from app.models.library import Borrow, BorrowStatus, Review
from app.repositories.book_repository import BookRepository
from app.schemas.books import (
    BookAnalysisResponse,
    BookResponse,
    BookUpdateRequest,
    BorrowResponse,
    PaginatedBooksResponse,
    RecommendationResponse,
    ReviewCreateRequest,
    ReviewResponse,
)
from app.services.storage.storage_service import get_storage_service
from app.tasks.background import generate_book_summary, update_review

router = APIRouter(prefix="/books", tags=["books"])

ALLOWED_CONTENT_TYPES = {"application/pdf", "text/plain"}


# POST /books


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    current_user: CurrentUser,
    db: DBSession,
    title: Annotated[str, Form()],
    author: Annotated[str, Form()],
    description: Annotated[str | None, Form()] = None,
    genre: Annotated[str | None, Form()] = None,
    published_year: Annotated[int | None, Form()] = None,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> BookResponse:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Only PDF or plain text accepted"
        )

    content = await file.read()
    storage = get_storage_service()
    key = await storage.upload_file(content, file.filename or "book", file.content_type)
    url = await storage.get_url(key)

    repo = BookRepository(db)
    book = await repo.create(
        title=title,
        author=author,
        description=description,
        genre=genre,
        published_year=published_year,
        file_key=key,
        file_url=url,
    )

    # Fire async summary task
    background_tasks.add_task(generate_book_summary, book.id)

    return BookResponse.model_validate(book)


# GET /books


@router.get("", response_model=PaginatedBooksResponse)
async def list_books(
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedBooksResponse:
    skip = (page - 1) * page_size
    repo = BookRepository(db)
    books, total = await repo.list_paginated(skip=skip, limit=page_size)
    return PaginatedBooksResponse(
        items=[BookResponse.model_validate(b) for b in books],
        total=total,
        page=page,
        page_size=page_size,
    )


# PUT /books/{id}


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    payload: BookUpdateRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> BookResponse:
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")

    updates = payload.model_dump(exclude_unset=True)
    book = await repo.update(book, **updates)
    return BookResponse.model_validate(book)


# DELETE /books/{id}


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, current_user: CurrentUser, db: DBSession) -> None:
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")

    if book.file_key:
        storage = get_storage_service()
        await storage.delete_file(book.file_key)

    await repo.delete(book)


# POST /books/{id}/borrow


@router.post(
    "/{book_id}/borrow",
    response_model=BorrowResponse,
    status_code=status.HTTP_201_CREATED,
)
async def borrow_book(
    book_id: int, current_user: CurrentUser, db: DBSession
) -> BorrowResponse:
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
    if book.status != BookStatus.AVAILABLE:
        raise HTTPException(status.HTTP_409_CONFLICT, "Book is currently borrowed")

    # Check user doesn't already have it
    existing = await db.execute(
        select(Borrow).where(
            Borrow.user_id == current_user.id,
            Borrow.book_id == book_id,
            Borrow.status == BorrowStatus.ACTIVE,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status.HTTP_409_CONFLICT, "You already have this book borrowed"
        )

    borrow = Borrow(user_id=current_user.id, book_id=book_id)
    db.add(borrow)
    book.status = BookStatus.BORROWED
    await db.flush()
    await db.refresh(borrow)
    return BorrowResponse.model_validate(borrow)


@router.get(
    "/{user_id}/borrowed",
    response_model=list[BorrowResponse],
    status_code=status.HTTP_200_OK,
)
async def list_borrowed_books(
    user_id: int, current_user: CurrentUser, db: DBSession
) -> list[BorrowResponse]:
    if user_id != current_user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Cannot view other user's borrows"
        )

    result = await db.execute(
        select(Borrow)
        .where(Borrow.user_id == user_id, Borrow.status == BorrowStatus.ACTIVE.value)
        .order_by(Borrow.borrowed_at.desc())
    )
    borrows = result.scalars().all()
    return [BorrowResponse.model_validate(b) for b in borrows]


# POST /books/{id}/return


@router.post("/{book_id}/return", response_model=BorrowResponse)
async def return_book(
    book_id: int, current_user: CurrentUser, db: DBSession
) -> BorrowResponse:
    result = await db.execute(
        select(Borrow).where(
            Borrow.user_id == current_user.id,
            Borrow.book_id == book_id,
            Borrow.status == BorrowStatus.ACTIVE.value,
        )
    )
    borrow = result.scalar_one_or_none()
    if not borrow:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "No active borrow found for this book"
        )

    from datetime import datetime, timezone

    borrow.status = BorrowStatus.RETURNED.value
    borrow.returned_at = datetime.now(timezone.utc)

    book = await db.get(Book, book_id)
    if book:
        book.status = BookStatus.AVAILABLE

    await db.flush()
    await db.refresh(borrow)
    return BorrowResponse.model_validate(borrow)


# POST /books/{id}/reviews


@router.post(
    "/{book_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    book_id: int,
    payload: ReviewCreateRequest,
    current_user: CurrentUser,
    db: DBSession,
    background_tasks: BackgroundTasks,
) -> ReviewResponse:
    # Verify user has borrowed this book
    borrow_result = await db.execute(
        select(Borrow).where(
            Borrow.user_id == current_user.id,
            Borrow.book_id == book_id,
            Borrow.status == BorrowStatus.ACTIVE.value,
        )
    )
    if not borrow_result.scalar_one_or_none():
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "You must borrow a book before reviewing it"
        )

    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")

    review = Review(
        user_id=current_user.id,
        book_id=book_id,
        rating=payload.rating,
        body=payload.body,
    )
    db.add(review)
    await db.flush()
    await db.refresh(review)

    # Trigger background task for update
    background_tasks.add_task(update_review, book_id)

    return ReviewResponse.model_validate(review)


# GET /books/{id}/analysis


@router.get("/{book_id}/analysis", response_model=BookAnalysisResponse)
async def get_book_analysis(book_id: int, db: DBSession) -> BookAnalysisResponse:
    book = await db.get(Book, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
    return BookAnalysisResponse(
        book_id=book.id,
        ai_summary=book.ai_summary,
        ai_review_consensus=book.ai_review_consensus,
        average_rating=book.average_rating,
        review_count=book.review_count,
    )
