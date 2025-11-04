"""Company LinkedIn scraping tool for Agent A - Research Orchestrator."""
from typing import Dict, Any
from pydantic_ai import Tool
from ....services.apify_service import apify_service
from ....utils.logger import info


async def get_company_linkedin(company_name: str) -> Dict[str, Any]:
    """
    Scrape company LinkedIn page using Apify actor.

    Args:
        company_name: Name of the company to scrape

    Returns:
        Dictionary with LinkedIn company data
    """
    info(f"Tool called: get_company_linkedin for company: {company_name}")

    result = await apify_service.scrape_company_linkedin(company_name)

    if result["success"]:
        return {
            "success": True,
            "company_name": company_name,
            "data": result.get("data", {}),
            "error": None
        }
    else:
        return {
            "success": False,
            "company_name": company_name,
            "data": None,
            "error": result.get("error", "LinkedIn data not found")
        }


get_company_linkedin_tool = Tool(
    get_company_linkedin,
    description="Scrape company LinkedIn page for company size, industry, recent posts, hiring signals, and activity. Use this to get official company data. Parameter: company_name (str) - company name."
)
