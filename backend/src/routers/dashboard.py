"""Router for dashboard data and statistics."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import AsyncClient
from supabase_auth.types import User

from ..dependencies import get_current_user, get_supabase_client
from ..services.supabase_service import get_supabase_service
from ..utils.logger import error, info

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
    user_id = str(current_user.id)
    info(f"Fetching dashboard data for user: {user_id}")

    supabase_service = get_supabase_service()

    try:
        info(f"Fetching aggregated dashboard data for user {user_id}")
        dashboard_data = await supabase_service.get_dashboard_aggregated(user_id)

        info(f"✓ Dashboard data fetched for user {user_id}")
        return dashboard_data

    except Exception:
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
    user_id = str(current_user.id)
    info(f"Fetching preps for user {user_id}, page {page}, limit {limit}")

    supabase_service = get_supabase_service()

    try:
        offset = (page - 1) * limit

        preps_data = await supabase_service.get_user_preps_paginated(
            user_id=user_id,
            limit=limit,
            offset=offset,
            status_filter=status_filter,
            search=search,
        )

        total_count = await supabase_service.get_user_preps_count(
            user_id=user_id, status_filter=status_filter, search=search
        )

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

    except Exception:
        error(f"Error fetching user preps")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch preps.",
        )
