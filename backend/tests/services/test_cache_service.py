"""Tests for cache service."""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock, patch
from backend.src.services.cache_service import CacheService


class TestCacheService:
    """Test CacheService functionality."""

    @pytest.fixture
    def cache_service(self, mock_supabase_client):
        """Create CacheService instance with mocked Supabase."""
        return CacheService(mock_supabase_client)

    @pytest.mark.asyncio
    async def test_get_cached_company_data_fresh(self, cache_service, mock_supabase_client):
        """Test retrieving fresh cached data."""
        # Mock response with fresh data (2 days old)
        now = datetime.now(timezone.utc)
        mock_data = {
            "company_name_normalized": "acme-corp",
            "company_data": {"name": "Acme Corp", "industry": "Tech"},
            "confidence_score": 0.9,
            "source_urls": ["https://acme.com"],
            "last_updated": (now - timedelta(days=2)).isoformat()
        }
        mock_supabase_client.execute.return_value = Mock(data=[mock_data])

        result = await cache_service.get_cached_company_data("acme-corp")

        assert result is not None
        assert result["cache_status"] == "fresh"
        assert result["company_data"]["name"] == "Acme Corp"
        assert result["confidence_score"] == 0.9
        mock_supabase_client.table.assert_called_once_with("company_cache")

    @pytest.mark.asyncio
    async def test_get_cached_company_data_stale(self, cache_service, mock_supabase_client):
        """Test retrieving stale cached data (>7 days old)."""
        now = datetime.now(timezone.utc)
        mock_data = {
            "company_name_normalized": "old-corp",
            "company_data": {"name": "Old Corp"},
            "confidence_score": 0.8,
            "source_urls": [],
            "last_updated": (now - timedelta(days=10)).isoformat()
        }
        mock_supabase_client.execute.return_value = Mock(data=[mock_data])

        result = await cache_service.get_cached_company_data("old-corp")

        assert result is not None
        assert result["cache_status"] == "stale"
        assert result["company_data"]["name"] == "Old Corp"

    @pytest.mark.asyncio
    async def test_get_cached_company_data_not_found(self, cache_service, mock_supabase_client):
        """Test when no cached data exists."""
        mock_supabase_client.execute.return_value = Mock(data=[])

        result = await cache_service.get_cached_company_data("nonexistent-corp")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_cached_company_data_error(self, cache_service, mock_supabase_client):
        """Test error handling during cache retrieval."""
        mock_supabase_client.execute.side_effect = Exception("Database error")

        result = await cache_service.get_cached_company_data("error-corp")

        assert result is None

    @pytest.mark.asyncio
    async def test_cache_company_data_success(self, cache_service, mock_supabase_client):
        """Test successfully caching company data."""
        company_data = {"name": "Test Corp", "industry": "Tech"}
        mock_supabase_client.execute.return_value = Mock(data=[{"id": "123"}])

        result = await cache_service.cache_company_data(
            normalized_company_name="test-corp",
            company_data=company_data,
            confidence_score=0.85,
            source_urls=["https://test.com"]
        )

        assert result is True
        mock_supabase_client.table.assert_called_with("company_cache")
        mock_supabase_client.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_company_data_error(self, cache_service, mock_supabase_client):
        """Test error handling during cache storage."""
        mock_supabase_client.execute.side_effect = Exception("Insert failed")

        result = await cache_service.cache_company_data(
            normalized_company_name="fail-corp",
            company_data={},
            confidence_score=0.5,
            source_urls=[]
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_cache_ttl_boundary(self, cache_service, mock_supabase_client):
        """Test cache TTL at exactly 7 days."""
        now = datetime.now(timezone.utc)
        # Exactly 7 days old
        mock_data = {
            "company_name_normalized": "boundary-corp",
            "company_data": {"name": "Boundary Corp"},
            "confidence_score": 0.7,
            "source_urls": [],
            "last_updated": (now - timedelta(days=7)).isoformat()
        }
        mock_supabase_client.execute.return_value = Mock(data=[mock_data])

        result = await cache_service.get_cached_company_data("boundary-corp")

        # At exactly 7 days, should be considered stale
        assert result is not None
        assert result["cache_status"] == "stale"