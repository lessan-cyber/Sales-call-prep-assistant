"""Agent B - Sales Brief Synthesizer."""

import os
from typing import Dict, Any
from pydantic_ai import Agent
from pydantic import BaseModel
from ...config import settings
from ...utils.logger import info, error
from ...schemas.prep_report import PrepReport
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
                "  Use this AFTER understanding the prospect's challenges\n\n"
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
                "Return the complete PrepReport as specified in the schema."
            ),
        )

    async def synthesize_sales_brief(
        self,
        research_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        meeting_objective: str,
    ) -> PrepReport:
        """
        Synthesize a sales brief from research data and user context.

        Args:
            research_data: Research results from Agent A
            user_profile: User's company profile and portfolio
            meeting_objective: Objective of the sales meeting

        Returns:
            Complete PrepReport with all sections and confidence scores
        """
        info("Starting sales brief synthesis")

        # Prepare comprehensive context
        context = {
            "meeting_objective": meeting_objective,
            "user_profile": user_profile,
            "research_data": research_data,
        }

        try:
            # Run the agent to synthesize the brief
            prompt = (
                f"Generate a comprehensive sales prep report based on:\n\n"
                f"Meeting Objective: {meeting_objective}\n\n"
                f"User Profile Context:\n{user_profile}\n\n"
                f"Research Data:\n{research_data}\n\n"
                f"Create a detailed, actionable sales brief that helps prepare for this call. "
                f"Focus on connecting the user's portfolio to the prospect's specific challenges."
            )

            result = await self.agent.run(prompt)
            prep_report = result.data

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


# Global instance
sales_brief_synthesizer = SalesBriefSynthesizer()
