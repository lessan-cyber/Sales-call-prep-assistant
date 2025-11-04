"""Agent A - Research Orchestrator with tool-calling."""

import os
import time
import json
from typing import Dict, Any, List
from pydantic_ai import Agent
from requests import api
from ...config import settings
from ...utils.logger import info, error
from .tools.web_search import web_search_tool
from .tools.scrape_website import scrape_website_tool
from .tools.get_company_linkedin import get_company_linkedin_tool
from .tools.search_linkedin_profile import search_linkedin_profile_tool
from .tools.scrape_linkedin_posts import scrape_linkedin_posts_tool


async def run_with_retry(agent: Agent, prompt: str, max_retries: int = 3) -> Any:
    """
    Run an agent with retry logic for handling API errors.

    Args:
        agent: The pydantic_ai agent to run
        prompt: The prompt to send to the agent
        max_retries: Maximum number of retry attempts

    Returns:
        The agent result

    Raises:
        Exception: If all retries are exhausted
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            result = await agent.run(prompt)
            return result
        except Exception as e:
            last_error = e
            error_msg = str(e).lower()

            # Check if this is a retryable error
            is_rate_limit = "429" in error_msg or "rate limit" in error_msg
            is_quota_exceeded = "quota" in error_msg or "billing" in error_msg
            is_server_error = any(code in error_msg for code in ["500", "502", "503", "504"])
            is_overloaded = "overloaded" in error_msg or "busy" in error_msg

            # Non-retryable errors
            if "invalid" in error_msg and "argument" in error_msg:
                error(f"Non-retryable error: {e}")
                raise e

            if attempt < max_retries - 1:
                # Calculate backoff delay (exponential: 1s, 2s, 4s)
                delay = 2 ** attempt
                error(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")

                # Additional delay for specific error types
                if is_rate_limit:
                    delay = min(delay * 2, 30)  # Longer delay for rate limits
                elif is_quota_exceeded:
                    error(f"Quota exceeded: {e}. Not retrying.")
                    raise e

                time.sleep(delay)
            else:
                error(f"All {max_retries} attempts failed. Last error: {e}")

    # If we get here, all retries failed
    raise last_error


class ResearchOrchestrator:
    """Agent A: Research Orchestrator with intelligent tool-calling."""

    def __init__(self):
        """Initialize the Research Orchestrator agent."""
        # Set GOOGLE_API_KEY environment variable for pydantic_ai
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY

        self.agent = Agent(
            model=settings.GEMINI_MODEL,
            tools=[
                web_search_tool,
                scrape_website_tool,
                get_company_linkedin_tool,
                search_linkedin_profile_tool,
                scrape_linkedin_posts_tool,
            ],
            system_prompt=(
                "You are Agent A - Research Orchestrator, an expert at intelligently gathering "
                "information about companies and decision makers for sales preparation.\n\n"
                "Your role:\n"
                "1. Receive a company name, meeting objective, and optional contact information\n"
                "2. Intelligently decide which tools to call and in what order\n"
                "3. Make iterative tool calls based on what you learn\n"
                "4. Analyze results and decide if more research is needed\n"
                "5. Return structured research data with confidence scores\n\n"
                "Available tools:\n"
                "- web_search: Search the web for general info, news, or to find LinkedIn profiles\n"
                "- scrape_website: Get detailed company info from their website\n"
                "- get_company_linkedin: Get company data from LinkedIn (size, industry, posts)\n"
                "- search_linkedin_profile: Find specific person's profile with high accuracy\n"
                "- scrape_linkedin_posts: Get recent company posts for strategic insights\n\n"
                "Strategy:\n"
                "1. Start with web_search to find official website and basic info\n"
                "2. Use scrape_website for detailed company information\n"
                "3. Use get_company_linkedin for company size, industry, and activity\n"
                "4. If contact info provided, use search_linkedin_profile for decision maker data\n"
                "5. Use scrape_linkedin_posts to understand recent strategic initiatives\n\n"
                "Decision-making guidelines:\n"
                "- If web search fails, try alternative queries\n"
                "- If scraping fails, note limitation and continue with available data\n"
                "- If LinkedIn data not found, focus on web search and company website\n"
                "- Always try to gather enough data for high confidence (>0.7)\n"
                "- Call tools iteratively, not all at once\n"
                "- Stop when you have sufficient data for sales preparation\n\n"
                "Return a structured research package with:\n"
                "- company_intelligence: {name, industry, size, description, recent_news, strategic_initiatives}\n"
                "- decision_makers: [{name, title, linkedin_url, background, recent_activity}]\n"
                "- research_limitations: [list of any data gaps]\n"
                "- overall_confidence: score from 0.0 to 1.0\n"
                "- sources_used: [list of sources]\n\n"
                "IMPORTANT: Return your research as a valid JSON object. Do not include any markdown formatting or additional text - just the JSON data.\n"
            ),
        )

    async def research_company(
        self,
        company_name: str,
        meeting_objective: str,
        contact_person_name: str = None,
        contact_linkedin_url: str = None,
    ) -> Dict[str, Any]:
        """
        Orchestrate research for a company using intelligent tool-calling.

        Args:
            company_name: Name of the company to research
            meeting_objective: Objective of the sales meeting
            contact_person_name: Optional name of contact person
            contact_linkedin_url: Optional LinkedIn URL of contact

        Returns:
            Structured research data with confidence scores
        """
        info(f"Starting research for {company_name}")

        # Prepare context for the agent
        context = {
            "company_name": company_name,
            "meeting_objective": meeting_objective,
            "contact_person_name": contact_person_name,
            "contact_linkedin_url": contact_linkedin_url,
        }

        try:
            # Run the agent with retry logic
            prompt = (
                f"Research {company_name} for a sales meeting. "
                f"Meeting objective: {meeting_objective}. "
                f"Contact person: {contact_person_name if contact_person_name else 'Not provided'}. "
                f"LinkedIn URL: {contact_linkedin_url if contact_linkedin_url else 'Not provided'}. "
                f"Gather comprehensive intelligence to help prepare for this sales call. "
                f"Return the research as a JSON object with these fields: "
                f"company_intelligence, decision_makers, research_limitations, overall_confidence, sources_used."
            )
            result = await run_with_retry(self.agent, prompt)

            info(f"Research completed for {company_name}")

            # Get the result data - handle different pydantic_ai versions
            if hasattr(result, 'data'):
                result_data = result.data
            elif hasattr(result, 'output'):
                result_data = result.output
            else:
                # Fallback to str representation
                result_data = str(result)

            # Ensure result_data is a dictionary
            if isinstance(result_data, str):
                # Try to parse as JSON
                try:
                    result_data = json.loads(result_data)
                except json.JSONDecodeError:
                    error(f"Could not parse research data as JSON: {result_data}")
                    result_data = {
                        "company_intelligence": {
                            "name": company_name,
                            "description": "Unable to parse research data"
                        },
                        "decision_makers": [],
                        "research_limitations": ["Research data format invalid"],
                        "overall_confidence": 0.1,
                        "sources_used": []
                    }

            # Extract sources and confidence from result
            if isinstance(result_data, dict):
                sources_used = result_data.get("sources_used", [])
                confidence_score = result_data.get("overall_confidence", 0.5)
            else:
                sources_used = []
                confidence_score = 0.5

            return {
                "success": True,
                "company_name": company_name,
                "research_data": result_data,
                "sources_used": sources_used,
                "confidence_score": confidence_score,
            }

        except Exception as e:
            error(f"Error during research for {company_name}: {e}")
            return {
                "success": False,
                "company_name": company_name,
                "error": str(e),
                "research_data": None,
                "confidence_score": 0.0,
            }


# Global instance
research_orchestrator = ResearchOrchestrator()
