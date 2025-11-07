"""Router for sales prep generation using two-agent system."""

import re
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from supabase_auth.types import User

from supabase import AsyncClient

from ..agents import research_orchestrator, sales_brief_synthesizer
from ..dependencies import get_current_user, get_supabase_client
from ..schemas.prep_report import PrepRequest
from ..services.cache_service import CacheService
from ..services.supabase_service import SupabaseService, get_supabase_service
from ..utils.logger import error, info
from ..utils.normalise import normalize_company_name

router = APIRouter()


@router.post("/preps", status_code=status.HTTP_200_OK)
async def create_prep(
    prep_request: PrepRequest,
    current_user: User = Depends(get_current_user),
    supabase: AsyncClient = Depends(get_supabase_client),
):
    """
    Create a new sales prep report using the two-agent system.
    Args:
        prep_request: Sales prep request with company and meeting details
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        Generated prep report with ID
    """
    info(
        f"Received prep request for company: {prep_request.company_name} "
        f"with objective: {prep_request.meeting_objective} "
        f"by user: {current_user.id}"
    )

    normalized_company_name = normalize_company_name(prep_request.company_name)

    # Initialize services
    cache_service = CacheService(supabase)
    supabase_service = get_supabase_service()

    # Step 1: Check cache
    info(f"Checking cache for {normalized_company_name}")
    cached_data = await cache_service.get_cached_company_data(normalized_company_name)

    research_data = {}
    cache_hit = False

    if cached_data and cached_data.get("cache_status") == "fresh":
        # Cache hit - use cached data
        info(f"✓ Cache hit for {normalized_company_name}. Using cached data.")
        research_data = cached_data["company_data"]
        cache_hit = True
    else:
        # Cache miss or stale - run Agent A
        info(
            f"Cache miss or stale for {normalized_company_name}. Running Agent A (Research Orchestrator)."
        )

        try:
            # Agent A: Research Orchestrator
            research_result = await research_orchestrator.research_company(
                company_name=prep_request.company_name,
                meeting_objective=prep_request.meeting_objective,
                contact_person_name=prep_request.contact_person_name,
                contact_linkedin_url=prep_request.contact_linkedin_url,
            )

            if not research_result["success"]:
                error(f"Agent A failed for {normalized_company_name}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Research failed: {research_result.get('error', 'Unknown error')}",
                )

            research_data = research_result["research_data"]

            # Cache the research data for future use
            if research_data:
                source_urls = research_result.get("sources_used", [])
                confidence_score = research_result.get("confidence_score", 0.5)

                await cache_service.cache_company_data(
                    normalized_company_name=normalized_company_name,
                    company_data=research_data,
                    confidence_score=confidence_score,
                    source_urls=source_urls,
                )

        except Exception as e:
            error(f"Error during research phase: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Research error: {str(e)}",
            )

    # Step 2: Get user profile
    info(f"Fetching user profile for user {current_user.id}")
    user_profile = await supabase_service.get_user_profile(str(current_user.id))

    if not user_profile:
        error(f"User profile not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please complete your profile before creating preps.",
        )

    # Step 3: Agent B - Sales Brief Synthesizer
    info("Running Agent B (Sales Brief Synthesizer)")
    try:
        prep_report = await sales_brief_synthesizer.synthesize_sales_brief(
            research_data=research_data,
            user_profile=user_profile,
            user_id=str(current_user.id),
            meeting_objective=prep_request.meeting_objective,
        )

        info(
            f"✓ Sales brief synthesized successfully with confidence: {prep_report.overall_confidence}"
        )

    except Exception as e:
        error(f"Error during synthesis phase: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Synthesis error: {str(e)}",
        )

    # Step 4: Save to database
    try:
        prep_id = await supabase_service.save_meeting_prep(
            user_id=str(current_user.id),
            company_name=prep_request.company_name,
            normalized_company_name=normalized_company_name,
            meeting_objective=prep_request.meeting_objective,
            meeting_date=prep_request.meeting_date,
            contact_person_name=prep_request.contact_person_name,
            contact_linkedin_url=prep_request.contact_linkedin_url,
            prep_data=prep_report.model_dump(),
            overall_confidence=prep_report.overall_confidence,
            cache_hit=cache_hit,
        )

        if not prep_id:
            raise Exception("Failed to save prep to database")

        info(f"✓ Prep report saved successfully with ID: {prep_id}")

        return {
            "message": "Prep report generated and saved successfully",
            "prep_id": prep_id,
            "report": prep_report.model_dump(),
            "cache_hit": cache_hit,
        }

    except Exception as e:
        error(f"Error saving prep to database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


@router.get("/preps/{prep_id}", status_code=status.HTTP_200_OK)
async def get_prep_report(
    prep_id: str,
    current_user: User = Depends(get_current_user),
    supabase: AsyncClient = Depends(get_supabase_client),
):
    """
    Retrieve a saved sales prep report by ID.

    Args:
        prep_id: UUID of the prep report
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        The prep report
    """
    from ..schemas.prep_report import PrepReport

    info(
        f"Received request to fetch prep report with ID: {prep_id} "
        f"by user: {current_user.id}"
    )

    supabase_service = get_supabase_service()
    prep_data = await supabase_service.get_meeting_prep(prep_id, str(current_user.id))

    if not prep_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prep report not found or not authorized.",
        )

    try:
        # Check if prep_data is already a dict or needs JSON parsing
        prep_data_value = prep_data["prep_data"]
        if isinstance(prep_data_value, str):
            # It's a JSON string, parse it
            prep_report = PrepReport.model_validate_json(prep_data_value)
        else:
            # It's already a dict, validate directly
            prep_report = PrepReport.model_validate(prep_data_value)

        return prep_report
    except Exception as e:
        error(f"Error parsing prep_data from database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing report data.",
        )


