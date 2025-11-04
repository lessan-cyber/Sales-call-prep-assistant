"""Tests for search service."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.src.services.search_service import SearchService


class TestSearchService:
    """Test SearchService functionality."""

    @pytest.fixture
    def search_service(self):
        """Create SearchService instance."""
        return SearchService()

    @pytest.mark.asyncio
    async def test_search_success(self, search_service):
        """Test successful web search."""
        mock_results = {
            "organic_results": [
                {
                    "title": "Acme Corp - Official Website",
                    "link": "https://acme.com",
                    "snippet": "Leading provider of enterprise solutions",
                    "position": 1
                },
                {
                    "title": "Acme Corp News",
                    "link": "https://news.com/acme",
                    "snippet": "Recent acquisition announcement",
                    "position": 2
                }
            ],
            "news_results": [
                {
                    "title": "Acme Corp Announces New Product",
                    "link": "https://news.com/acme-product",
                    "snippet": "Revolutionary AI solution",
                    "date": "2 days ago",
                    "source": "Tech News"
                }
            ],
            "search_information": {
                "total_results": 1500
            }
        }

        with patch("backend.src.services.search_service.search") as mock_search:
            mock_search.return_value.get_dict.return_value = mock_results

            result = await search_service.search("Acme Corp", num_results=10)

            assert result["success"] is True
            assert result["query"] == "Acme Corp"
            assert len(result["organic_results"]) == 2
            assert len(result["news_results"]) == 1
            assert result["organic_results"][0]["title"] == "Acme Corp - Official Website"
            assert result["news_results"][0]["source"] == "Tech News"

    @pytest.mark.asyncio
    async def test_search_no_news_results(self, search_service):
        """Test search with no news results."""
        mock_results = {
            "organic_results": [
                {
                    "title": "Test",
                    "link": "https://test.com",
                    "snippet": "Test snippet",
                    "position": 1
                }
            ],
            "search_information": {
                "total_results": 100
            }
        }

        with patch("backend.src.services.search_service.search") as mock_search:
            mock_search.return_value.get_dict.return_value = mock_results

            result = await search_service.search("Test Query")

            assert result["success"] is True
            assert len(result["news_results"]) == 0
            assert len(result["organic_results"]) == 1

    @pytest.mark.asyncio
    async def test_search_error_handling(self, search_service):
        """Test error handling during search."""
        with patch("backend.src.services.search_service.search") as mock_search:
            mock_search.side_effect = Exception("API error")

            result = await search_service.search("Error Query")

            assert result["success"] is False
            assert "error" in result
            assert "API error" in result["error"]

    @pytest.mark.asyncio
    async def test_search_empty_results(self, search_service):
        """Test search with no results."""
        mock_results = {
            "search_information": {
                "total_results": 0
            }
        }

        with patch("backend.src.services.search_service.search") as mock_search:
            mock_search.return_value.get_dict.return_value = mock_results

            result = await search_service.search("Nonexistent Company XYZ123")

            assert result["success"] is True
            assert len(result["organic_results"]) == 0
            assert len(result["news_results"]) == 0

    @pytest.mark.asyncio
    async def test_search_respects_num_results(self, search_service):
        """Test that num_results parameter is respected."""
        mock_results = {
            "organic_results": [
                {"title": f"Result {i}", "link": f"https://test{i}.com", 
                 "snippet": f"Snippet {i}", "position": i}
                for i in range(1, 21)
            ],
            "search_information": {"total_results": 1000}
        }

        with patch("backend.src.services.search_service.search") as mock_search:
            mock_search.return_value.get_dict.return_value = mock_results

            result = await search_service.search("Test", num_results=5)

            # Should only return first 5 results
            assert len(result["organic_results"]) <= 5