"""Tests for prep report schemas."""
import pytest
from pydantic import ValidationError
from backend.src.schemas.prep_report import (
    PrepRequest,
    PainPoint,
    PortfolioMatch,
    ExecutiveSummary,
    StrategicNarrative,
    TalkingPoints,
)


class TestPrepRequest:
    """Test PrepRequest schema validation."""

    def test_valid_prep_request_minimal(self):
        """Test creation with only required fields."""
        request = PrepRequest(
            company_name="Acme Corp",
            meeting_objective="Discuss partnership opportunities"
        )
        assert request.company_name == "Acme Corp"
        assert request.meeting_objective == "Discuss partnership opportunities"
        assert request.contact_person_name is None
        assert request.contact_linkedin_url is None
        assert request.meeting_date is None

    def test_valid_prep_request_full(self):
        """Test creation with all fields."""
        request = PrepRequest(
            company_name="Acme Corp",
            meeting_objective="Discuss AI implementation",
            contact_person_name="John Doe",
            contact_linkedin_url="https://linkedin.com/in/johndoe",
            meeting_date="2024-01-15"
        )
        assert request.company_name == "Acme Corp"
        assert request.contact_person_name == "John Doe"
        assert request.contact_linkedin_url == "https://linkedin.com/in/johndoe"
        assert request.meeting_date == "2024-01-15"

    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            PrepRequest(company_name="Acme Corp")
        assert "meeting_objective" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            PrepRequest(meeting_objective="Discuss partnership")
        assert "company_name" in str(exc_info.value)

    def test_empty_string_fields(self):
        """Test that empty strings are accepted for required fields."""
        # This should raise validation error if we add min_length validators
        request = PrepRequest(company_name="", meeting_objective="")
        assert request.company_name == ""
        assert request.meeting_objective == ""


class TestPainPoint:
    """Test PainPoint schema validation."""

    def test_valid_pain_point(self):
        """Test creation with valid data."""
        pain = PainPoint(
            pain="High customer churn rate",
            urgency=5,
            impact=4,
            evidence=["Q4 report shows 20% churn", "Customer survey results"]
        )
        assert pain.pain == "High customer churn rate"
        assert pain.urgency == 5
        assert pain.impact == 4
        assert len(pain.evidence) == 2

    def test_urgency_validation(self):
        """Test urgency must be between 1 and 5."""
        with pytest.raises(ValidationError):
            PainPoint(pain="Test", urgency=0, impact=3, evidence=[])

        with pytest.raises(ValidationError):
            PainPoint(pain="Test", urgency=6, impact=3, evidence=[])

        # Valid boundaries
        pain1 = PainPoint(pain="Test", urgency=1, impact=3, evidence=[])
        pain5 = PainPoint(pain="Test", urgency=5, impact=3, evidence=[])
        assert pain1.urgency == 1
        assert pain5.urgency == 5

    def test_impact_validation(self):
        """Test impact must be between 1 and 5."""
        with pytest.raises(ValidationError):
            PainPoint(pain="Test", urgency=3, impact=0, evidence=[])

        with pytest.raises(ValidationError):
            PainPoint(pain="Test", urgency=3, impact=6, evidence=[])

        # Valid boundaries
        pain1 = PainPoint(pain="Test", urgency=3, impact=1, evidence=[])
        pain5 = PainPoint(pain="Test", urgency=3, impact=5, evidence=[])
        assert pain1.impact == 1
        assert pain5.impact == 5

    def test_empty_evidence_list(self):
        """Test pain point with empty evidence list."""
        pain = PainPoint(pain="Test", urgency=3, impact=3, evidence=[])
        assert pain.evidence == []

    def test_evidence_default_factory(self):
        """Test evidence defaults to empty list."""
        pain = PainPoint(pain="Test", urgency=3, impact=3)
        assert pain.evidence == []


