"""Integration tests for borrow, return, review, and analysis endpoints."""
import io
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book


def _mock_storage():
    mock = AsyncMock()
    mock.upload_file.return_value = "fake-key"
    mock.get_url.return_value = "http://storage/fake-key"
    mock.delete_file.return_value = None
    return patch(
        "app.api.v1.endpoints.books.get_storage_service", return_value=mock
    )


def _mock_background():
    return patch("app.api.v1.endpoints.books.generate_book_summary")


def _mock_review_bg():
    return patch("app.api.v1.endpoints.books.update_review")


async def _create_book(client: AsyncClient, auth_headers: dict) -> int:
    """Helper: upload a book and return its id."""
    with _mock_storage(), _mock_background():
        resp = await client.post(
            "/api/v1/books",
            headers=auth_headers,
            files={"file": ("b.txt", io.BytesIO(b"content"), "text/plain")},
            data={"title": "Test Book", "author": "Author"},
        )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _second_user_headers(client: AsyncClient) -> dict[str, str]:
    """Register and log in a second user."""
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "bob@example.com",
            "username": "bob",
            "password": "password123",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "bob@example.com", "password": "password123"},
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


#Borrow

async def test_borrow_book_success(client: AsyncClient, auth_headers: dict):
    book_id = await _create_book(client, auth_headers)
    resp = await client.post(
        f"/api/v1/books/{book_id}/borrow", headers=auth_headers
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "active"
    assert data["book_id"] == book_id


async def test_borrow_already_borrowed_by_another(
    client: AsyncClient, auth_headers: dict
):
    book_id = await _create_book(client, auth_headers)
    # First user borrows
    await client.post(f"/api/v1/books/{book_id}/borrow", headers=auth_headers)
    # Second user tries to borrow same book
    bob_headers = await _second_user_headers(client)
    resp = await client.post(
        f"/api/v1/books/{book_id}/borrow", headers=bob_headers
    )
    assert resp.status_code == 409


async def test_borrow_same_user_re_borrow(
    client: AsyncClient, auth_headers: dict, db_session: AsyncSession
):
    book_id = await _create_book(client, auth_headers)
    await client.post(f"/api/v1/books/{book_id}/borrow", headers=auth_headers)

    # Force book back to available to test the user duplicate check
    book = await db_session.get(Book, book_id)
    from app.models.book import BookStatus
    book.status = BookStatus.AVAILABLE  # type: ignore[union-attr]
    await db_session.flush()

    resp = await client.post(
        f"/api/v1/books/{book_id}/borrow", headers=auth_headers
    )
    assert resp.status_code == 409


# Return

async def test_return_book_success(client: AsyncClient, auth_headers: dict):
    book_id = await _create_book(client, auth_headers)
    await client.post(f"/api/v1/books/{book_id}/borrow", headers=auth_headers)
    resp = await client.post(
        f"/api/v1/books/{book_id}/return", headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "returned"


async def test_return_book_no_active_borrow(
    client: AsyncClient, auth_headers: dict
):
    book_id = await _create_book(client, auth_headers)
    resp = await client.post(
        f"/api/v1/books/{book_id}/return", headers=auth_headers
    )
    assert resp.status_code == 404


#Borrowed list

async def test_list_borrowed_books(client: AsyncClient, auth_headers: dict):
    # Get current user id from /me
    me_resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    user_id = me_resp.json()["id"]

    book_id = await _create_book(client, auth_headers)
    await client.post(f"/api/v1/books/{book_id}/borrow", headers=auth_headers)

    resp = await client.get(
        f"/api/v1/books/{user_id}/borrowed", headers=auth_headers
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_list_borrowed_books_forbidden(
    client: AsyncClient, auth_headers: dict
):
    # Try to view another user's borrows
    bob_headers = await _second_user_headers(client)
    me_resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    user_id = me_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/books/{user_id}/borrowed", headers=bob_headers
    )
    assert resp.status_code == 403


# Reviews

async def test_create_review_success(client: AsyncClient, auth_headers: dict):
    book_id = await _create_book(client, auth_headers)
    await client.post(f"/api/v1/books/{book_id}/borrow", headers=auth_headers)

    with _mock_review_bg():
        resp = await client.post(
            f"/api/v1/books/{book_id}/reviews",
            headers=auth_headers,
            json={"rating": 4, "body": "A great read with interesting insights."},
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["rating"] == 4
    assert data["book_id"] == book_id


async def test_create_review_without_borrow(
    client: AsyncClient, auth_headers: dict
):
    book_id = await _create_book(client, auth_headers)
    with _mock_review_bg():
        resp = await client.post(
            f"/api/v1/books/{book_id}/reviews",
            headers=auth_headers,
            json={"rating": 5, "body": "Trying without borrowing first."},
        )
    assert resp.status_code == 403


# Analysis

async def test_get_book_analysis(client: AsyncClient, auth_headers: dict):
    book_id = await _create_book(client, auth_headers)
    resp = await client.get(f"/api/v1/books/{book_id}/analysis")
    assert resp.status_code == 200
    data = resp.json()
    assert data["book_id"] == book_id
    assert "average_rating" in data
    assert "review_count" in data


async def test_get_book_analysis_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/books/99999/analysis")
    assert resp.status_code == 404
