"""
All LLM generation is offloaded here so that HTTP responses remain fast.
"""

import asyncio
import logging

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


# Helper: run async code


def _run(coro):
    return asyncio.run(coro)


# Task: Generate book summary


def generate_book_summary(book_id: int) -> None:
    """Read book content from storage, call LLM, persist summary."""
    try:
        _run(_generate_book_summary_async(book_id))
    except Exception as exc:
        logger.exception("generate_book_summary failed for book %s", book_id)


async def _generate_book_summary_async(book_id: int) -> None:
    from app.db.session import AsyncSessionLocal
    from app.models.book import Book, SummaryStatus
    from app.services.llm.llm_service import (
        BOOK_SUMMARY_SYSTEM,
        build_summary_prompt,
        get_llm_service,
    )
    from app.services.storage.storage_service import get_storage_service
    from app.utils.text_extraction import extract_text

    async with AsyncSessionLocal() as db:
        book = await db.get(Book, book_id)
        if not book or not book.file_key:
            return

        book.summary_status = SummaryStatus.PROCESSING
        await db.commit()

        try:
            storage = get_storage_service()
            raw_bytes = await storage.read_file(book.file_key)
            content_text = extract_text(raw_bytes, book.file_key)[
                : settings.MAX_CONTENT_LENGTH
            ]  # because of LLM input limits

            llm = get_llm_service()
            summary = await llm.complete(
                system_prompt=BOOK_SUMMARY_SYSTEM,
                user_prompt=build_summary_prompt(book.title, book.author, content_text),
                max_tokens=400,
            )

            book.ai_summary = summary
            book.summary_status = SummaryStatus.COMPLETED
        except Exception:
            book.summary_status = SummaryStatus.FAILED
            raise
        finally:
            await db.commit()


# Task: Update review
def update_review(book_id: int) -> None:
    try:
        _run(_update_review_async(book_id))
    except Exception as exc:
        logger.exception("update_review_consensus failed for book %s", book_id)


async def _update_review_async(book_id: int) -> None:
    from sqlalchemy import select

    from app.db.session import AsyncSessionLocal
    from app.models.book import Book
    from app.models.library import Review
    from app.services.llm.llm_service import (
        REVIEW_CONSENSUS_SYSTEM,
        build_review_consensus_prompt,
        get_llm_service,
    )

    async with AsyncSessionLocal() as db:
        book = await db.get(Book, book_id)
        if not book:
            return

        result = await db.execute(select(Review).where(Review.book_id == book_id))
        reviews = result.scalars().all()
        if not reviews:
            return

        review_dicts = [{"rating": r.rating, "body": r.body} for r in reviews]

        llm = get_llm_service()
        consensus = await llm.complete(
            system_prompt=REVIEW_CONSENSUS_SYSTEM,
            user_prompt=build_review_consensus_prompt(book.title, review_dicts),
            max_tokens=300,
        )

        book.ai_review_consensus = consensus
        book.review_count = len(reviews)
        book.average_rating = sum(r.rating for r in reviews) / len(reviews)
        await db.commit()
