import os
import httpx
from fastapi import HTTPException, status

from ..utils.logger import info, error
from ..config import settings

async def perform_serpapi_search(query: str) -> dict:
    """Performs a web search using SerpAPI."""
    if not settings.SERP_API_KEY:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SERP_API_KEY not set in settings.")

    search_url = "https://serpapi.com/search"
    params = {
        "api_key": settings.SERP_API_KEY,
        "q": query,
        "engine": "google", # Can be changed to other engines if needed
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, params=params)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            search_results = response.json()
            info(f"SerpAPI search for '{query}' successful.")
            return search_results
    except httpx.RequestError as e:
        error(f"SerpAPI request error for '{query}': {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"SerpAPI request failed: {e}")
    except httpx.HTTPStatusError as e:
        error(f"SerpAPI HTTP error for '{query}': {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"SerpAPI HTTP error: {e.response.text}")
    except Exception as e:
        error(f"An unexpected error occurred during SerpAPI search for '{query}': {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")
