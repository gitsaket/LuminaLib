"""Integration tests for /api/v1/auth endpoints (SQLite in-memory)."""
from httpx import AsyncClient


SIGNUP_PAYLOAD = {
    "email": "saket@duck.com",
    "username": "saket",
    "password": "password123",
    "full_name": "Saket Bisht",
}


#Signup

async def test_signup_success(client: AsyncClient):
    resp = await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == SIGNUP_PAYLOAD["email"]
    assert data["username"] == SIGNUP_PAYLOAD["username"]
    assert "hashed_password" not in data


async def test_signup_duplicate_email(client: AsyncClient):
    await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    resp = await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    assert resp.status_code == 409
    assert "Email" in resp.json()["detail"]


async def test_signup_duplicate_username(client: AsyncClient):
    await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    # Same username, different email
    payload = {**SIGNUP_PAYLOAD, "email": "other@example.com"}
    resp = await client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 409
    assert "Username" in resp.json()["detail"]


async def test_signup_invalid_data(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "not-an-email", "username": "x", "password": "short"},
    )
    assert resp.status_code == 422


#Login

async def test_login_success(client: AsyncClient):
    await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": SIGNUP_PAYLOAD["email"], "password": SIGNUP_PAYLOAD["password"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": SIGNUP_PAYLOAD["email"], "password": "wrongpassword"},
    )
    assert resp.status_code == 401


async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "password123"},
    )
    assert resp.status_code == 401


#Profile

async def test_get_me_authenticated(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


async def test_get_me_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_update_profile(client: AsyncClient, auth_headers: dict):
    resp = await client.put(
        "/api/v1/auth/me",
        json={"full_name": "Updated Name", "bio": "My bio"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Updated Name"
    assert data["bio"] == "My bio"


async def test_update_password(client: AsyncClient, auth_headers: dict):
    resp = await client.put(
        "/api/v1/auth/me",
        json={"password": "newpassword123"},
        headers=auth_headers,
    )
    assert resp.status_code == 200


#Signout

async def test_signout(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/auth/signout", headers=auth_headers)
    assert resp.status_code == 204
