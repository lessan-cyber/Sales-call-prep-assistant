import httpx
from fastapi import HTTPException, status

from ..config import settings
from ..utils.logger import error, info


async def perform_serpapi_search(query: str) -> dict:
    """Performs a web search using SerpAPI."""
    if not settings.SERP_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SERP_API_KEY not set in settings.",
        )

    search_url = "https://serpapi.com/search"
    params = {
        "api_key": settings.SERP_API_KEY,
        "q": query,
        "engine": "google",  # Can be changed to other engines if needed
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SerpAPI request failed: {e}",
        ) from e
    except httpx.HTTPStatusError as e:
        serpapi_status = e.response.status_code
        serpapi_text = e.response.text

        error(
            f"SerpAPI HTTP error for '{query}': {serpapi_status} - {serpapi_text}"
        )

        if serpapi_status >= 500:
            upstream_status = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            upstream_status = status.HTTP_502_BAD_GATEWAY

        raise HTTPException(
            status_code=upstream_status,
            detail="Search service temporarily unavailable. Please try again later.",
        ) from e
    except Exception as e:
        error(f"An unexpected error occurred during SerpAPI search for '{query}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        ) from e
