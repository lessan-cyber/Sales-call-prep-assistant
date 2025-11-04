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

            # Check if response has success attribute or check the response structure
            if hasattr(response, 'success'):
                success = response.success
                error_msg = getattr(response, 'error', None)
                data = response.data if hasattr(response, 'data') else response
            else:
                # New API structure - validate response before assuming success
                success = False
                error_msg = None
                data = None

                # Validate response structure - check for expected keys
                if hasattr(response, 'data'):
                    data = response.data
                    success = True
                elif hasattr(response, 'content'):
                    # Response has content but no explicit success flag
                    # Check if it looks like a valid response
                    data = response
                    success = True
                elif isinstance(response, dict):
                    # Check for common response patterns
                    if 'data' in response:
                        data = response['data']
                        success = True
                        error_msg = response.get('error')
                    elif 'content' in response:
                        data = response
                        success = True
                        error_msg = response.get('error')
                    elif 'error' in response:
                        # Explicit error in response
                        success = False
                        error_msg = response.get('error', 'Unknown error')
                        data = None
                    else:
                        # Unknown dict structure
                        error(f"Unexpected response structure from Firecrawl: {response}")
                        error_msg = f"Unexpected response format: {response}"
                else:
                    # Unexpected type
                    error(f"Unexpected response type from Firecrawl: {type(response).__name__}")
                    error_msg = f"Unexpected response type: {type(response).__name__}"

            if success:
                info(f"Successfully scraped: {url}")
                return {
                    "success": True,
                    "url": url,
                    "content": data.content if hasattr(data, 'content') else str(data),
                    "markdown": data.markdown
                    if hasattr(data, "markdown")
                    else None,
                    "metadata": data.metadata if hasattr(data, 'metadata') else {},
                    "source": "firecrawl",
                }
            else:
                error(f"Failed to scrape {url}: {error_msg}")
                return {
                    "success": False,
                    "url": url,
                    "error": error_msg,
                    "content": None,
                }

        except Exception as e:
            error_msg = str(e).lower()
            error(f"Error scraping {url}: {e}")

            # Check for specific error types
            if "quota" in error_msg or "billing" in error_msg:
                return {
                    "success": False,
                    "url": url,
                    "error": f"API quota exceeded: {str(e)}. Please check your Firecrawl billing.",
                    "content": None,
                }
            elif "429" in error_msg or "rate limit" in error_msg:
                return {
                    "success": False,
                    "url": url,
                    "error": f"API rate limit exceeded: {str(e)}. Please try again later.",
                    "content": None,
                }
            elif any(code in error_msg for code in ["500", "502", "503", "504"]):
                return {
                    "success": False,
                    "url": url,
                    "error": f"Firecrawl server error: {str(e)}. Please try again later.",
                    "content": None,
                }
            else:
                return {
                    "success": False,
                    "url": url,
                    "error": f"Scraping failed: {str(e)}",
                    "content": None,
                }

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

            # Check if response has success attribute or check the response structure
            if hasattr(response, 'success'):
                success = response.success
                error_msg = getattr(response, 'error', None)
                data = response.data if hasattr(response, 'data') else response
            else:
                # New API structure - validate response before assuming success
                success = False
                error_msg = None
                data = None

                # Validate response structure - check for expected keys
                if hasattr(response, 'data'):
                    data = response.data
                    success = True
                elif hasattr(response, 'content'):
                    # Response has content but no explicit success flag
                    # Check if it looks like a valid response
                    data = response
                    success = True
                elif isinstance(response, dict):
                    # Check for common response patterns
                    if 'data' in response:
                        data = response['data']
                        success = True
                        error_msg = response.get('error')
                    elif 'content' in response:
                        data = response
                        success = True
                        error_msg = response.get('error')
                    elif 'error' in response:
                        # Explicit error in response
                        success = False
                        error_msg = response.get('error', 'Unknown error')
                        data = None
                    else:
                        # Unknown dict structure
                        error(f"Unexpected response structure from Firecrawl: {response}")
                        error_msg = f"Unexpected response format: {response}"
                else:
                    # Unexpected type
                    error(f"Unexpected response type from Firecrawl: {type(response).__name__}")
                    error_msg = f"Unexpected response type: {type(response).__name__}"

            if success:
                info(f"Successfully extracted structured data from: {url}")
                return {
                    "success": True,
                    "url": url,
                    "data": data.extracted if hasattr(data, 'extracted') else str(data),
                    "source": "firecrawl_extract",
                }
            else:
                error(f"Failed to extract from {url}: {error_msg}")
                return {
                    "success": False,
                    "url": url,
                    "error": error_msg,
                    "data": None,
                }

        except Exception as e:
            error_msg = str(e).lower()
            error(f"Error extracting from {url}: {e}")

            # Check for specific error types
            if "quota" in error_msg or "billing" in error_msg:
                return {
                    "success": False,
                    "url": url,
                    "error": f"API quota exceeded: {str(e)}. Please check your Firecrawl billing.",
                    "data": None,
                }
            elif "429" in error_msg or "rate limit" in error_msg:
                return {
                    "success": False,
                    "url": url,
                    "error": f"API rate limit exceeded: {str(e)}. Please try again later.",
                    "data": None,
                }
            elif any(code in error_msg for code in ["500", "502", "503", "504"]):
                return {
                    "success": False,
                    "url": url,
                    "error": f"Firecrawl server error: {str(e)}. Please try again later.",
                    "data": None,
                }
            else:
                return {
                    "success": False,
                    "url": url,
                    "error": f"Extraction failed: {str(e)}",
                    "data": None,
                }


# Global instance
firecrawl_service = FirecrawlService()