@router.post("/preps/{prep_id}/outcome", status_code=status.HTTP_201_CREATED)
async def record_meeting_outcome(
    prep_id: str,
    outcome_data: dict,
    current_user: User = Depends(get_current_user),
    supabase: AsyncClient = Depends(get_supabase_client),
):
    """
    Record or update a meeting outcome for a prep.

    Args:
        prep_id: UUID of the prep
        outcome_data: Meeting outcome data
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        Success message with outcome ID
    """
    from ..schemas.meeting_outcome import MeetingOutcomeCreate
    from ..services.supabase_service import get_supabase_service

    info(
        f"Recording meeting outcome for prep ID: {prep_id} "
        f"by user: {current_user.id}"
    )

    # Verify the prep belongs to the current user
    supabase_service = get_supabase_service()
    prep_data = await supabase_service.get_meeting_prep(prep_id, str(current_user.id))

    if not prep_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prep not found or not authorized.",
        )

    # Validate the outcome data
    try:
        validated_outcome = MeetingOutcomeCreate(**outcome_data)
    except Exception as e:
        error(f"Invalid outcome data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid outcome data: {str(e)}",
        )

    # Save the outcome
    outcome_id = await supabase_service.save_meeting_outcome(
        prep_id=prep_id,
        outcome_data=validated_outcome.model_dump(exclude_unset=True)
    )

    if not outcome_id:
        error(f"Failed to save meeting outcome for prep {prep_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save meeting outcome.",
        )

    info(f"✓ Meeting outcome saved with ID: {outcome_id}")

    return {
        "message": "Meeting outcome recorded successfully",
        "outcome_id": outcome_id
    }


@router.get("/preps/{prep_id}/outcome", status_code=status.HTTP_200_OK)
async def get_meeting_outcome(
    prep_id: str,
    current_user: User = Depends(get_current_user),
    supabase: AsyncClient = Depends(get_supabase_client),
):
    """
    Retrieve a meeting outcome for a prep.

    Args:
        prep_id: UUID of the prep
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        The meeting outcome
    """
    from ..services.supabase_service import get_supabase_service

    info(
        f"Fetching meeting outcome for prep ID: {prep_id} "
        f"by user: {current_user.id}"
    )

    # Verify the prep belongs to the current user
    supabase_service = get_supabase_service()
    prep_data = await supabase_service.get_meeting_prep(prep_id, str(current_user.id))

    if not prep_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prep not found or not authorized.",
        )

    # Get the outcome
    outcome = await supabase_service.get_meeting_outcome(prep_id)

    return outcome
