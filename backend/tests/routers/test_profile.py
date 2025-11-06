"""Tests for profile router."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException, status
from backend.src.routers.profile import get_profile, upsert_profile
from backend.src.schemas.user_profile import UserProfile


class TestProfileRouter:
    """Test profile router endpoints."""

    @pytest.mark.asyncio
    async def test_get_profile_success(self, mock_user, mock_supabase_client, sample_user_profile):
        """Test successful profile retrieval."""
        mock_supabase_client.execute.return_value = Mock(data=[sample_user_profile])

        result = await get_profile(
            current_user=mock_user,
            supabase=mock_supabase_client
        )

        assert result["company_name"] == "Test Consulting LLC"
        assert result["id"] == "test-user-id-123"
        mock_supabase_client.table.assert_called_once_with("user_profiles")
        mock_supabase_client.eq.assert_called_once_with("id", mock_user.id)

    @pytest.mark.asyncio
    async def test_get_profile_not_found(self, mock_user, mock_supabase_client):
        """Test profile not found error."""
        mock_supabase_client.execute.return_value = Mock(data=[])

        with pytest.raises(HTTPException) as exc_info:
            await get_profile(
                current_user=mock_user,
                supabase=mock_supabase_client
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Profile not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_upsert_profile_create(self, mock_user, mock_supabase_client):
        """Test creating a new profile."""
        profile_data = UserProfile(
            company_name="New Company",
            company_description="A new consulting firm",
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

        created_profile = profile_data.model_dump()
        created_profile["id"] = mock_user.id
        mock_supabase_client.execute.return_value = Mock(data=[created_profile])

        result = await upsert_profile(
            profile_data=profile_data,
            current_user=mock_user,
            supabase=mock_supabase_client
        )

        assert result["company_name"] == "New Company"
        assert result["id"] == mock_user.id
        mock_supabase_client.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_profile_update(self, mock_user, mock_supabase_client):
        """Test updating an existing profile."""
        profile_data = UserProfile(
            company_name="Updated Company",
            company_description="Updated description",
            industries_served=["Tech", "Healthcare"],
            portfolio=[
                {
                    "name": "New Project",
                    "client_industry": "Technology",
                    "description": "Latest work",
                    "key_outcomes": "Great success"
                },
                {
                    "name": "Project 2",
                    "client_industry": "Healthcare",
                    "description": "Another project",
                    "key_outcomes": "Good results"
                },
                {
                    "name": "Project 3",
                    "client_industry": "Finance",
                    "description": "Third project",
                    "key_outcomes": "Excellent outcomes"
                },
                {
                    "name": "Project 4",
                    "client_industry": "Retail",
                    "description": "Fourth project",
                    "key_outcomes": "Strong performance"
                },
                {
                    "name": "Project 5",
                    "client_industry": "Manufacturing",
                    "description": "Fifth project",
                    "key_outcomes": "Outstanding success"
                }
            ]
        )

        updated_profile = profile_data.model_dump()
        updated_profile["id"] = mock_user.id
        mock_supabase_client.execute.return_value = Mock(data=[updated_profile])

        result = await upsert_profile(
            profile_data=profile_data,
            current_user=mock_user,
            supabase=mock_supabase_client
        )

        assert result["company_name"] == "Updated Company"
        assert len(result["portfolio"]) == 5
        mock_supabase_client.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_profile_error(self, mock_user, mock_supabase_client):
        """Test error handling during profile upsert."""
        profile_data = UserProfile(
            company_name="Test",
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

        mock_supabase_client.execute.return_value = Mock(data=[])

        with pytest.raises(HTTPException) as exc_info:
            await upsert_profile(
                profile_data=profile_data,
                current_user=mock_user,
                supabase=mock_supabase_client
            )

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Error updating profile" in exc_info.value.detail