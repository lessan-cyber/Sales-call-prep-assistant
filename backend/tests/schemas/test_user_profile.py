"""Tests for user profile schemas."""
import pytest
from pydantic import ValidationError
from backend.src.schemas.user_profile import UserProfile


class TestUserProfile:
    """Test UserProfile schema validation."""

    def test_valid_user_profile_minimal(self):
        """Test creation with minimal required fields."""
        profile = UserProfile(
            company_name="Test LLC",
            company_description="A test company",
            industries_served=["Technology"],
            portfolio=[]
        )
        assert profile.company_name == "Test LLC"
        assert profile.company_description == "A test company"
        assert profile.industries_served == ["Technology"]
        assert profile.portfolio == []

    def test_valid_user_profile_full(self):
        """Test creation with full portfolio."""
        profile = UserProfile(
            company_name="Consulting Inc",
            company_description="Full-service consulting",
            industries_served=["Tech", "Healthcare", "Finance"],
            portfolio=[
                {
                    "project_name": "Project A",
                    "description": "AI implementation",
                    "technologies": ["Python", "TensorFlow"],
                    "results": "50% efficiency gain"
                },
                {
                    "project_name": "Project B",
                    "description": "Cloud migration",
                    "technologies": ["AWS", "Kubernetes"],
                    "results": "Reduced costs by 30%"
                }
            ]
        )
        assert len(profile.portfolio) == 2
        assert profile.portfolio[0]["project_name"] == "Project A"
        assert len(profile.industries_served) == 3

    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(
                company_description="Test",
                industries_served=["Tech"],
                portfolio=[]
            )
        assert "company_name" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserProfile(
                company_name="Test",
                industries_served=["Tech"],
                portfolio=[]
            )
        assert "company_description" in str(exc_info.value)

    def test_empty_industries_served(self):
        """Test profile with empty industries list."""
        profile = UserProfile(
            company_name="Test",
            company_description="Test",
            industries_served=[],
            portfolio=[]
        )
        assert profile.industries_served == []

    def test_portfolio_structure(self):
        """Test portfolio items have expected structure."""
        profile = UserProfile(
            company_name="Test",
            company_description="Test",
            industries_served=["Tech"],
            portfolio=[
                {
                    "project_name": "Test Project",
                    "description": "Test description",
                    "technologies": ["Python"],
                    "results": "Test results"
                }
            ]
        )
        assert isinstance(profile.portfolio[0], dict)
        assert "project_name" in profile.portfolio[0]
        assert "description" in profile.portfolio[0]
        assert "technologies" in profile.portfolio[0]
        assert "results" in profile.portfolio[0]