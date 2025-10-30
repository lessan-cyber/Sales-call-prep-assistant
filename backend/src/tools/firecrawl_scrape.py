import os
import httpx
from fastapi import HTTPException, status

from ..utils.logger import info, error
from ..config import settings

async def perform_firecrawl_scrape(url: str) -> dict:
    """Performs web scraping using Firecrawl API."""
    if not settings.FIRECRAWL_API_KEY:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="FIRECRAWL_API_KEY not set in settings.")

    firecrawl_url = "https://api.firecrawl.dev/v0/scrape"
    headers = {
        "Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "url": url,
        "pageOptions": {
            "onlyMainContent": True
        }
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Firecrawl request failed: {e}")
    except httpx.HTTPStatusError as e:
        error(f"Firecrawl HTTP error for '{url}': {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Firecrawl HTTP error: {e.response.text}")
    except Exception as e:
        error(f"An unexpected error occurred during Firecrawl scrape for '{url}': {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")
