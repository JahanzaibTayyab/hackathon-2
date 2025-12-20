"""Unit tests for security functions."""

from datetime import UTC, datetime, timedelta

import pytest

from src.core.security import extract_user_id_from_token_async


class TestExtractUserIdFromToken:
    """Test extract_user_id_from_token_async."""

    @pytest.mark.asyncio
    async def test_extract_user_id_from_sub(self, monkeypatch):
        """Test extracting user_id from 'sub' field."""
        # Mock verify_jwt_token_async to return payload with 'sub'
        async def mock_verify(token: str):
            return {"sub": "user-123", "exp": int((datetime.now(UTC) + timedelta(days=1)).timestamp())}

        monkeypatch.setattr("src.core.security.verify_jwt_token_async", mock_verify)

        user_id = await extract_user_id_from_token_async("fake-token")
        assert user_id == "user-123"

    @pytest.mark.asyncio
    async def test_extract_user_id_from_user_id_field(self, monkeypatch):
        """Test extracting user_id from 'user_id' field (fallback)."""
        async def mock_verify(token: str):
            return {"user_id": "user-456", "exp": int((datetime.now(UTC) + timedelta(days=1)).timestamp())}

        monkeypatch.setattr("src.core.security.verify_jwt_token_async", mock_verify)

        user_id = await extract_user_id_from_token_async("fake-token")
        assert user_id == "user-456"

    @pytest.mark.asyncio
    async def test_extract_user_id_from_id_field(self, monkeypatch):
        """Test extracting user_id from 'id' field (fallback)."""
        async def mock_verify(token: str):
            return {"id": "user-789", "exp": int((datetime.now(UTC) + timedelta(days=1)).timestamp())}

        monkeypatch.setattr("src.core.security.verify_jwt_token_async", mock_verify)

        user_id = await extract_user_id_from_token_async("fake-token")
        assert user_id == "user-789"

    @pytest.mark.asyncio
    async def test_extract_user_id_invalid_token(self, monkeypatch):
        """Test with invalid token (verify returns None)."""
        async def mock_verify(token: str):
            return None

        monkeypatch.setattr("src.core.security.verify_jwt_token_async", mock_verify)

        user_id = await extract_user_id_from_token_async("invalid-token")
        assert user_id is None

    @pytest.mark.asyncio
    async def test_extract_user_id_no_user_id_in_payload(self, monkeypatch):
        """Test when payload has no user_id fields."""
        async def mock_verify(token: str):
            return {"exp": int((datetime.now(UTC) + timedelta(days=1)).timestamp())}

        monkeypatch.setattr("src.core.security.verify_jwt_token_async", mock_verify)

        user_id = await extract_user_id_from_token_async("fake-token")
        assert user_id is None
