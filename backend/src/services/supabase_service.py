"""Supabase service for database operations."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from supabase_auth.types import User

from supabase import AsyncClient

from ..utils.logger import error, info

# Import specific exceptions for better error handling
try:
    from postgrest.exceptions import PostgrestError
except ImportError:
    PostgrestError = Exception

try:
    from supabase import APIError
except ImportError:
    APIError = Exception


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
                .select(
                    "company_name, company_description, industries_served, portfolio"
                )
                .eq("id", user_id)
                .execute()
            )

            if response.data:
                return response.data[0]
            return None

        except PostgrestError as e:
            error(f"Database error retrieving user profile: {e}")
            return None
        except APIError as e:
            error(f"API error retrieving user profile: {e}")
            return None
        except Exception as e:
            error(f"Unexpected error retrieving user profile: {e}")
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
        cache_hit: bool,
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
                "cache_hit": cache_hit,
            }

            response = (
                await self.supabase.table("meeting_preps").insert(prep_record).execute()
            )

            if response.data:
                prep_id = response.data[0]["id"]
                info(f"Saved meeting prep with ID: {prep_id}")
                return prep_id

            return None

        except PostgrestError as e:
            error(f"Database error saving meeting prep: {e}")
            return None
        except APIError as e:
            error(f"API error saving meeting prep: {e}")
            return None
        except Exception as e:
            error(f"Unexpected error saving meeting prep: {e}")
            return None

    async def get_meeting_prep(
        self, prep_id: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
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

        except PostgrestError as e:
            error(f"Database error retrieving meeting prep: {e}")
            return None
        except APIError as e:
            error(f"API error retrieving meeting prep: {e}")
            return None
        except Exception as e:
            error(f"Unexpected error retrieving meeting prep: {e}")
            return None

    async def search_portfolio_projects(
        self, user_id: str, search_query: str, limit: int = 5
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
                    matches.append(
                        {
                            "index": i,
                            "project": project,
                            "relevance_score": relevance_score,
                        }
                    )

            # Sort by relevance score
            matches.sort(key=lambda x: x["relevance_score"], reverse=True)

            return matches[:limit]

        except PostgrestError as e:
            error(f"Database error searching portfolio: {e}")
            return []
        except APIError as e:
            error(f"API error searching portfolio: {e}")
            return []
        except Exception as e:
            error(f"Unexpected error searching portfolio: {e}")
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
        project_text = " ".join(
            [
                str(project.get("name", "")),
                str(project.get("client_industry", "")),
                str(project.get("description", "")),
                str(project.get("key_outcomes", "")),
            ]
        ).lower()

        query_terms = query.lower().split()
        matches = sum(1 for term in query_terms if term in project_text)

        # Simple score: matches / total query terms
        return matches / len(query_terms) if query_terms else 0.0

    async def save_meeting_outcome(
        self, prep_id: str, outcome_data: Dict[str, Any]
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
                # (updated_at will be set automatically by database trigger)
                response = (
                    await self.supabase.table("meeting_outcomes")
                    .update(outcome_data)
                    .eq("prep_id", prep_id)
                    .execute()
                )
                info(f"Updated meeting outcome for prep {prep_id}")
            else:
                # Create new outcome
                outcome_record = {"prep_id": prep_id, **outcome_data}
                response = (
                    await self.supabase.table("meeting_outcomes")
                    .insert(outcome_record)
                    .execute()
                )
                info(f"Created meeting outcome for prep {prep_id}")

            if response.data:
                return response.data[0]["id"]

            return None

        except PostgrestError as e:
            error(f"Database error saving meeting outcome: {e}")
            return None
        except APIError as e:
            error(f"API error saving meeting outcome: {e}")
            return None
        except Exception as e:
            error(f"Unexpected error saving meeting outcome: {e}")
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

        except PostgrestError as e:
            error(f"Database error retrieving meeting outcome: {e}")
            return None
        except APIError as e:
            error(f"API error retrieving meeting outcome: {e}")
            return None
        except Exception as e:
            error(f"Unexpected error retrieving meeting outcome: {e}")
            return None

    async def get_user_meeting_outcomes(
        self, user_id: str, limit: int = 50
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

        except PostgrestError as e:
            error(f"Database error retrieving meeting outcomes: {e}")
            return []
        except APIError as e:
            error(f"API error retrieving meeting outcomes: {e}")
            return []
        except Exception as e:
            error(f"Unexpected error retrieving meeting outcomes: {e}")
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

        except PostgrestError as e:
            error(f"Database error counting preps: {e}")
            return 0
        except APIError as e:
            error(f"API error counting preps: {e}")
            return 0
        except Exception as e:
            error(f"Unexpected error counting preps: {e}")
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
                    "avg_confidence": 0.0,
                }

            # Calculate average confidence
            total_confidence = sum(
                prep["overall_confidence"] for prep in preps_response.data
            )
            avg_confidence = total_confidence / len(preps_response.data)

            # Get outcomes to calculate success rate
            outcomes_response = (
                await self.supabase.table("meeting_outcomes")
                .select("meeting_status, outcome, meeting_preps!inner(user_id)")
                .eq("meeting_preps.user_id", user_id)
                .execute()
            )

            if not outcomes_response.data:
                return {
                    "success_rate": 0.0,
                    "total_successful": 0,
                    "total_completed": 0,
                    "avg_confidence": round(avg_confidence, 2),
                }

            # Calculate success rate
            completed_count = sum(
                1 for o in outcomes_response.data if o["meeting_status"] == "completed"
            )
            successful_count = sum(
                1 for o in outcomes_response.data if o["outcome"] == "successful"
            )

            success_rate = (
                (successful_count / completed_count * 100)
                if completed_count > 0
                else 0.0
            )

            return {
                "success_rate": round(success_rate, 1),
                "total_successful": successful_count,
                "total_completed": completed_count,
                "avg_confidence": round(avg_confidence, 2),
            }

        except PostgrestError as e:
            error(f"Database error calculating success metrics: {e}")
            return {
                "success_rate": 0.0,
                "total_successful": 0,
                "total_completed": 0,
                "avg_confidence": 0.0,
            }
        except APIError as e:
            error(f"API error calculating success metrics: {e}")
            return {
                "success_rate": 0.0,
                "total_successful": 0,
                "total_completed": 0,
                "avg_confidence": 0.0,
            }
        except Exception as e:
            error(f"Unexpected error calculating success metrics: {e}")
            return {
                "success_rate": 0.0,
                "total_successful": 0,
                "total_completed": 0,
                "avg_confidence": 0.0,
            }

    async def get_recent_preps(
        self, user_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent preps for a user.

        Args:
            user_id: UUID of the user
            limit: Maximum number of preps to return

        Returns:
            List of recent preps with basic info including outcome_status
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
                    overall_confidence,
                    meeting_outcomes!prep_id(meeting_status, outcome)
                """)
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            # Process the data to flatten outcome_status
            preps_data = response.data if response.data else []

            for prep in preps_data:
                # Extract meeting_status from meeting_outcomes (it's a single object due to UNIQUE constraint)
                if prep.get("meeting_outcomes"):
                    prep["outcome_status"] = prep["meeting_outcomes"].get("meeting_status")
                else:
                    prep["outcome_status"] = None
                # Remove the nested meeting_outcomes field
                prep.pop("meeting_outcomes", None)

            return preps_data

        except PostgrestError as e:
            error(f"Database error retrieving recent preps: {e}")
            return []
        except APIError as e:
            error(f"API error retrieving recent preps: {e}")
            return []
        except Exception as e:
            error(f"Unexpected error retrieving recent preps: {e}")
            return []

    async def get_upcoming_meetings(
        self, user_id: str, days_ahead: int = 7
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
            future_date = (datetime.now() + timedelta(days=days_ahead)).strftime(
                "%Y-%m-%d"
            )

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
                .order("meeting_date", desc=False)
                .execute()
            )

            return response.data if response.data else []

        except PostgrestError as e:
            error(f"Database error retrieving upcoming meetings: {e}")
            return []
        except APIError as e:
            error(f"API error retrieving upcoming meetings: {e}")
            return []
        except Exception as e:
            error(f"Unexpected error retrieving upcoming meetings: {e}")
            return []

    async def get_dashboard_aggregated(self, user_id: str) -> Dict[str, Any]:
        """
        Get all dashboard data in a single optimized query using CTEs.

        This method combines:
        - get_total_preps_count (1 query)
        - get_success_metrics (2 queries)
        - get_recent_preps (1 query)
        - get_upcoming_meetings (1 query)

        Total: 5 queries → 1 query (80% reduction in database round-trips)

        Args:
            user_id: UUID of the user

        Returns:
            Dictionary with all dashboard data
        """
        try:
            # Use the new simplified RPC function
            response = await self.supabase.rpc(
                "get_dashboard_data_aggregated",
                {"user_uuid": user_id}
            ).execute()

            # Check if the RPC function returns a dict directly or wrapped in a list
            if response.data and isinstance(response.data, dict):
                result = response.data
            elif response.data and len(response.data) > 0:
                result = response.data[0]
            else:
                return {
                    "total_preps": 0,
                    "success_rate": 0.0,
                    "total_successful": 0,
                    "total_completed": 0,
                    "avg_confidence": 0.0,
                    "time_saved_hours": 0.0,
                    "time_saved_minutes": 0,
                    "recent_preps": [],
                    "upcoming_meetings": [],
                }

            # Calculate time saved (18 minutes per prep on average)
            total_preps = result.get("total_preps", 0)
            time_saved_minutes = total_preps * 18
            time_saved_hours = round(time_saved_minutes / 60, 1)

            recent_preps = result.get("recent_preps", [])
            upcoming_meetings = result.get("upcoming_meetings", [])

            # Build the dashboard response
            dashboard_data = {
                "total_preps": total_preps,
                "success_rate": result.get("success_rate", 0.0),
                "total_successful": result.get("total_successful", 0),
                "total_completed": result.get("total_completed", 0),
                "avg_confidence": result.get("avg_confidence", 0.0),
                "time_saved_hours": time_saved_hours,
                "time_saved_minutes": time_saved_minutes,
                "recent_preps": recent_preps,
                "upcoming_meetings": upcoming_meetings,
            }

            return dashboard_data

        except PostgrestError as e:
            error(f"Database error in aggregated dashboard query: {e}")
            # Fallback to individual queries if aggregated query fails
            return await self._get_dashboard_fallback(user_id)
        except APIError as e:
            error(f"API error in aggregated dashboard query: {e}")
            return await self._get_dashboard_fallback(user_id)
        except Exception as e:
            error(f"Unexpected error in aggregated dashboard query: {e}")
            return await self._get_dashboard_fallback(user_id)

    async def _get_dashboard_fallback(self, user_id: str) -> Dict[str, Any]:
        """
        Fallback method that uses individual queries if aggregated query fails.
        This ensures the dashboard still works even if the optimized query has issues.
        """
        try:
            # Call individual methods (original implementation)
            total_preps = await self.get_total_preps_count(user_id)
            success_metrics = await self.get_success_metrics(user_id)
            recent_preps = await self.get_recent_preps(user_id, limit=10)
            upcoming_meetings = await self.get_upcoming_meetings(user_id, days_ahead=7)

            # Calculate time saved
            time_saved_minutes = total_preps * 18
            time_saved_hours = round(time_saved_minutes / 60, 1)

            return {
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
        except Exception as e:
            error(f"Fatal error in dashboard fallback: {e}")
            return {
                "total_preps": 0,
                "success_rate": 0.0,
                "total_successful": 0,
                "total_completed": 0,
                "avg_confidence": 0.0,
                "time_saved_hours": 0.0,
                "time_saved_minutes": 0,
                "recent_preps": [],
                "upcoming_meetings": [],
            }

    async def get_user_preps_paginated(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
        status_filter: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get paginated list of user's preps.

        Args:
            user_id: UUID of the user
            limit: Number of items to return
            offset: Number of items to skip
            status_filter: Filter by status (pending, completed, cancelled, rescheduled, all)
            search: Search by company name

        Returns:
            List of preps with outcomes joined
        """
        try:
            # Build query
            query = (
                self.supabase.table("meeting_preps")
                .select("""
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
            """)
                .eq("user_id", user_id)
            )

            # Apply status filter
            if status_filter and status_filter != "all":
                # Validate and split status values (support comma-separated)
                valid_statuses = {"pending", "completed", "cancelled", "rescheduled"}
                status_values = [s.strip() for s in status_filter.split(",")]

                # Validate all status values
                for status in status_values:
                    if status not in valid_statuses:
                        raise ValueError(
                            f"Invalid status filter: '{status}'. Valid values are: {', '.join(valid_statuses)}"
                        )

                # Get prep IDs based on status filter
                prep_ids = []

                # Handle 'pending' - preps without outcomes
                if "pending" in status_values:
                    # Get all prep IDs for the user
                    user_preps_response = (
                        await self.supabase.table("meeting_preps")
                        .select("id")
                        .eq("user_id", user_id)
                        .execute()
                    )
                    all_prep_ids = (
                        [p["id"] for p in user_preps_response.data]
                        if user_preps_response.data
                        else []
                    )

                    # Get prep IDs that have outcomes
                    outcome_response = (
                        await self.supabase.table("meeting_outcomes")
                        .select("prep_id")
                        .in_("prep_id", all_prep_ids)
                        .execute()
                    )
                    prep_ids_with_outcomes = (
                        [o["prep_id"] for o in outcome_response.data]
                        if outcome_response.data
                        else []
                    )

                    # Pending = all preps minus preps with outcomes
                    prep_ids = [
                        pid for pid in all_prep_ids if pid not in prep_ids_with_outcomes
                    ]

                    # If there are other statuses mixed with pending, we'll get those separately
                    other_statuses = [s for s in status_values if s != "pending"]
                    if other_statuses:
                        outcomes_response = (
                            await self.supabase.table("meeting_outcomes")
                            .select("prep_id")
                            .in_("meeting_status", other_statuses)
                            .execute()
                        )
                        prep_ids.extend(
                            [o["prep_id"] for o in outcomes_response.data]
                            if outcomes_response.data
                            else []
                        )
                else:
                    # No 'pending' - just filter by meeting_status
                    outcomes_response = (
                        await self.supabase.table("meeting_outcomes")
                        .select("prep_id")
                        .in_("meeting_status", status_values)
                        .execute()
                    )
                    prep_ids = (
                        [o["prep_id"] for o in outcomes_response.data]
                        if outcomes_response.data
                        else []
                    )

                # Apply the filter to the query
                if prep_ids:
                    query = query.in_("id", prep_ids)
                else:
                    # If no matching preps, return empty result
                    return []

            # Apply search
            if search:
                query = query.ilike("company_name", f"%{search}%")

            # Apply pagination and ordering
            response = (
                query.order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return response.data if response.data else []

        except PostgrestError as e:
            error(f"Database error retrieving paginated preps: {e}")
            return []
        except APIError as e:
            error(f"API error retrieving paginated preps: {e}")
            return []
        except Exception as e:
            error(f"Unexpected error retrieving paginated preps: {e}")
            return []

    async def get_user_preps_count(
        self,
        user_id: str,
        status_filter: Optional[str] = None,
        search: Optional[str] = None,
    ) -> int:
        """
        Get total count of user's preps for pagination.

        Args:
            user_id: UUID of the user
            status_filter: Filter by status (pending, completed, cancelled, rescheduled, all)
            search: Search by company name

        Returns:
            Total count
        """
        try:
            # If status_filter is provided and not "all", we need to apply the filter
            # For count, we can't use joins easily, so we'll get matching prep IDs first
            prep_ids = None

            if status_filter and status_filter != "all":
                # Validate and split status values (support comma-separated)
                valid_statuses = {"pending", "completed", "cancelled", "rescheduled"}
                status_values = [s.strip() for s in status_filter.split(",")]

                # Validate all status values
                for status in status_values:
                    if status not in valid_statuses:
                        raise ValueError(
                            f"Invalid status filter: '{status}'. Valid values are: {', '.join(valid_statuses)}"
                        )

                # Get prep IDs based on status filter
                prep_ids = []

                # Handle 'pending' - preps without outcomes
                if "pending" in status_values:
                    # Get all prep IDs for the user
                    user_preps_response = (
                        await self.supabase.table("meeting_preps")
                        .select("id")
                        .eq("user_id", user_id)
                        .execute()
                    )
                    all_prep_ids = (
                        [p["id"] for p in user_preps_response.data]
                        if user_preps_response.data
                        else []
                    )

                    # Get prep IDs that have outcomes
                    outcome_response = (
                        await self.supabase.table("meeting_outcomes")
                        .select("prep_id")
                        .in_("prep_id", all_prep_ids)
                        .execute()
                    )
                    prep_ids_with_outcomes = (
                        [o["prep_id"] for o in outcome_response.data]
                        if outcome_response.data
                        else []
                    )

                    # Pending = all preps minus preps with outcomes
                    prep_ids = [
                        pid for pid in all_prep_ids if pid not in prep_ids_with_outcomes
                    ]

                    # If there are other statuses mixed with pending, we'll get those separately
                    other_statuses = [s for s in status_values if s != "pending"]
                    if other_statuses:
                        outcomes_response = (
                            await self.supabase.table("meeting_outcomes")
                            .select("prep_id")
                            .in_("meeting_status", other_statuses)
                            .execute()
                        )
                        prep_ids.extend(
                            [o["prep_id"] for o in outcomes_response.data]
                            if outcomes_response.data
                            else []
                        )
                else:
                    # No 'pending' - just filter by meeting_status
                    outcomes_response = (
                        await self.supabase.table("meeting_outcomes")
                        .select("prep_id")
                        .in_("meeting_status", status_values)
                        .execute()
                    )
                    prep_ids = (
                        [o["prep_id"] for o in outcomes_response.data]
                        if outcomes_response.data
                        else []
                    )

            # Build the query
            query = (
                self.supabase.table("meeting_preps")
                .select("id", count="exact")
                .eq("user_id", user_id)
            )

            # Apply the status filter
            if prep_ids is not None:
                if prep_ids:
                    query = query.in_("id", prep_ids)
                else:
                    # If no matching preps, return 0
                    return 0

            if search:
                query = query.ilike("company_name", f"%{search}%")

            response = query.execute()
            return response.count if response.count else 0

        except PostgrestError as e:
            error(f"Database error counting user preps: {e}")
            return 0
        except APIError as e:
            error(f"API error counting user preps: {e}")
            return 0
        except Exception as e:
            error(f"Unexpected error counting user preps: {e}")
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
        error_message: Optional[str],
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
                "error_message": error_message,
            }

            await self.supabase.table("api_usage_logs").insert(log_entry).execute()
            return True

        except PostgrestError as e:
            error(f"Database error logging API usage: {e}")
            return False
        except APIError as e:
            error(f"API error logging API usage: {e}")
            return False
        except Exception as e:
            error(f"Unexpected error logging API usage: {e}")
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
        raise RuntimeError(
            "SupabaseService not initialized. Call init_supabase_service() first."
        )
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
