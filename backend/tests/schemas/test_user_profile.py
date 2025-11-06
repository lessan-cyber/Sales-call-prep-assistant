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
            portfolio=[
                {
                    "name": "Project 1",
                    "client_industry": "Technology",
                    "description": "A test project",
                    "key_outcomes": "Test results"
                },
                {
                    "name": "Project 2",
                    "client_industry": "Healthcare",
                    "description": "Another test project",
                    "key_outcomes": "More test results"
                },
                {
                    "name": "Project 3",
                    "client_industry": "Finance",
                    "description": "Third test project",
                    "key_outcomes": "Additional test results"
                },
                {
                    "name": "Project 4",
                    "client_industry": "Retail",
                    "description": "Fourth test project",
                    "key_outcomes": "Further test results"
                },
                {
                    "name": "Project 5",
                    "client_industry": "Manufacturing",
                    "description": "Fifth test project",
                    "key_outcomes": "Final test results"
                }
            ]
        )
        assert profile.company_name == "Test LLC"
        assert profile.company_description == "A test company"
        assert profile.industries_served == ["Technology"]
        assert len(profile.portfolio) == 5

    def test_valid_user_profile_full(self):
        """Test creation with full portfolio."""
        profile = UserProfile(
            company_name="Consulting Inc",
            company_description="Full-service consulting",
            industries_served=["Tech", "Healthcare", "Finance"],
            portfolio=[
                {
                    "name": "Project A",
                    "client_industry": "Technology",
                    "description": "AI implementation",
                    "key_outcomes": "50% efficiency gain"
                },
                {
                    "name": "Project B",
                    "client_industry": "Finance",
                    "description": "Cloud migration",
                    "key_outcomes": "Reduced costs by 30%"
                },
                {
                    "name": "Project C",
                    "client_industry": "Healthcare",
                    "description": "Data analytics platform",
                    "key_outcomes": "Improved patient outcomes"
                },
                {
                    "name": "Project D",
                    "client_industry": "Retail",
                    "description": "E-commerce optimization",
                    "key_outcomes": "Increased sales by 25%"
                },
                {
                    "name": "Project E",
                    "client_industry": "Manufacturing",
                    "description": "Supply chain automation",
                    "key_outcomes": "Reduced delays by 40%"
                }
            ]
        )
        assert len(profile.portfolio) == 5
        assert profile.portfolio[0].name == "Project A"
        assert len(profile.industries_served) == 3

    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(
                company_description="Test",
                industries_served=["Tech"],
                portfolio=[
                    {
                        "name": "Project 1",
                        "client_industry": "Technology",
                        "description": "A test project",
                        "key_outcomes": "Test results"
                    },
                    {
                        "name": "Project 2",
                        "client_industry": "Healthcare",
                        "description": "Another test project",
                        "key_outcomes": "More test results"
                    },
                    {
                        "name": "Project 3",
                        "client_industry": "Finance",
                        "description": "Third test project",
                        "key_outcomes": "Additional test results"
                    },
                    {
                        "name": "Project 4",
                        "client_industry": "Retail",
                        "description": "Fourth test project",
                        "key_outcomes": "Further test results"
                    },
                    {
                        "name": "Project 5",
                        "client_industry": "Manufacturing",
                        "description": "Fifth test project",
                        "key_outcomes": "Final test results"
                    }
                ]
            )
        assert "company_name" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserProfile(
                company_name="Test",
                industries_served=["Tech"],
                portfolio=[
                    {
                        "name": "Project 1",
                        "client_industry": "Technology",
                        "description": "A test project",
                        "key_outcomes": "Test results"
                    },
                    {
                        "name": "Project 2",
                        "client_industry": "Healthcare",
                        "description": "Another test project",
                        "key_outcomes": "More test results"
                    },
                    {
                        "name": "Project 3",
                        "client_industry": "Finance",
                        "description": "Third test project",
                        "key_outcomes": "Additional test results"
                    },
                    {
                        "name": "Project 4",
                        "client_industry": "Retail",
                        "description": "Fourth test project",
                        "key_outcomes": "Further test results"
                    },
                    {
                        "name": "Project 5",
                        "client_industry": "Manufacturing",
                        "description": "Fifth test project",
                        "key_outcomes": "Final test results"
                    }
                ]
            )
        assert "company_description" in str(exc_info.value)

    def test_empty_industries_served(self):
        """Test profile with empty industries list."""
        profile = UserProfile(
            company_name="Test",
            company_description="Test",
            industries_served=[],
            portfolio=[
                {
                    "name": "Project 1",
                    "client_industry": "Technology",
                    "description": "A test project",
                    "key_outcomes": "Test results"
                },
                {
                    "name": "Project 2",
                    "client_industry": "Healthcare",
                    "description": "Another test project",
                    "key_outcomes": "More test results"
                },
                {
                    "name": "Project 3",
                    "client_industry": "Finance",
                    "description": "Third test project",
                    "key_outcomes": "Additional test results"
                },
                {
                    "name": "Project 4",
                    "client_industry": "Retail",
                    "description": "Fourth test project",
                    "key_outcomes": "Further test results"
                },
                {
                    "name": "Project 5",
                    "client_industry": "Manufacturing",
                    "description": "Fifth test project",
                    "key_outcomes": "Final test results"
                }
            ]
        )
        assert profile.industries_served == []
        assert len(profile.portfolio) == 5

    def test_portfolio_structure(self):
        """Test portfolio items have expected structure."""
        profile = UserProfile(
            company_name="Test",
            company_description="Test",
            industries_served=["Tech"],
            portfolio=[
                {
                    "name": "Test Project",
                    "client_industry": "Technology",
                    "description": "Test description",
                    "key_outcomes": "Test results"
                },
                {
                    "name": "Test Project 2",
                    "client_industry": "Healthcare",
                    "description": "Test description 2",
                    "key_outcomes": "Test results 2"
                },
                {
                    "name": "Test Project 3",
                    "client_industry": "Finance",
                    "description": "Test description 3",
                    "key_outcomes": "Test results 3"
                },
                {
                    "name": "Test Project 4",
                    "client_industry": "Retail",
                    "description": "Test description 4",
                    "key_outcomes": "Test results 4"
                },
                {
                    "name": "Test Project 5",
                    "client_industry": "Manufacturing",
                    "description": "Test description 5",
                    "key_outcomes": "Test results 5"
                }
            ]
        )
        # Portfolio items are Pydantic models, not dicts
        from backend.src.schemas.user_profile import PortfolioItem
        assert isinstance(profile.portfolio[0], PortfolioItem)
        assert profile.portfolio[0].name == "Test Project"
        assert profile.portfolio[0].client_industry == "Technology"
        assert profile.portfolio[0].description == "Test description"
        assert profile.portfolio[0].key_outcomes == "Test results"