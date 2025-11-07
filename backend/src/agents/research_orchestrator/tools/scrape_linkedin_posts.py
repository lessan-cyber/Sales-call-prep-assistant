"""LinkedIn posts scraping tool for Agent A - Research Orchestrator."""

from typing import Any

from pydantic_ai import Tool

from ....services.apify_service import apify_service
from ....utils.logger import info


async def scrape_linkedin_posts(company_name: str, limit: int = 10) -> dict[str, Any]:
    """
    Scrape recent LinkedIn posts from a company or a profile using Apify actor.

    Args:
        company_name: Name of the company
        limit: Maximum number of posts to scrape

    Returns:
        Dictionary with recent posts
    """
    info(f"Tool called: scrape_linkedin_posts for {company_name} (limit: {limit})")

    result = await apify_service.scrape_linkedin_posts(company_name, limit)

    if result["success"]:
        return {
            "success": True,
            "company_name": company_name,
            "posts": result.get("data", []),
            "error": None,
        }
    else:
        return {
            "success": False,
            "company_name": company_name,
            "posts": [],
            "error": result.get("error", "No posts found"),
        }


scrape_linkedin_posts_tool = Tool(
    scrape_linkedin_posts,
    description="Scrape recent LinkedIn posts from a company page for insights on strategic initiatives, announcements, and activity. Use this to understand what's happening at the company. Parameters: company_name (str) - company name, limit (int) - number of posts (default 10).",
)
