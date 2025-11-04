"""Web search tool for Agent A - Research Orchestrator."""
from typing import List, Dict, Any
from pydantic_ai import Tool
from ....services.search_service import search_service
from ....utils.logger import info


async def web_search(query: str, num_results: int = 10) -> Dict[str, Any]:
    """
    Perform a web search using SerpAPI.

    Args:
        query: Search query
        num_results: Number of results to return

    Returns:
        Dictionary with search results
    """
    info(f"Tool called: web_search for query: {query}")

    result = await search_service.search(query, num_results=num_results)

    return {
        "success": result["success"],
        "query": query,
        "organic_results": result.get("organic_results", []),
        "news_results": result.get("news_results", []),
        "total_results": result.get("total_results", 0),
        "error": result.get("error")
    }


web_search_tool = Tool(
    web_search,
    description="Search the web for information about a company, news, or decision makers. Use this when you need general web information, company overviews, recent news, or to find LinkedIn profiles. Parameters: query (str) - search query, num_results (int) - number of results (default 10)."
)
