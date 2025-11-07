"""Supabase service for database operations."""
from typing import Optional, Dict, Any, List
from supabase import AsyncClient
from supabase_auth.types import User
from ..utils.logger import info, error


class SupabaseService:
    """Service for database operations."""

    def __init__(self, supabase: AsyncClient):
        """Initialize with Supabase client."""
        self.supabase = supabase

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile from database.

        Args:
            user_id: UUID of the user

        Returns:
            User profile data or None if not found
        """
        try:
            response = (
                await self.supabase.table("user_profiles")
                .select("company_name, company_description, industries_served, portfolio")
                .eq("id", user_id)
                .execute()
            )

            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            error(f"Error retrieving user profile: {e}")
            return None

    async def save_meeting_prep(
        self,
        user_id: str,
        company_name: str,
        normalized_company_name: str,
        meeting_objective: str,
        meeting_date: Optional[str],
        contact_person_name: Optional[str],
        contact_linkedin_url: Optional[str],
        prep_data: Dict[str, Any],
        overall_confidence: float,
        cache_hit: bool
    ) -> Optional[str]:
        """
        Save a meeting prep to the database.

        Args:
            user_id: UUID of the user
            company_name: Company name
            normalized_company_name: Normalized company name
            meeting_objective: Meeting objective
            meeting_date: Optional meeting date
            contact_person_name: Optional contact person name
            contact_linkedin_url: Optional contact LinkedIn URL
            prep_data: Generated prep data
            overall_confidence: Overall confidence score
            cache_hit: Whether this was a cache hit

        Returns:
            ID of the saved prep or None if error
        """
        try:
            prep_record = {
                "user_id": user_id,
                "company_name": company_name,
                "company_name_normalized": normalized_company_name,
                "meeting_objective": meeting_objective,
                "meeting_date": meeting_date,
                "contact_person_name": contact_person_name,
                "contact_linkedin_url": contact_linkedin_url,
                "prep_data": prep_data,
                "overall_confidence": max(0.0, min(1.0, overall_confidence)),
                "cache_hit": cache_hit
            }

            response = await self.supabase.table("meeting_preps").insert(prep_record).execute()

            if response.data:
                prep_id = response.data[0]["id"]
                info(f"Saved meeting prep with ID: {prep_id}")
                return prep_id

            return None

        except Exception as e:
            error(f"Error saving meeting prep: {e}")
            return None

    async def get_meeting_prep(self, prep_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a meeting prep by ID.

        Args:
            prep_id: UUID of the prep
            user_id: UUID of the user (for authorization)

        Returns:
            Prep data or None if not found
        """
        try:
            response = (
                await self.supabase.table("meeting_preps")
                .select("*")
                .eq("id", prep_id)
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )

            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            error(f"Error retrieving meeting prep: {e}")
            return None

    async def search_portfolio_projects(
        self,
        user_id: str,
        search_query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search through user's portfolio projects for relevance.
        Note: This is a simple text search. For vector similarity, implement embeddings.

        Args:
            user_id: UUID of the user
            search_query: Query to match against portfolio
            limit: Maximum number of results

        Returns:
            List of matching projects with relevance scores
        """
        try:
            # Get user's portfolio
            response = (
                await self.supabase.table("user_profiles")
                .select("portfolio")
                .eq("id", user_id)
                .execute()
            )

            if not response.data or not response.data[0].get("portfolio"):
                return []

            portfolio = response.data[0]["portfolio"]
            matches = []

            # Simple text-based matching (upgrade to vector search for better results)
            for i, project in enumerate(portfolio):
                relevance_score = self._calculate_relevance(search_query, project)
                if relevance_score > 0.3:  # Threshold for relevance
                    matches.append({
                        "index": i,
                        "project": project,
                        "relevance_score": relevance_score
                    })

            # Sort by relevance score
            matches.sort(key=lambda x: x["relevance_score"], reverse=True)

            return matches[:limit]

        except Exception as e:
            error(f"Error searching portfolio: {e}")
            return []

    def _calculate_relevance(self, query: str, project: Dict[str, Any]) -> float:
        """
        Calculate relevance score between query and project.
        Simple implementation using text matching.

        Args:
            query: Search query
            project: Portfolio project

        Returns:
            Relevance score (0.0 to 1.0)
        """
        # Combine project fields for comparison
        project_text = " ".join([
            str(project.get("name", "")),
            str(project.get("client_industry", "")),
            str(project.get("description", "")),
            str(project.get("key_outcomes", ""))
        ]).lower()

        query_terms = query.lower().split()
        matches = sum(1 for term in query_terms if term in project_text)

        # Simple score: matches / total query terms
        return matches / len(query_terms) if query_terms else 0.0

    async def save_meeting_outcome(
        self,
        prep_id: str,
        outcome_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Save or update a meeting outcome.

        Args:
            prep_id: UUID of the prep
            outcome_data: Meeting outcome data

        Returns:
            ID of the saved outcome or None if error
        """
        try:
            # Check if outcome already exists
            existing_response = (
                await self.supabase.table("meeting_outcomes")
                .select("id")
                .eq("prep_id", prep_id)
                .execute()
            )

            if existing_response.data:
                # Update existing outcome
                response = (
                    await self.supabase.table("meeting_outcomes")
                    .update({
                        **outcome_data,
                        "updated_at": "NOW()"
                    })
                    .eq("prep_id", prep_id)
                    .execute()
                )
                info(f"Updated meeting outcome for prep {prep_id}")
            else:
                # Create new outcome
                outcome_record = {
                    "prep_id": prep_id,
                    **outcome_data
                }
                response = await self.supabase.table("meeting_outcomes").insert(outcome_record).execute()
                info(f"Created meeting outcome for prep {prep_id}")

            if response.data:
                return response.data[0]["id"]

            return None

        except Exception as e:
            error(f"Error saving meeting outcome: {e}")
            return None

    async def get_meeting_outcome(self, prep_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a meeting outcome by prep ID.

        Args:
            prep_id: UUID of the prep

        Returns:
            Meeting outcome data or None if not found
        """
        try:
            response = (
                await self.supabase.table("meeting_outcomes")
                .select("*")
                .eq("prep_id", prep_id)
                .limit(1)
                .execute()
            )

            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            error(f"Error retrieving meeting outcome: {e}")
            return None

    async def get_user_meeting_outcomes(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all meeting outcomes for a user.

        Args:
            user_id: UUID of the user
            limit: Maximum number of outcomes to return

        Returns:
            List of meeting outcomes with prep data
        """
        try:
            response = (
                await self.supabase.table("meeting_outcomes")
                .select("""
                    *,
                    meeting_preps:prep_id (
                        id,
                        company_name,
                        meeting_objective,
                        meeting_date,
                        created_at,
                        overall_confidence
                    )
                """)
                .eq("meeting_preps.user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return response.data if response.data else []

        except Exception as e:
            error(f"Error retrieving meeting outcomes: {e}")
            return []

    async def get_total_preps_count(self, user_id: str) -> int:
        """
        Get total count of preps for a user.

        Args:
            user_id: UUID of the user

        Returns:
            Total count of preps
        """
        try:
            response = (
                await self.supabase.table("meeting_preps")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .execute()
            )

            return response.count if response.count else 0

        except Exception as e:
            error(f"Error counting preps: {e}")
            return 0

    async def get_success_metrics(self, user_id: str) -> Dict[str, Any]:
        """
        Get success rate and confidence metrics for a user.

        Args:
            user_id: UUID of the user

        Returns:
            Dictionary with success metrics
        """
        try:
            # Get all preps with their confidence scores
            preps_response = (
                await self.supabase.table("meeting_preps")
                .select("overall_confidence")
                .eq("user_id", user_id)
                .execute()
            )

            if not preps_response.data:
                return {
                    "success_rate": 0.0,
                    "total_successful": 0,
                    "total_completed": 0,
                    "avg_confidence": 0.0
                }

            # Calculate average confidence
            total_confidence = sum(prep["overall_confidence"] for prep in preps_response.data)
            avg_confidence = total_confidence / len(preps_response.data)

            # Get outcomes to calculate success rate
            outcomes_response = (
                await self.supabase.table("meeting_outcomes")
                .select("meeting_status, outcome")
                .execute()
            )

            if not outcomes_response.data:
                return {
                    "success_rate": 0.0,
                    "total_successful": 0,
                    "total_completed": 0,
                    "avg_confidence": round(avg_confidence, 2)
                }

            # Calculate success rate
            completed_count = sum(1 for o in outcomes_response.data if o["meeting_status"] == "completed")
            successful_count = sum(1 for o in outcomes_response.data if o["outcome"] == "successful")

            success_rate = (successful_count / completed_count * 100) if completed_count > 0 else 0.0

            return {
                "success_rate": round(success_rate, 1),
                "total_successful": successful_count,
                "total_completed": completed_count,
                "avg_confidence": round(avg_confidence, 2)
            }

        except Exception as e:
            error(f"Error calculating success metrics: {e}")
            return {
                "success_rate": 0.0,
                "total_successful": 0,
                "total_completed": 0,
                "avg_confidence": 0.0
            }

    async def get_recent_preps(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent preps for a user.

        Args:
            user_id: UUID of the user
            limit: Maximum number of preps to return

        Returns:
            List of recent preps with basic info
        """
        try:
            response = (
                await self.supabase.table("meeting_preps")
                .select("""
                    id,
                    company_name,
                    meeting_objective,
                    meeting_date,
                    created_at,
                    overall_confidence
                """)
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return response.data if response.data else []

        except Exception as e:
            error(f"Error retrieving recent preps: {e}")
            return []

    async def get_upcoming_meetings(
        self,
        user_id: str,
        days_ahead: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming meetings for a user.

        Args:
            user_id: UUID of the user
            days_ahead: Number of days to look ahead

        Returns:
            List of upcoming meetings
        """
        try:
            # Calculate date range
            today = datetime.now().strftime("%Y-%m-%d")
            future_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

            response = (
                await self.supabase.table("meeting_preps")
                .select("""
                    id,
                    company_name,
                    meeting_objective,
                    meeting_date
                """)
                .eq("user_id", user_id)
                .not_.is_("meeting_date", None)
                .gte("meeting_date", today)
                .lte("meeting_date", future_date)
                .order("meeting_date", desc=True)
                .execute()
            )

            return response.data if response.data else []

        except Exception as e:
            error(f"Error retrieving upcoming meetings: {e}")
            return []

    async def get_user_preps_paginated(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get paginated list of user's preps.

        Args:
            user_id: UUID of the user
            limit: Number of items to return
            offset: Number of items to skip
            status_filter: Filter by status (pending, completed, all)
            search: Search by company name

        Returns:
            List of preps with outcomes joined
        """
        try:
            # Build query
            query = self.supabase.table("meeting_preps").select("""
                id,
                company_name,
                meeting_objective,
                meeting_date,
                created_at,
                overall_confidence,
                meeting_outcomes:meeting_outcomes (
                    meeting_status,
                    outcome
                )
            """).eq("user_id", user_id)

            # Apply status filter
            if status_filter and status_filter != "all":
                # This is a simplified filter - in production you might want to use joins
                pass

            # Apply search
            if search:
                query = query.ilike("company_name", f"%{search}%")

            # Apply pagination and ordering
            response = (
                query
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return response.data if response.data else []

        except Exception as e:
            error(f"Error retrieving paginated preps: {e}")
            return []

    async def get_user_preps_count(
        self,
        user_id: str,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> int:
        """
        Get total count of user's preps for pagination.

        Args:
            user_id: UUID of the user
            status_filter: Filter by status
            search: Search by company name

        Returns:
            Total count
        """
        try:
            query = self.supabase.table("meeting_preps").select("id", count="exact").eq("user_id", user_id)

            if search:
                query = query.ilike("company_name", f"%{search}%")

            response = query.execute()
            return response.count if response.count else 0

        except Exception as e:
            error(f"Error counting user preps: {e}")
            return 0

    async def log_api_usage(
        self,
        user_id: Optional[str],
        prep_id: Optional[str],
        operation: str,
        provider: Optional[str],
        tokens_used: Optional[int],
        cost_usd: Optional[float],
        duration_ms: int,
        success: bool,
        error_message: Optional[str]
    ) -> bool:
        """
        Log API usage for monitoring.

        Args:
            user_id: UUID of the user
            prep_id: UUID of the prep
            operation: Type of operation
            provider: API provider
            tokens_used: Number of tokens used
            cost_usd: Cost in USD
            duration_ms: Duration in milliseconds
            success: Whether operation was successful
            error_message: Optional error message

        Returns:
            True if successful, False otherwise
        """
        try:
            log_entry = {
                "user_id": user_id,
                "prep_id": prep_id,
                "operation": operation,
                "provider": provider,
                "tokens_used": tokens_used,
                "cost_usd": cost_usd,
                "duration_ms": duration_ms,
                "success": success,
                "error_message": error_message
            }

            await self.supabase.table("api_usage_logs").insert(log_entry).execute()
            return True

        except Exception as e:
            error(f"Error logging API usage: {e}")
            return False


# Global service instance (will be initialized with Supabase client)
supabase_service: Optional[SupabaseService] = None


def get_supabase_service() -> SupabaseService:
    """
    Get the global Supabase service instance.

    Returns:
        SupabaseService instance

    Raises:
        RuntimeError: If service not initialized
    """
    if supabase_service is None:
        raise RuntimeError("SupabaseService not initialized. Call init_supabase_service() first.")
    return supabase_service


async def init_supabase_service(supabase: AsyncClient) -> SupabaseService:
    """
    Initialize the global Supabase service.

    Args:
        supabase: Async Supabase client

    Returns:
        Initialized SupabaseService instance
    """
    global supabase_service
    supabase_service = SupabaseService(supabase)
    return supabase_service
