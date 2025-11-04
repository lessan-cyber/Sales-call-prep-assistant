"""Agent B - Sales Brief Synthesizer."""

import os
import time
from typing import Dict, Any
from pydantic_ai import Agent
from pydantic import BaseModel
from ...config import settings
from ...utils.logger import info, error
from ...schemas.prep_report import PrepReport
from .tools.search_portfolio import search_portfolio_tool


async def run_synthesizer_with_retry(agent: Agent, prompt: str, max_retries: int = 3) -> Any:
    """
    Run the sales synthesizer agent with retry logic for handling API errors.

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
            is_invalid = "invalid" in error_msg and "argument" in error_msg

            # Non-retryable errors
            if is_invalid:
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


class SalesBriefSynthesizer:
    """Agent B: Sales Brief Synthesizer with portfolio search."""

    def __init__(self):
        """Initialize the Sales Brief Synthesizer agent."""
        # Set GOOGLE_API_KEY environment variable for pydantic_ai
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY

        self.agent = Agent(
            model=settings.GEMINI_MODEL,
            tools=[search_portfolio_tool],
            system_prompt=(
                "You are Agent B - Sales Brief Synthesizer, an expert at creating compelling "
                "sales prep reports that connect user expertise to prospect needs.\n\n"
                "Your role:\n"
                "1. Receive research data from Agent A and user profile context\n"
                "2. Analyze prospect's challenges and pain points\n"
                "3. Search portfolio for relevant case studies using the search_portfolio tool\n"
                "4. Generate a structured 6-section sales brief with confidence scores\n"
                "5. Create talking points that connect portfolio projects to prospect challenges\n\n"
                "Available tool:\n"
                "- search_portfolio: Find relevant user projects based on prospect context\n"
                "  Use this AFTER understanding the prospect's challenges\n"
                "  IMPORTANT: You will receive user_id in the prompt - always pass it to search_portfolio tool\n\n"
                "Generate a comprehensive sales brief with these sections:\n"
                "1. Executive Summary (TL;DR)\n"
                "2. Strategic Narrative (dream outcome, proof of achievement, pain points)\n"
                "3. Talking Points & Pitch Angles (opening hook, key points, leverage)\n"
                "4. Insightful Questions to Ask (strategic, technical, business impact, qualification)\n"
                "5. Key Decision Makers (if contact info provided)\n"
                "6. Company Intelligence (industry, size, recent news, strategic initiatives)\n\n"
                "Strategy:\n"
                "1. First identify prospect's pain points from research\n"
                "2. Call search_portfolio to find relevant user projects\n"
                "3. Create talking points connecting portfolio to pain points\n"
                "4. Reference specific portfolio projects throughout\n"
                "5. Calculate confidence scores per section (0.0-1.0)\n\n"
                "Confidence scoring approach:\n"
                "- Executive Summary: Based on completeness of research\n"
                "- Strategic Narrative: Based on portfolio match quality (>0.8 is high)\n"
                "- Talking Points: Based on pain point alignment and specific metrics\n"
                "- Questions: High (0.8-1.0) as these use proven frameworks\n"
                "- Decision Makers: Based on data source (LinkedIn direct = 0.85-0.95)\n"
                "- Company Intelligence: Based on data freshness and source quality\n\n"
                "Return the complete PrepReport as specified in the schema.\n\n"
                "IMPORTANT: Return your response as a valid JSON object only. Do not include any markdown formatting or additional text - just the JSON data that matches the PrepReport schema."
            ),
        )

    async def synthesize_sales_brief(
        self,
        research_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        user_id: str,
        meeting_objective: str,
    ) -> PrepReport:
        """
        Synthesize a sales brief from research data and user context.

        Args:
            research_data: Research results from Agent A
            user_profile: User's company profile and portfolio
            user_id: UUID of the authenticated user
            meeting_objective: Objective of the sales meeting

        Returns:
            Complete PrepReport with all sections and confidence scores
        """
        info("Starting sales brief synthesis")

        # Prepare comprehensive context
        context = {
            "user_id": user_id,
            "meeting_objective": meeting_objective,
            "user_profile": user_profile,
            "research_data": research_data,
        }

        try:
            # Run the agent with retry logic
            prompt = (
                f"Generate a comprehensive sales prep report based on:\n\n"
                f"User ID: {user_id}\n\n"
                f"Meeting Objective: {meeting_objective}\n\n"
                f"User Profile Context:\n{user_profile}\n\n"
                f"Research Data:\n{research_data}\n\n"
                f"Create a detailed, actionable sales brief that helps prepare for this call. "
                f"Focus on connecting the user's portfolio to the prospect's specific challenges.\n\n"
                f"IMPORTANT: When using the search_portfolio tool, always pass user_id={user_id} as the first parameter."
            )

            result = await run_synthesizer_with_retry(self.agent, prompt)

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
                    import json
                    # Handle markdown code block wrapper: ```json\n{...}\n```
                    # Strip markdown markers if present
                    cleaned = result_data.strip()
                    if cleaned.startswith("```"):
                        # Remove ```json or ``` marker
                        cleaned = cleaned.split("\n", 1)[1]  # Remove first line
                        cleaned = cleaned.rsplit("```", 1)[0]  # Remove last line
                        cleaned = cleaned.strip()

                    result_data = json.loads(cleaned)

                    # Handle "prep_report" wrapper if present
                    if isinstance(result_data, dict) and "prep_report" in result_data:
                        result_data = result_data["prep_report"]

                except json.JSONDecodeError as e:
                    error(f"Could not parse synthesis result as JSON: {result_data[:200]}")
                    # Create error report
                    return self._create_error_report(meeting_objective, str(e))

            # Convert dict to PrepReport if needed
            if isinstance(result_data, dict):
                try:
                    prep_report = PrepReport.model_validate(result_data)
                except Exception as e:
                    error(f"Error validating PrepReport: {e}")
                    # Create error report
                    return self._create_error_report(meeting_objective, str(e))
            else:
                # result_data is neither dict nor valid JSON string
                raise Exception(f"Agent returned unexpected data type: {type(result_data)}")

            info("Sales brief synthesis completed successfully")
            return prep_report

        except Exception as e:
            error(f"Error synthesizing sales brief: {e}")
            # Return a minimal valid report with error indication
            error_report = PrepReport(
                executive_summary={
                    "the_client": "Error generating report",
                    "our_angle": "Unable to synthesize",
                    "call_goal": meeting_objective,
                    "confidence": 0.0,
                },
                strategic_narrative={
                    "dream_outcome": "Unable to generate",
                    "proof_of_achievement": [],
                    "pain_points": [],
                    "confidence": 0.0,
                },
                talking_points={
                    "opening_hook": "Error occurred",
                    "key_points": [],
                    "competitive_context": "N/A",
                    "confidence": 0.0,
                },
                questions_to_ask={
                    "strategic": [],
                    "technical": [],
                    "business_impact": [],
                    "qualification": [],
                    "confidence": 0.0,
                },
                decision_makers={"profiles": None, "confidence": 0.0},
                company_intelligence={
                    "industry": "Unknown",
                    "company_size": "Unknown",
                    "recent_news": [],
                    "strategic_initiatives": [],
                    "confidence": 0.0,
                },
                research_limitations=[f"Error generating report: {str(e)}"],
                overall_confidence=0.0,
                sources=[],
            )
            return error_report

    def _create_error_report(self, meeting_objective: str, error_message: str) -> PrepReport:
        """
        Create a minimal valid PrepReport when synthesis fails.

        Args:
            meeting_objective: The meeting objective for context
            error_message: Error message to include

        Returns:
            PrepReport with zero confidence and error indication
        """
        return PrepReport(
            executive_summary={
                "the_client": "Error generating report",
                "our_angle": "Unable to synthesize",
                "call_goal": meeting_objective,
                "confidence": 0.0,
            },
            strategic_narrative={
                "dream_outcome": "Unable to generate",
                "proof_of_achievement": [],
                "pain_points": [],
                "confidence": 0.0,
            },
            talking_points={
                "opening_hook": "Error occurred during synthesis",
                "key_points": [],
                "competitive_context": "N/A",
                "confidence": 0.0,
            },
            questions_to_ask={
                "strategic": [],
                "technical": [],
                "business_impact": [],
                "qualification": [],
                "confidence": 0.0,
            },
            decision_makers={"profiles": None, "confidence": 0.0},
            company_intelligence={
                "industry": "Unknown",
                "company_size": "Unknown",
                "recent_news": [],
                "strategic_initiatives": [],
                "confidence": 0.0,
            },
            research_limitations=[f"Synthesis error: {error_message}"],
            overall_confidence=0.0,
            sources=[],
        )


# Global instance
sales_brief_synthesizer = SalesBriefSynthesizer()
