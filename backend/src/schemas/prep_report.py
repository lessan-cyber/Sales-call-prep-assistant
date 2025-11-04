"""Schemas for sales prep reports."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class PrepRequest(BaseModel):
    """Input request for creating a new sales prep report."""
    company_name: str = Field(..., description="Name of the prospect company")
    meeting_objective: str = Field(..., description="Objective of the sales meeting")
    contact_person_name: Optional[str] = Field(None, description="Name of the contact person")
    contact_linkedin_url: Optional[str] = Field(None, description="LinkedIn URL of the contact person")
    meeting_date: Optional[str] = Field(None, description="Scheduled meeting date (ISO format)")


class PainPoint(BaseModel):
    """Represents a specific pain point."""
    pain: str = Field(..., description="Description of the pain point")
    urgency: int = Field(..., ge=1, le=5, description="Urgency level (1-5)")
    impact: int = Field(..., ge=1, le=5, description="Business impact level (1-5)")
    evidence: List[str] = Field(default_factory=list, description="Evidence supporting this pain point")


class PortfolioMatch(BaseModel):
    """Represents a portfolio project match."""
    project_name: str = Field(..., description="Name of the matching project")
    relevance: str = Field(..., description="Why this project is relevant")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0.0-1.0)")


class ExecutiveSummary(BaseModel):
    """Section 1: Executive Summary (TL;DR)."""
    the_client: str = Field(..., description="Company description and strategic focus")
    our_angle: str = Field(..., description="How user's goals align with prospect's portfolio")
    call_goal: str = Field(..., description="Clear objective for this meeting")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this section")


class StrategicNarrative(BaseModel):
    """Section 2: Strategic Narrative."""
    dream_outcome: str = Field(..., description="What the prospect wants to achieve")
    proof_of_achievement: List[PortfolioMatch] = Field(
        default_factory=list,
        description="Top portfolio matches with specific results"
    )
    pain_points: List[PainPoint] = Field(
        default_factory=list,
        description="3-5 pain points ranked by urgency and impact"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this section")


class TalkingPoints(BaseModel):
    """Section 3: Talking Points & Pitch Angles."""
    opening_hook: str = Field(..., description="Specific observation to start the conversation")
    key_points: List[str] = Field(
        default_factory=list,
        description="4-6 points connecting experience to prospect's challenges"
    )
    competitive_context: str = Field(..., description="Leverage their context for positioning")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this section")


class QuestionsToAsk(BaseModel):
    """Section 4: Insightful Questions to Ask."""
    strategic: List[str] = Field(default_factory=list, description="Strategic questions")
    technical: List[str] = Field(default_factory=list, description="Technical questions")
    business_impact: List[str] = Field(default_factory=list, description="Business impact questions")
    qualification: List[str] = Field(default_factory=list, description="Qualification questions")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this section")


class DecisionMaker(BaseModel):
    """Represents a decision maker profile."""
    name: str = Field(..., description="Decision maker's name")
    title: str = Field(..., description="Current job title")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    background_points: List[str] = Field(
        default_factory=list,
        description="2-3 background points"
    )


class DecisionMakers(BaseModel):
    """Section 5: Key Decision Makers."""
    profiles: Optional[List[DecisionMaker]] = Field(None, description="Decision maker profiles")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this section")


class NewsItem(BaseModel):
    """Represents a recent news item."""
    headline: str = Field(..., description="News headline")
    date: str = Field(..., description="Date of the news")
    significance: str = Field(..., description="Why this news matters")


class CompanyIntelligence(BaseModel):
    """Section 6: Company Intelligence."""
    industry: str = Field(..., description="Specific sector/vertical")
    company_size: str = Field(..., description="Employee count estimate + revenue")
    recent_news: List[NewsItem] = Field(
        default_factory=list,
        description="3-5 recent events with dates"
    )
    strategic_initiatives: List[str] = Field(
        default_factory=list,
        description="Current priorities based on news/job postings"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this section")


class PrepReport(BaseModel):
    """Complete sales prep report with all sections."""
    executive_summary: ExecutiveSummary = Field(..., description="Executive Summary section")
    strategic_narrative: StrategicNarrative = Field(..., description="Strategic Narrative section")
    talking_points: TalkingPoints = Field(..., description="Talking Points section")
    questions_to_ask: QuestionsToAsk = Field(..., description="Questions to Ask section")
    decision_makers: DecisionMakers = Field(..., description="Decision Makers section")
    company_intelligence: CompanyIntelligence = Field(..., description="Company Intelligence section")
    research_limitations: List[str] = Field(
        default_factory=list,
        description="List of research limitations or gaps"
    )
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    sources: List[str] = Field(default_factory=list, description="Source URLs used")