class TestPortfolioMatch:
    """Test PortfolioMatch schema validation."""

    def test_valid_portfolio_match(self):
        """Test creation with valid data."""
        match = PortfolioMatch(
            project_name="AI Chatbot",
            relevance="Similar customer service automation needs",
            relevance_score=0.85
        )
        assert match.project_name == "AI Chatbot"
        assert match.relevance == "Similar customer service automation needs"
        assert match.relevance_score == 0.85

    def test_relevance_score_validation(self):
        """Test relevance_score must be between 0.0 and 1.0."""
        with pytest.raises(ValidationError):
            PortfolioMatch(
                project_name="Test",
                relevance="Test",
                relevance_score=-0.1
            )

        with pytest.raises(ValidationError):
            PortfolioMatch(
                project_name="Test",
                relevance="Test",
                relevance_score=1.1
            )

        # Valid boundaries
        match0 = PortfolioMatch(
            project_name="Test",
            relevance="Test",
            relevance_score=0.0
        )
        match1 = PortfolioMatch(
            project_name="Test",
            relevance="Test",
            relevance_score=1.0
        )
        assert match0.relevance_score == 0.0
        assert match1.relevance_score == 1.0


class TestExecutiveSummary:
    """Test ExecutiveSummary schema validation."""

    def test_valid_executive_summary(self):
        """Test creation with valid data."""
        summary = ExecutiveSummary(
            the_client="Enterprise SaaS company focused on customer success",
            our_angle="Proven track record in AI-powered customer engagement",
            call_goal="Explore opportunities for AI chatbot implementation",
            confidence=0.9
        )
        assert summary.the_client == "Enterprise SaaS company focused on customer success"
        assert summary.our_angle == "Proven track record in AI-powered customer engagement"
        assert summary.call_goal == "Explore opportunities for AI chatbot implementation"
        assert summary.confidence == 0.9

    def test_confidence_validation(self):
        """Test confidence must be between 0.0 and 1.0."""
        with pytest.raises(ValidationError):
            ExecutiveSummary(
                the_client="Test",
                our_angle="Test",
                call_goal="Test",
                confidence=-0.1
            )

        with pytest.raises(ValidationError):
            ExecutiveSummary(
                the_client="Test",
                our_angle="Test",
                call_goal="Test",
                confidence=1.5
            )


class TestStrategicNarrative:
    """Test StrategicNarrative schema validation."""

    def test_valid_strategic_narrative(self):
        """Test creation with valid data."""
        narrative = StrategicNarrative(
            dream_outcome="Reduce customer support costs by 50%",
            proof_of_achievement=[
                PortfolioMatch(
                    project_name="Project A",
                    relevance="Similar outcome",
                    relevance_score=0.9
                )
            ],
            pain_points=[
                PainPoint(
                    pain="High support ticket volume",
                    urgency=5,
                    impact=4,
                    evidence=["Q4 metrics"]
                )
            ],
            confidence=0.85
        )
        assert narrative.dream_outcome == "Reduce customer support costs by 50%"
        assert len(narrative.proof_of_achievement) == 1
        assert len(narrative.pain_points) == 1
        assert narrative.confidence == 0.85

    def test_empty_lists(self):
        """Test narrative with empty proof and pain points."""
        narrative = StrategicNarrative(
            dream_outcome="Test outcome",
            proof_of_achievement=[],
            pain_points=[],
            confidence=0.5
        )
        assert narrative.proof_of_achievement == []
        assert narrative.pain_points == []

    def test_default_factory_lists(self):
        """Test lists default to empty."""
        narrative = StrategicNarrative(
            dream_outcome="Test outcome",
            confidence=0.5
        )
        assert narrative.proof_of_achievement == []
        assert narrative.pain_points == []


class TestTalkingPoints:
    """Test TalkingPoints schema validation."""

    def test_valid_talking_points(self):
        """Test creation with valid data."""
        points = TalkingPoints(
            opening_hook="I noticed your recent product launch announcement",
            key_points=[
                "Point 1: Experience with similar implementations",
                "Point 2: Proven ROI metrics",
                "Point 3: Fast deployment timeline"
            ],
            competitive_context="Unlike traditional vendors, we focus on rapid deployment",
            confidence=0.8
        )
        assert points.opening_hook == "I noticed your recent product launch announcement"
        assert len(points.key_points) == 3
        assert points.competitive_context == "Unlike traditional vendors, we focus on rapid deployment"
        assert points.confidence == 0.8

    def test_empty_key_points(self):
        """Test talking points with empty key points list."""
        points = TalkingPoints(
            opening_hook="Hook",
            key_points=[],
            competitive_context="Context",
            confidence=0.7
        )
        assert points.key_points == []

    def test_default_factory_key_points(self):
        """Test key_points defaults to empty list."""
        points = TalkingPoints(
            opening_hook="Hook",
            competitive_context="Context",
            confidence=0.7
        )
        assert points.key_points == []