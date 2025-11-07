"""Router for dashboard data and statistics."""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from supabase_auth.types import User
from supabase import AsyncClient

from ..dependencies import get_current_user, get_supabase_client
from ..services.supabase_service import get_supabase_service
from ..utils.logger import info, error

router = APIRouter()


@router.get("/dashboard", status_code=status.HTTP_200_OK)
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    supabase: AsyncClient = Depends(get_supabase_client),
):
    """
    Get dashboard data and statistics for the current user.

    Returns:
        Dashboard stats including total preps, success rate, avg confidence, etc.
    """
    from ..services.supabase_service import get_supabase_service

    user_id = str(current_user.id)
    info(f"Fetching dashboard data for user: {user_id}")

    supabase_service = get_supabase_service()

    try:
        # Get total preps count
        total_preps = await supabase_service.get_total_preps_count(user_id)

        # Get success rate and other metrics
        success_metrics = await supabase_service.get_success_metrics(user_id)

        # Get recent preps (last 10)
        recent_preps = await supabase_service.get_recent_preps(user_id, limit=10)

        # Get upcoming meetings (next 7 days)
        upcoming_meetings = await supabase_service.get_upcoming_meetings(user_id, days_ahead=7)

        # Calculate time saved (18 minutes per prep on average)
        time_saved_minutes = total_preps * 18
        time_saved_hours = round(time_saved_minutes / 60, 1)

        # Build response
        dashboard_data = {
            "total_preps": total_preps,
            "success_rate": success_metrics["success_rate"],
            "total_successful": success_metrics["total_successful"],
            "total_completed": success_metrics["total_completed"],
            "avg_confidence": success_metrics["avg_confidence"],
            "time_saved_hours": time_saved_hours,
            "time_saved_minutes": time_saved_minutes,
            "recent_preps": recent_preps,
            "upcoming_meetings": upcoming_meetings,
        }

        info(f"✓ Dashboard data fetched for user {user_id}")
        return dashboard_data

    except Exception as e:
        error(f"Error fetching dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard data.",
        )


@router.get("/preps", status_code=status.HTTP_200_OK)
async def get_user_preps(
    page: int = 1,
    limit: int = 10,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    supabase: AsyncClient = Depends(get_supabase_client),
):
    """
    Get paginated list of user's preps for dashboard table.

    Args:
        page: Page number (1-indexed)
        limit: Number of items per page
        status_filter: Filter by status (all, pending, completed)
        search: Search by company name
        current_user: Authenticated user
        supabase: Supabase client

    Returns:
        Paginated list of preps with metadata
    """
    from ..services.supabase_service import get_supabase_service

    user_id = str(current_user.id)
    info(f"Fetching preps for user {user_id}, page {page}, limit {limit}")

    supabase_service = get_supabase_service()

    try:
        # Calculate offset
        offset = (page - 1) * limit

        # Get preps with filters
        preps_data = await supabase_service.get_user_preps_paginated(
            user_id=user_id,
            limit=limit,
            offset=offset,
            status_filter=status_filter,
            search=search
        )

        # Get total count for pagination
        total_count = await supabase_service.get_user_preps_count(
            user_id=user_id,
            status_filter=status_filter,
            search=search
        )

        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1

        info(f"✓ Fetched {len(preps_data)} preps for user {user_id}")

        return {
            "preps": preps_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }

    except Exception as e:
        error(f"Error fetching user preps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch preps.",
        )
