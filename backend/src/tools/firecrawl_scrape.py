import json
import os
import httpx
from fastapi import HTTPException, status
from ..utils.logger import info, error
from ..config import settings


async def perform_firecrawl_scrape(url: str) -> dict:
    """Performs web scraping using Firecrawl API.

    Args:
        url: The URL to scrape using Firecrawl API.

    Returns:
        dict: Response from Firecrawl API containing:
            - success (bool): Indicates if the scrape was successful
            - content (str): Raw HTML or text content from the page
            - metadata (dict): Additional metadata like headers, timings, etc.
            - status_code (int): HTTP status code from the scrape
            - error (str, optional): Error message if scraping failed

    Raises:
        HTTPException: If FIRECRAWL_API_KEY is not configured or if the
            scraping request fails due to network issues, HTTP errors, or
            other unexpected problems.
    """
    if not settings.FIRECRAWL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FIRECRAWL_API_KEY not set in settings.",
        )

    firecrawl_url = "https://api.firecrawl.dev/v0/scrape"
    headers = {
        "Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "url": url,
        "pageOptions": {
            "onlyMainContent": True,
        },
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(firecrawl_url, headers=headers, json=data)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            scraped_data = response.json()
            info(f"Firecrawl scrape for '{url}' successful.")
            return scraped_data
    except httpx.RequestError as e:
        error(f"Firecrawl request error for '{url}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Firecrawl request failed: {e}",
        ) from e
    except httpx.HTTPStatusError as e:
        firecrawl_status = e.response.status_code
        firecrawl_text = e.response.text

        # Log the detailed Firecrawl error
        error(
            f"Firecrawl HTTP error for '{url}': {firecrawl_status} - {firecrawl_text}"
        )

        # Map Firecrawl status codes to appropriate upstream HTTP status codes
        if firecrawl_status == 401 or firecrawl_status == 403:
            # Authentication/authorization failure from Firecrawl
            upstream_status = status.HTTP_502_BAD_GATEWAY
        elif firecrawl_status == 429:
            # Rate limiting from Firecrawl
            upstream_status = status.HTTP_503_SERVICE_UNAVAILABLE
        elif firecrawl_status >= 500:
            # Firecrawl server errors
            upstream_status = status.HTTP_502_BAD_GATEWAY
        else:
            # Other client errors (4xx)
            upstream_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        raise HTTPException(
            status_code=upstream_status,
            detail=f"Firecrawl HTTP error ({firecrawl_status}): {firecrawl_text}",
        ) from e
    except (json.JSONDecodeError, KeyError, AttributeError, TypeError, ValueError) as e:
        # Handle specific parsing/data processing errors
        error(f"Data parsing error during Firecrawl scrape for '{url}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse Firecrawl response: {e}",
        ) from e
    except Exception as e:
        # Broad catch for any other unexpected errors (e.g., logic errors, unexpected
        # API responses, etc.). We need this to ensure we don't leak internal errors
        # to clients and to provide meaningful error responses.
        error(f"An unexpected error occurred during Firecrawl scrape for '{url}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        ) from e
