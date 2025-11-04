"""Tests for Firecrawl service."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.src.services.firecrawl_service import FirecrawlService


class TestFirecrawlService:
    """Test FirecrawlService functionality."""

    @pytest.fixture
    def firecrawl_service(self):
        """Create FirecrawlService instance with mocked client."""
        with patch("backend.src.services.firecrawl_service.Firecrawl"):
            service = FirecrawlService()
            return service

    @pytest.mark.asyncio
    async def test_scrape_website_success(self, firecrawl_service):
        """Test successful website scraping."""
        mock_response = Mock()
        mock_response.success = True
        mock_response.data = Mock()
        mock_response.data.content = "Website content here"
        mock_response.data.markdown = "# Website Title\n\nContent"
        mock_response.data.metadata = {
            "title": "Test Website",
            "description": "Test description"
        }

        firecrawl_service.client.scrape = Mock(return_value=mock_response)

        result = await firecrawl_service.scrape_website("https://example.com")

        assert result["success"] is True
        assert result["url"] == "https://example.com"
        assert result["content"] == "Website content here"
        assert result["markdown"] == "# Website Title\n\nContent"
        assert result["metadata"]["title"] == "Test Website"
        assert result["source"] == "firecrawl"

    @pytest.mark.asyncio
    async def test_scrape_website_failure(self, firecrawl_service):
        """Test failed website scraping."""
        mock_response = Mock()
        mock_response.success = False
        mock_response.error = "404 Not Found"

        firecrawl_service.client.scrape = Mock(return_value=mock_response)

        result = await firecrawl_service.scrape_website("https://notfound.com")

        assert result["success"] is False
        assert result["url"] == "https://notfound.com"
        assert result["error"] == "404 Not Found"
        assert result["content"] is None

    @pytest.mark.asyncio
    async def test_scrape_website_exception(self, firecrawl_service):
        """Test exception handling during scraping."""
        firecrawl_service.client.scrape = Mock(side_effect=Exception("Connection timeout"))

        result = await firecrawl_service.scrape_website("https://timeout.com")

        assert result["success"] is False
        assert result["url"] == "https://timeout.com"
        assert "Connection timeout" in result["error"]
        assert result["content"] is None

    @pytest.mark.asyncio
    async def test_scrape_website_custom_formats(self, firecrawl_service):
        """Test scraping with custom format list."""
        mock_response = Mock()
        mock_response.success = True
        mock_response.data = Mock()
        mock_response.data.content = "Content"
        mock_response.data.metadata = {}

        firecrawl_service.client.scrape = Mock(return_value=mock_response)

        result = await firecrawl_service.scrape_website(
            "https://example.com",
            formats=["html"]
        )

        assert result["success"] is True
        firecrawl_service.client.scrape.assert_called_once()
        call_args = firecrawl_service.client.scrape.call_args
        assert call_args[1]["formats"] == ["html"]

    @pytest.mark.asyncio
    async def test_extract_with_schema_success(self, firecrawl_service):
        """Test structured data extraction with schema."""
        mock_response = Mock()
        mock_response.success = True
        mock_response.data = {
            "company_name": "Acme Corp",
            "industry": "Technology",
            "employees": "500-1000"
        }

        firecrawl_service.client.scrape = Mock(return_value=mock_response)

        schema = {
            "type": "object",
            "properties": {
                "company_name": {"type": "string"},
                "industry": {"type": "string"},
                "employees": {"type": "string"}
            }
        }

        result = await firecrawl_service.extract_with_schema(
            "https://acme.com",
            schema
        )

        assert result["success"] is True
        assert result["data"]["company_name"] == "Acme Corp"
        firecrawl_service.client.scrape.assert_called_once()