"""Pytest configuration and shared fixtures."""

from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    client = AsyncMock()
    client.table = Mock(return_value=client)
    client.select = Mock(return_value=client)
    client.insert = Mock(return_value=client)
    client.update = Mock(return_value=client)
    client.upsert = Mock(return_value=client)
    client.delete = Mock(return_value=client)
    client.eq = Mock(return_value=client)
    client.limit = Mock(return_value=client)
    client.execute = AsyncMock()
    return client


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    user = Mock()
    user.id = "test-user-id-123"
    user.email = "test@example.com"
    return user


@pytest.fixture
def sample_user_profile() -> dict[str, Any]:
    """Sample user profile data."""
    return {
        "id": "test-user-id-123",
        "company_name": "Test Consulting LLC",
        "company_description": "A consulting firm specializing in AI solutions",
        "industries_served": ["Technology", "Healthcare", "Finance"],
        "portfolio": [
            {
                "name": "AI Chatbot Implementation",
                "client_industry": "Technology",
                "description": "Deployed enterprise chatbot solution",
                "key_outcomes": "Reduced customer support costs by 40%",
            },
            {
                "name": "Cloud Migration Project",
                "client_industry": "Finance",
                "description": "Migrated legacy systems to AWS cloud infrastructure",
                "key_outcomes": "Reduced infrastructure costs by 35% and improved uptime to 99.9%",
            },
            {
                "name": "Data Analytics Platform",
                "client_industry": "Healthcare",
                "description": "Built real-time analytics platform for patient data",
                "key_outcomes": "Enabled data-driven decisions affecting 50,000+ patients",
            },
            {
                "name": "E-commerce Modernization",
                "client_industry": "Retail",
                "description": "Redesigned online shopping experience with ML recommendations",
                "key_outcomes": "Increased conversion rate by 28% and customer retention by 15%",
            },
            {
                "name": "Cybersecurity Audit",
                "client_industry": "Technology",
                "description": "Comprehensive security assessment and remediation",
                "key_outcomes": "Identified and fixed 47 critical vulnerabilities",
            },
        ],
    }


@pytest.fixture
def sample_prep_request() -> dict[str, Any]:
    """Sample prep request data."""
    return {
        "company_name": "Acme Corp",
        "meeting_objective": "Discuss AI implementation for customer service",
        "contact_person_name": "John Doe",
        "contact_linkedin_url": "https://linkedin.com/in/johndoe",
        "meeting_date": "2024-01-15",
    }


@pytest.fixture
def sample_research_data() -> dict[str, Any]:
    """Sample research data from Agent A."""
    return {
        "company_intelligence": {
            "name": "Acme Corp",
            "industry": "Technology",
            "size": "500-1000 employees",
            "description": "Leading provider of enterprise software solutions",
            "recent_news": ["Acquired startup X", "Launched new product Y"],
            "strategic_initiatives": ["Digital transformation", "Cloud migration"],
        },
        "decision_makers": [
            {
                "name": "John Doe",
                "title": "VP of Engineering",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "background": "15 years in tech leadership",
                "recent_activity": "Posted about AI adoption",
            }
        ],
        "research_limitations": [],
        "overall_confidence": 0.85,
        "sources_used": ["company website", "LinkedIn", "news articles"],
    }


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("backend.src.config.settings") as mock:
        mock.SUPABASE_URL = "https://test.supabase.co"
        mock.SUPABASE_ANON_KEY = "test-anon-key"
        mock.SUPABASE_SERVICE_KEY = "test-service-key"
        mock.GOOGLE_API_KEY = "test-google-key"
        mock.SERP_API_KEY = "test-serp-key"
        mock.FIRECRAWL_API_KEY = "test-firecrawl-key"
        mock.APIFY_API_KEY = "test-apify-key"
        mock.GEMINI_MODEL = "gemini-2.5-flash"
        yield mock
