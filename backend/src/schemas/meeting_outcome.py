"""Pydantic schemas for meeting outcome recording."""

from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class MeetingStatus(str, Enum):
    """Meeting status enum."""
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class MeetingOutcomeValue(str, Enum):
    """Meeting outcome enum."""
    SUCCESSFUL = "successful"
    NEEDS_IMPROVEMENT = "needs_improvement"
    LOST_OPPORTUNITY = "lost_opportunity"


class PrepSection(str, Enum):
    """Most useful prep section enum."""
    EXECUTIVE_SUMMARY = "executive_summary"
    TALKING_POINTS = "talking_points"
    QUESTIONS = "questions"
    DECISION_MAKERS = "decision_makers"
    COMPANY_INTELLIGENCE = "company_intelligence"


class MeetingOutcomeCreate(BaseModel):
    """Schema for creating a meeting outcome."""
    meeting_status: MeetingStatus = Field(
        ...,
        description="Status of the meeting"
    )
    outcome: Optional[MeetingOutcomeValue] = Field(
        None,
        description="Overall outcome of the meeting"
    )
    prep_accuracy: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="How accurate the prep was (1-5 scale)"
    )
    most_useful_section: Optional[PrepSection] = Field(
        None,
        description="Which section of the prep was most useful"
    )
    what_was_missing: Optional[str] = Field(
        None,
        max_length=1000,
        description="What information was missing from the prep"
    )
    general_notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="General notes about the meeting"
    )


class MeetingOutcomeResponse(BaseModel):
    """Schema for meeting outcome response."""
    id: str
    prep_id: str
    meeting_status: MeetingStatus
    outcome: Optional[MeetingOutcomeValue]
    prep_accuracy: Optional[int]
    most_useful_section: Optional[PrepSection]
    what_was_missing: Optional[str]
    general_notes: Optional[str]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
