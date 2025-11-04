"""LinkedIn profile search tool for Agent A - Research Orchestrator."""
from typing import Dict, Any
from pydantic_ai import Tool
from ....services.apify_service import apify_service
from ....utils.logger import info


async def search_linkedin_profile(person_name: str, company_name: str) -> Dict[str, Any]:
    """
    Search for a person's LinkedIn profile using Apify actor.

    Args:
        person_name: Name of the person to search for
        company_name: Name of their company

    Returns:
        Dictionary with profile data
    """
    info(f"Tool called: search_linkedin_profile for {person_name} at {company_name}")

    result = await apify_service.search_linkedin_profile(person_name, company_name)

    if result["success"]:
        return {
            "success": True,
            "person_name": person_name,
            "company_name": company_name,
            "data": result.get("data", {}),
            "error": None
        }
    else:
        return {
            "success": False,
            "person_name": person_name,
            "company_name": company_name,
            "data": None,
            "error": result.get("error", "Profile not found")
        }


search_linkedin_profile_tool = Tool(
    search_linkedin_profile,
    description="Search for a specific person's LinkedIn profile by name and company. Use this when you have contact information to get high-confidence decision maker data. Parameters: person_name (str) - person's name, company_name (str) - their company."
)
