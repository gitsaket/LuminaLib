from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book


class BookRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, book_id: int) -> Book | None:
        return await self._db.get(Book, book_id)

    async def list_paginated(self, skip: int = 0, limit: int = 20) -> tuple[list[Book], int]:
        count_result = await self._db.execute(select(func.count()).select_from(Book))
        total = count_result.scalar_one()

        result = await self._db.execute(
            select(Book).order_by(Book.created_at.desc()).offset(skip).limit(limit)
        )
        books = list(result.scalars().all())
        return books, total

    async def create(self, **kwargs) -> Book:
        book = Book(**kwargs)
        self._db.add(book)
        await self._db.flush()
        await self._db.refresh(book)
        return book

    async def update(self, book: Book, **kwargs) -> Book:
        for key, value in kwargs.items():
            setattr(book, key, value)
        await self._db.flush()
        await self._db.refresh(book)
        return book

    async def delete(self, book: Book) -> None:
        await self._db.delete(book)
        await self._db.flush()
