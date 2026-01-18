"""
Authentication API tests.
Tests for /api/v1/auth/* endpoints.

TDD Status: RED (tests written, implementation pending for some)
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestRegister:
    """Tests for POST /api/v1/auth/register"""

    async def test_register_success(self, client: AsyncClient):
        """Should create a new user and return user info."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        assert "hashed_password" not in data

    async def test_register_duplicate_email(self, client: AsyncClient):
        """Should return 400 when email already exists."""
        # First registration
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user1",
                "password": "password123",
            },
        )
        # Duplicate email
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user2",
                "password": "password123",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    async def test_register_duplicate_username(self, client: AsyncClient):
        """Should return 400 when username already exists."""
        # First registration
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user1@example.com",
                "username": "sameusername",
                "password": "password123",
            },
        )
        # Duplicate username
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user2@example.com",
                "username": "sameusername",
                "password": "password123",
            },
        )
        assert response.status_code == 400
        assert "already taken" in response.json()["detail"].lower()

    async def test_register_invalid_email(self, client: AsyncClient):
        """Should return 422 for invalid email format."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "username": "validuser",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    async def test_register_short_password(self, client: AsyncClient):
        """Should return 422 for password shorter than 8 characters."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "username": "validuser",
                "password": "short",
            },
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/v1/auth/login"""

    async def test_login_success(self, client: AsyncClient):
        """Should return user info and tokens on successful login."""
        # Create user first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "password123",
            },
        )

        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "tokens" in data
        assert data["user"]["email"] == "login@example.com"
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]

    async def test_login_wrong_password(self, client: AsyncClient):
        """Should return 401 for incorrect password."""
        # Create user first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrongpass@example.com",
                "username": "wrongpassuser",
                "password": "password123",
            },
        )

        # Login with wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Should return 401 for non-existent user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 401


class TestRefreshToken:
    """Tests for POST /api/v1/auth/refresh"""

    async def test_refresh_success(self, client: AsyncClient):
        """Should return new tokens with valid refresh token."""
        # Create and login user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh@example.com",
                "username": "refreshuser",
                "password": "password123",
            },
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "refresh@example.com",
                "password": "password123",
            },
        )
        refresh_token = login_response.json()["tokens"]["refresh_token"]

        # Refresh
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Should return 401 for invalid refresh token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        assert response.status_code == 401


class TestGetCurrentUser:
    """Tests for GET /api/v1/auth/me"""

    async def test_get_me_success(self, client: AsyncClient):
        """Should return current user info with valid token."""
        # Create and login user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "me@example.com",
                "username": "meuser",
                "password": "password123",
            },
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "me@example.com",
                "password": "password123",
            },
        )
        access_token = login_response.json()["tokens"]["access_token"]

        # Get current user
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        assert data["username"] == "meuser"

    async def test_get_me_no_token(self, client: AsyncClient):
        """Should return 401 without token."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Should return 401 with invalid token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401
