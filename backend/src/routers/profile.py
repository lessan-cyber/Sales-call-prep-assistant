from fastapi import APIRouter, Depends, HTTPException, status
from gotrue import User
from supabase import AsyncClient

from ..dependencies import get_current_user, get_supabase_client
from ..schemas.user_profile import UserProfile

router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user: User = Depends(get_current_user),
    supabase: AsyncClient = Depends(get_supabase_client),
):
    """Fetches the profile for the currently authenticated user."""
    response = (
        await supabase.table("user_profiles")
        .select("company_name, company_description, industries_served, portfolio")
        .eq("id", current_user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return response.data[0]


@router.post("/profile", response_model=UserProfile)
async def upsert_profile(
    profile_data: UserProfile,
    current_user: User = Depends(get_current_user),
    supabase: AsyncClient = Depends(get_supabase_client),
):
    """Creates or updates a user's profile."""
    profile_dict = profile_data.model_dump()
    profile_dict["id"] = str(current_user.id)

    response = (
        await supabase.table("user_profiles")
        .upsert(profile_dict, on_conflict="id", returning="representation")
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile",
        )
    # The upsert operation returns a list, so we select the first item.
    return response.data[0]
