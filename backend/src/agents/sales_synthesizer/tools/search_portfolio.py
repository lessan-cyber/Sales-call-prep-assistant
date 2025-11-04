"""Portfolio search tool for Agent B - Sales Brief Synthesizer."""

from typing import List, Dict, Any
from pydantic_ai import Tool
from ....services.supabase_service import get_supabase_service
from ....utils.logger import info


async def search_portfolio(
    user_id: str, search_query: str, limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Search through user's portfolio projects for relevance.

    Args:
        user_id: UUID of the user whose portfolio to search
        search_query: Query combining prospect's pain points, industry, and required services
        limit: Maximum number of matching projects to return

    Returns:
        List of matching projects with relevance scores
    """
    info(f"Tool called: search_portfolio for user {user_id} with query: {search_query}")

    supabase = get_supabase_service()
    matches = await supabase.search_portfolio_projects(
        user_id, search_query, limit
    )

    return matches


search_portfolio_tool = Tool(
    search_portfolio,
    description="Search through the user's portfolio projects to find the most relevant case studies based on the prospect's challenges. Use this after understanding the prospect's pain points. Parameters: user_id (str) - user's UUID, search_query (str) - description of prospect's challenges, limit (int) - max results (default 5).",
)
