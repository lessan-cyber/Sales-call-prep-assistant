"""Agent B - Sales Brief Synthesizer."""

import os
from typing import Dict, Any
from pydantic_ai import Agent
from pydantic import BaseModel, ValidationError
from ...config import settings
from ...utils.logger import info, error
from ...schemas.prep_report import PrepReport
from ...utils.retry import run_agent_with_retry
from .tools.search_portfolio import search_portfolio_tool


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
                "STRICT JSON OUTPUT FORMAT:\n"
                "You MUST return a JSON object with EXACTLY these fields:\n\n"
                "{\n"
                '  "executive_summary": {\n'
                '    "the_client": "string - company description and strategic focus",\n'
                '    "our_angle": "string - how user goals align with prospect",\n'
                '    "call_goal": "string - clear objective for this meeting",\n'
                '    "confidence": 0.0\n'
                "  },\n"
                '  "strategic_narrative": {\n'
                '    "dream_outcome": "string - what prospect wants to achieve",\n'
                '    "proof_of_achievement": [\n'
                "      {\n"
                '        "project_name": "string - portfolio project name",\n'
                '        "relevance": "string - why this project is relevant",\n'
                '        "relevance_score": 0.0\n'
                "      }\n"
                "    ],\n"
                '    "pain_points": [\n'
                "      {\n"
                '        "pain": "string - description of pain point",\n'
                '        "urgency": 1,\n'
                '        "impact": 1,\n'
                '        "evidence": ["string"]\n'
                "      }\n"
                "    ],\n"
                '    "confidence": 0.0\n'
                "  },\n"
                '  "talking_points": {\n'
                '    "opening_hook": "string - specific observation to start",\n'
                '    "key_points": ["string"],\n'
                '    "competitive_context": "string - leverage their context",\n'
                '    "confidence": 0.0\n'
                "  },\n"
                '  "questions_to_ask": {\n'
                '    "strategic": ["string"],\n'
                '    "technical": ["string"],\n'
                '    "business_impact": ["string"],\n'
                '    "qualification": ["string"],\n'
                '    "confidence": 0.0\n'
                "  },\n"
                '  "decision_makers": {\n'
                '    "profiles": [\n'
                "      {\n"
                '        "name": "string",\n'
                '        "title": "string",\n'
                '        "linkedin_url": "string",\n'
                '        "background_points": ["string"]\n'
                "      }\n"
                "    ],\n"
                '    "confidence": 0.0\n'
                "  },\n"
                '  "company_intelligence": {\n'
                '    "industry": "string - specific sector/vertical",\n'
                '    "company_size": "string - employee count + revenue",\n'
                '    "recent_news": [\n'
                "      {\n"
                '        "headline": "string",\n'
                '        "date": "string",\n'
                '        "significance": "string"\n'
                "      }\n"
                "    ],\n"
                '    "strategic_initiatives": ["string"],\n'
                '    "confidence": 0.0\n'
                "  },\n"
                '  "research_limitations": ["string"],\n'
                '  "overall_confidence": 0.0,\n'
                '  "sources": ["string"]\n'
                "}\n\n"
                "CRITICAL REQUIREMENTS:\n"
                "1. Use EXACT field names shown above (the_client NOT summary, confidence NOT confidence_score)\n"
                "2. pain_points must be objects with pain, urgency, impact, evidence fields - NOT strings\n"
                "3. proof_of_achievement must be objects with project_name, relevance, relevance_score - NOT strings\n"
                "4. All confidence scores must be floats between 0.0 and 1.0\n"
                "5. Return ONLY the JSON object, no markdown formatting\n\n"
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
                "Return ONLY valid JSON matching this exact schema."
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

            result = await run_agent_with_retry(self.agent, prompt)

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
                except ValidationError as e:
                    error(f"Error validating PrepReport: {e}")
                    # Create error report
                    return self._create_error_report(meeting_objective, str(e))
            else:
                # result_data is neither dict nor valid JSON string
                raise TypeError(
                    f"Agent returned unexpected data type: {type(result_data)}"
                ) from None

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
