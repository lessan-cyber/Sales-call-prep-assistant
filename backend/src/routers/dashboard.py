"""Router for dashboard data and statistics."""

from typing import Optional

from fastapi import APIRouter, Depends, status
from supabase_auth.types import User

from supabase import AsyncClient

from ..dependencies import get_current_user, get_supabase_client
from ..services.supabase_service import get_supabase_service
from ..utils.logger import info

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

    # Fetch fresh data from database using the optimized aggregated query
    supabase_service = get_supabase_service()

    try:
        # Use aggregated query (60-75% faster than 5 separate queries)
        info(f"Fetching aggregated dashboard data for user {user_id}")
        dashboard_data = await supabase_service.get_dashboard_aggregated(user_id)

        info(f"✓ Dashboard data fetched for user {user_id}")
        return dashboard_data

    except Exception as e:
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
            search=search,
        )

        # Get total count for pagination
        total_count = await supabase_service.get_user_preps_count(
            user_id=user_id, status_filter=status_filter, search=search
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
                "has_prev": has_prev,
            },
        }

    except Exception as e:
        error(f"Error fetching user preps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch preps.",
        )
