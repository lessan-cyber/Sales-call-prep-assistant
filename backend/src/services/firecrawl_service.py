"""Firecrawl client wrapper for web scraping."""

from typing import Optional, Dict, Any
from firecrawl import Firecrawl
from ..config import settings
from ..utils.logger import info, error


class FirecrawlService:
    """Service for interacting with Firecrawl API for deep website scraping."""

    def __init__(self):
        """Initialize the Firecrawl client."""
        self.client = Firecrawl(api_key=settings.FIRECRAWL_API_KEY)

    async def scrape_website(
        self, url: str, formats: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Scrape a website URL using Firecrawl.

        Args:
            url: The URL to scrape
            formats: List of formats to extract (e.g., ['markdown', 'html'])

        Returns:
            Dictionary containing scraped content
        """
        try:
            info(f"Scraping website: {url}")

            if formats is None:
                formats = ["markdown", "html"]

            # Use the scrape method
            response = self.client.scrape(url, formats=formats)

            if response.success:
                info(f"Successfully scraped: {url}")
                return {
                    "success": True,
                    "url": url,
                    "content": response.data.content,
                    "markdown": response.data.markdown
                    if hasattr(response.data, "markdown")
                    else None,
                    "metadata": response.data.metadata,
                    "source": "firecrawl",
                }
            else:
                error(f"Failed to scrape {url}: {response.error}")
                return {
                    "success": False,
                    "url": url,
                    "error": response.error,
                    "content": None,
                }

        except Exception as e:
            error(f"Error scraping {url}: {e}")
            return {"success": False, "url": url, "error": str(e), "content": None}

    async def extract_with_schema(
        self, url: str, schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract structured data from a website using a schema.

        Args:
            url: The URL to scrape
            schema: JSON schema for extraction

        Returns:
            Dictionary containing extracted data
        """
        try:
            info(f"Extracting structured data from: {url}")

            response = self.client.scrape(url, extract={"schema": schema})

            if response.success:
                info(f"Successfully extracted structured data from: {url}")
                return {
                    "success": True,
                    "url": url,
                    "data": response.data.extracted,
                    "source": "firecrawl_extract",
                }
            else:
                error(f"Failed to extract from {url}: {response.error}")
                return {
                    "success": False,
                    "url": url,
                    "error": response.error,
                    "data": None,
                }

        except Exception as e:
            error(f"Error extracting from {url}: {e}")
            return {"success": False, "url": url, "error": str(e), "data": None}


# Global instance
firecrawl_service = FirecrawlService()
