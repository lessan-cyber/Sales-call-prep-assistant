from pydantic import BaseModel, Field
from typing import List, Optional

class ExecutiveSummary(BaseModel):
    summary: str = Field(..., description="A concise overview of the company and key insights relevant to the meeting.")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score for the executive summary (0-1).")

class StrategicNarrative(BaseModel):
    narrative: str = Field(..., description="A strategic narrative outlining how the user's offerings align with the prospect's needs and objectives.")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score for the strategic narrative (0-1).")

class KeyTalkingPoint(BaseModel):
    point: str = Field(..., description="A specific talking point for the sales call.")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score for the talking point (0-1).")

class InsightfulQuestion(BaseModel):
    question: str = Field(..., description="An insightful question to ask during the sales call.")
    category: str = Field(..., description="Category of the question (e.g., 'Business Challenges', 'Strategic Goals').")

class KeyDecisionMaker(BaseModel):
    name: str = Field(..., description="Name of the key decision-maker.")
    title: str = Field(..., description="Title of the key decision-maker.")
    linkedin_profile: Optional[str] = Field(None, description="LinkedIn profile URL of the decision-maker.")
    key_interests: Optional[List[str]] = Field(None, description="Key interests or recent activities of the decision-maker.")

class CompanyIntelligence(BaseModel):
    overview: str = Field(..., description="General overview and background of the company.")
    recent_news: Optional[List[str]] = Field(None, description="List of recent news or press releases related to the company.")
    industry_trends: Optional[List[str]] = Field(None, description="Relevant industry trends affecting the company.")
    competitors: Optional[List[str]] = Field(None, description="List of key competitors of the company.")

class PrepReport(BaseModel):
    executive_summary: ExecutiveSummary
    strategic_narrative: StrategicNarrative
    key_talking_points: List[KeyTalkingPoint]
    insightful_questions: List[InsightfulQuestion]
    key_decision_makers: List[KeyDecisionMaker]
    company_intelligence: CompanyIntelligence
    overall_confidence: float = Field(..., ge=0, le=1, description="Overall confidence score for the entire report (0-1).")
