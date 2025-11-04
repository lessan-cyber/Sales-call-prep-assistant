"""Website scraping tool for Agent A - Research Orchestrator."""
from typing import Dict, Any
from pydantic_ai import Tool
from ....services.firecrawl_service import firecrawl_service
from ....utils.logger import info


async def scrape_website(url: str) -> Dict[str, Any]:
    """
    Scrape website content using Firecrawl.

    Args:
        url: Website URL to scrape

    Returns:
        Dictionary with scraped content
    """
    info(f"Tool called: scrape_website for URL: {url}")

    result = await firecrawl_service.scrape_website(url)

    if result["success"]:
        return {
            "success": True,
            "url": result["url"],
            "content": result.get("content", ""),
            "markdown": result.get("markdown", ""),
            "metadata": result.get("metadata", {}),
            "error": None
        }
    else:
        return {
            "success": False,
            "url": result.get("url", url),
            "content": None,
            "error": result.get("error", "Unknown error")
        }


scrape_website_tool = Tool(
    scrape_website,
    description="Scrape website content to get detailed company information. Use this after finding a company's website URL via web_search. Returns full page content in markdown and HTML formats. Parameter: url (str) - full URL to scrape."
)
