"""Integration tests for /api/v1/books endpoints (SQLite in-memory)."""
import io
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


def _txt_file(name: str = "book.txt", content: str = "Hello world") -> tuple:
    return (name, io.BytesIO(content.encode()), "text/plain")


def _mock_storage():
    """Return a patch context that mocks the storage service."""
    mock = AsyncMock()
    mock.upload_file.return_value = "fake-key"
    mock.get_url.return_value = "http://storage/fake-key"
    mock.delete_file.return_value = None
    return patch(
        "app.api.v1.endpoints.books.get_storage_service", return_value=mock
    )


def _mock_background():
    """Patch background tasks so they don't hit real DB/LLM."""
    return patch("app.api.v1.endpoints.books.generate_book_summary")


# List books

async def test_list_books_empty(client: AsyncClient):
    resp = await client.get("/api/v1/books")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


async def test_list_books_paginated(client: AsyncClient, auth_headers: dict):
    with _mock_storage(), _mock_background():
        for i in range(3):
            await client.post(
                "/api/v1/books",
                headers=auth_headers,
                files={"file": _txt_file(f"book{i}.txt")},
                data={"title": f"Book {i}", "author": "Author"},
            )

    resp = await client.get("/api/v1/books?page=1&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2


# Create book

async def test_create_book_success(client: AsyncClient, auth_headers: dict):
    with _mock_storage(), _mock_background():
        resp = await client.post(
            "/api/v1/books",
            headers=auth_headers,
            files={"file": _txt_file()},
            data={"title": "My Book", "author": "Jane Doe", "genre": "Fiction"},
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Book"
    assert data["author"] == "Jane Doe"
    assert data["status"] == "available"


async def test_create_book_rejects_unsupported_type(
    client: AsyncClient, auth_headers: dict
):
    with _mock_storage(), _mock_background():
        resp = await client.post(
            "/api/v1/books",
            headers=auth_headers,
            files={"file": ("book.exe", io.BytesIO(b"data"), "application/octet-stream")},
            data={"title": "Bad Book", "author": "Author"},
        )
    assert resp.status_code == 415


# Update book

async def test_update_book_title(client: AsyncClient, auth_headers: dict):
    with _mock_storage(), _mock_background():
        create_resp = await client.post(
            "/api/v1/books",
            headers=auth_headers,
            files={"file": _txt_file()},
            data={"title": "Original Title", "author": "Author"},
        )
    book_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/books/{book_id}",
        headers=auth_headers,
        json={"title": "Updated Title"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


async def test_update_book_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.put(
        "/api/v1/books/99999",
        headers=auth_headers,
        json={"title": "Ghost"},
    )
    assert resp.status_code == 404


# Delete book

async def test_delete_book(client: AsyncClient, auth_headers: dict):
    with _mock_storage(), _mock_background():
        create_resp = await client.post(
            "/api/v1/books",
            headers=auth_headers,
            files={"file": _txt_file()},
            data={"title": "To Delete", "author": "Author"},
        )
    book_id = create_resp.json()["id"]

    with _mock_storage():
        resp = await client.delete(
            f"/api/v1/books/{book_id}", headers=auth_headers
        )
    assert resp.status_code == 204


async def test_delete_book_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.delete("/api/v1/books/99999", headers=auth_headers)
    assert resp.status_code == 404
