"""Search service wrapper for SerpAPI web search."""

from typing import Optional, Dict, Any, List

# from serpapi import GoogleSearch
from ..config import settings
from ..utils.logger import info, error
from serpapi import search


class SearchService:
    """Service for performing web searches using SerpAPI."""

    def __init__(self):
        """Initialize the Search service."""
        pass

    async def search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Perform a web search using SerpAPI.

        Args:
            query: Search query string
            num_results: Number of results to return

        Returns:
            Dictionary containing search results
        """
        try:
            info(f"Performing search for query: {query}")

            params = {
                "engine": "google",
                "q": query,
                "api_key": settings.SERP_API_KEY,
                "num": num_results,
                "hl": "en",
                "gl": "us",
            }

            research = search(params)
            results = research

            # Extract organic results
            organic_results = []
            if "organic_results" in results:
                for result in results["organic_results"][:num_results]:
                    organic_results.append(
                        {
                            "title": result.get("title", ""),
                            "link": result.get("link", ""),
                            "snippet": result.get("snippet", ""),
                            "position": result.get("position", 0),
                        }
                    )

            # Extract news results if available
            news_results = []
            if "news_results" in results:
                for result in results["news_results"][:5]:
                    news_results.append(
                        {
                            "title": result.get("title", ""),
                            "link": result.get("link", ""),
                            "snippet": result.get("snippet", ""),
                            "date": result.get("date", ""),
                            "source": result.get("source", ""),
                        }
                    )

            info(
                f"Search completed for query: {query}. Found {len(organic_results)} organic results"
            )

            return {
                "success": True,
                "query": query,
                "organic_results": organic_results,
                "news_results": news_results,
                "total_results": results.get("search_information", {}).get(
                    "total_results", 0
                ),
                "source": "serpapi",
            }

        except Exception as e:
            error_msg = str(e).lower()
            error(f"Error performing search for query '{query}': {e}")

            # Check for specific error types
            if "quota" in error_msg or "billing" in error_msg:
                return {
                    "success": False,
                    "query": query,
                    "error": f"API quota exceeded: {str(e)}. Please check your SerpAPI billing.",
                    "organic_results": [],
                    "news_results": [],
                }
            elif "429" in error_msg or "rate limit" in error_msg:
                return {
                    "success": False,
                    "query": query,
                    "error": f"API rate limit exceeded: {str(e)}. Please try again later.",
                    "organic_results": [],
                    "news_results": [],
                }
            elif any(code in error_msg for code in ["500", "502", "503", "504"]):
                return {
                    "success": False,
                    "query": query,
                    "error": f"SerpAPI server error: {str(e)}. Please try again later.",
                    "organic_results": [],
                    "news_results": [],
                }
            else:
                return {
                    "success": False,
                    "query": query,
                    "error": f"Search failed: {str(e)}",
                    "organic_results": [],
                    "news_results": [],
                }

    async def find_company_website(self, company_name: str) -> Optional[str]:
        """
        Find the official website for a company.

        Args:
            company_name: Name of the company

        Returns:
            Official website URL if found, None otherwise
        """
        try:
            query = f"{company_name} official website"
            result = await self.search(query, num_results=5)

            if result["success"] and result["organic_results"]:
                # First result is typically the official site
                for organic_result in result["organic_results"]:
                    url = organic_result["link"]
                    # Basic heuristic: avoid wikipedia, news sites, etc.
                    if not any(
                        skip in url.lower()
                        for skip in [
                            "wikipedia",
                            "news",
                            "crunchbase",
                            "linkedin.com/company",
                        ]
                    ):
                        info(f"Found official website for {company_name}: {url}")
                        return url

                # If no good match found, return the first result
                info(
                    f"Using first search result as website for {company_name}: {result['organic_results'][0]['link']}"
                )
                return result["organic_results"][0]["link"]

            return None

        except Exception as e:
            error(f"Error finding website for {company_name}: {e}")
            return None

    async def search_decision_makers(
        self, company_name: str, person_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for decision makers at a company.

        Args:
            company_name: Name of the company
            person_name: Optional specific person to search for

        Returns:
            Dictionary containing decision maker information
        """
        try:
            if person_name:
                query = f'"{person_name}" {company_name} LinkedIn'
            else:
                query = f"{company_name} CEO CTO VP marketing decision makers LinkedIn"

            result = await self.search(query, num_results=10)

            return {
                "success": True,
                "company_name": company_name,
                "person_name": person_name,
                "results": result["organic_results"],
                "source": "serpapi_decision_makers",
            }

        except Exception as e:
            error(f"Error searching decision makers for {company_name}: {e}")
            return {
                "success": False,
                "company_name": company_name,
                "person_name": person_name,
                "error": str(e),
                "results": [],
            }


# Global instance
search_service = SearchService()
