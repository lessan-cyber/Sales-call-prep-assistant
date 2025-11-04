"""Firecrawl client wrapper for web scraping."""

from typing import Optional, Dict, Any
from firecrawl import Firecrawl
from ..config import settings
from ..utils.logger import info, error, warning


class FirecrawlService:
    """Service for interacting with Firecrawl API for deep website scraping."""

    def __init__(self):
        """Initialize the Firecrawl client."""
        self.client = Firecrawl(api_key=settings.FIRECRAWL_API_KEY)

    def _parse_response(self, response) -> tuple[bool, Any, Optional[str]]:
        """
        Parse Firecrawl response handling both legacy and new API structures.

        Args:
            response: The response from Firecrawl client

        Returns:
            Tuple of (success: bool, data: Any, error_msg: Optional[str])
        """
        if hasattr(response, 'success'):
            success = response.success
            error_msg = getattr(response, 'error', None)
            data = response.data if hasattr(response, 'data') else response
        else:
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

        return success, data, error_msg

    def _categorize_error(self, url: str, exception: Exception, result_key: str = "content") -> Dict[str, Any]:
        """
        Categorize exceptions and return structured error response.

        Args:
            url: The URL that failed to scrape
            exception: The exception that occurred
            result_key: Key for the result field (content/data)

        Returns:
            Dictionary with structured error information
        """
        error_msg = str(exception).lower()

        if "quota" in error_msg or "billing" in error_msg:
            error_text = f"API quota exceeded: {exception!s}. Please check your Firecrawl billing."
        elif "429" in error_msg or "rate limit" in error_msg:
            error_text = f"API rate limit exceeded: {exception!s}. Please try again later."
        elif any(code in error_msg for code in ["500", "502", "503", "504"]):
            error_text = f"Firecrawl server error: {exception!s}. Please try again later."
        else:
            error_text = f"Scraping failed: {exception!s}"

        return {
            "success": False,
            "url": url,
            "error": error_text,
            result_key: None,
        }

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

            # Parse response using shared helper
            success, data, error_msg = self._parse_response(response)

            if success:
                info(f"Successfully scraped: {url}")

                # Safely extract content with fallback priority:
                # 1. content attribute
                # 2. dict['text'] or dict['body']
                # 3. text attribute
                # 4. empty string (with warning)
                if hasattr(data, 'content'):
                    content = data.content
                elif isinstance(data, dict):
                    content = data.get('text') or data.get('body')
                else:
                    content = getattr(data, 'text', '')

                if not content:
                    warning(f"No content field found in response from {url}")
                    content = ''

                return {
                    "success": True,
                    "url": url,
                    "content": content,
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
            error(f"Error scraping {url}: {e}")
            return self._categorize_error(url, e)

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

            # Parse response using shared helper
            success, data, error_msg = self._parse_response(response)

            if success:
                info(f"Successfully extracted structured data from: {url}")

                # Safely extract data with fallback priority:
                # 1. extracted attribute
                # 2. dict['extracted']
                # 3. getattr extracted attribute
                # 4. empty string (with warning)
                if hasattr(data, 'extracted'):
                    extracted_data = data.extracted
                elif isinstance(data, dict):
                    extracted_data = data.get('extracted')
                else:
                    extracted_data = getattr(data, 'extracted', '')

                if not extracted_data:
                    warning(f"No extracted data field found in response from {url}")
                    extracted_data = ''

                return {
                    "success": True,
                    "url": url,
                    "data": extracted_data,
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
            error(f"Error extracting from {url}: {e}")
            return self._categorize_error(url, e, result_key="data")


# Global instance
firecrawl_service = FirecrawlService()
