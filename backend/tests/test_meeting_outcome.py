"""Tests for meeting outcome API."""

import pytest
from pydantic import ValidationError
from unittest.mock import AsyncMock, Mock, patch
from backend.src.schemas.meeting_outcome import MeetingOutcomeCreate, MeetingStatus, MeetingOutcomeValue
from backend.src.services.supabase_service import SupabaseService


class TestMeetingOutcomeSchema:
    """Test MeetingOutcome schema validation."""

    def test_valid_outcome_create(self):
        """Test creating a valid meeting outcome."""
        outcome_data = {
            "meeting_status": "completed",
            "outcome": "successful",
            "prep_accuracy": 5,
            "most_useful_section": "talking_points",
            "what_was_missing": "More info about competitors",
            "general_notes": "Great meeting overall"
        }

        outcome = MeetingOutcomeCreate(**outcome_data)
        assert outcome.meeting_status == MeetingStatus.COMPLETED
        assert outcome.outcome == MeetingOutcomeValue.SUCCESSFUL
        assert outcome.prep_accuracy == 5

    def test_minimal_outcome_create(self):
        """Test creating a minimal meeting outcome."""
        outcome_data = {
            "meeting_status": "completed"
        }

        outcome = MeetingOutcomeCreate(**outcome_data)
        assert outcome.meeting_status == MeetingStatus.COMPLETED
        assert outcome.outcome is None
        assert outcome.prep_accuracy is None

    def test_outcome_validation_failures(self):
        """Test validation failures."""
        # Test invalid prep_accuracy (too high)
        with pytest.raises(ValidationError):
            MeetingOutcomeCreate(
                meeting_status="completed",
                prep_accuracy=10  # Should be 1-5
            )

        # Test invalid meeting_status
        with pytest.raises(ValidationError):
            MeetingOutcomeCreate(
                meeting_status="invalid_status"
            )


class TestMeetingOutcomeService:
    """Test MeetingOutcome service methods."""

    @pytest.mark.asyncio
    async def test_save_meeting_outcome_creates_new(self, mock_supabase_client):
        """Test saving a new meeting outcome."""
        # Mock the select query for checking existing outcome (returns empty)
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(data=[])

        # Mock the insert response
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = Mock(data=[{"id": "test-outcome-id"}])

        service = SupabaseService(mock_supabase_client)

        outcome_id = await service.save_meeting_outcome(
            prep_id="test-prep-id",
            outcome_data={
                "meeting_status": "completed",
                "outcome": "successful"
            }
        )

        assert outcome_id == "test-outcome-id"

    @pytest.mark.asyncio
    async def test_get_meeting_outcome(self, mock_supabase_client):
        """Test retrieving a meeting outcome."""
        # Mock the select query
        mock_response = Mock(data=[{
            "id": "test-outcome-id",
            "prep_id": "test-prep-id",
            "meeting_status": "completed",
            "outcome": "successful"
        }])
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = mock_response

        service = SupabaseService(mock_supabase_client)

        outcome = await service.get_meeting_outcome("test-prep-id")

        assert outcome is not None
        assert outcome["id"] == "test-outcome-id"
        assert outcome["meeting_status"] == "completed"


