"""Cache service for managing company research data."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from supabase import AsyncClient
from ..utils.logger import info, error


class CacheService:
    """Service for managing the company_cache table with 7-day TTL."""

    def __init__(self, supabase: AsyncClient):
        """Initialize with Supabase client."""
        self.supabase = supabase
        self.cache_ttl_days = 7

    async def get_cached_company_data(self, normalized_company_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached company research data if it exists and is fresh.

        Args:
            normalized_company_name: Normalized company name for lookup

        Returns:
            Cached data if fresh, None otherwise
        """
        try:
            response = (
                await self.supabase.table("company_cache")
                .select("*")
                .eq("company_name_normalized", normalized_company_name)
                .limit(1)
                .execute()
            )

            if not response.data:
                info(f"No cache found for {normalized_company_name}")
                return None

            cached_entry = response.data[0]
            last_updated = datetime.fromisoformat(cached_entry["last_updated"])
            current_time = datetime.now(last_updated.tzinfo)
            age_days = (current_time - last_updated).days

            if age_days < self.cache_ttl_days:
                info(f"Cache hit for {normalized_company_name} (age: {age_days} days)")
                return {
                    "company_data": cached_entry["company_data"],
                    "confidence_score": cached_entry["confidence_score"],
                    "source_urls": cached_entry.get("source_urls", []),
                    "last_updated": cached_entry["last_updated"],
                    "cache_status": "fresh"
                }
            else:
                info(f"Cache for {normalized_company_name} is stale (age: {age_days} days)")
                return {
                    "company_data": cached_entry["company_data"],
                    "confidence_score": cached_entry["confidence_score"],
                    "source_urls": cached_entry.get("source_urls", []),
                    "last_updated": cached_entry["last_updated"],
                    "cache_status": "stale"
                }

        except Exception as e:
            error(f"Error retrieving cache for {normalized_company_name}: {e}")
            return None

    async def cache_company_data(
        self,
        normalized_company_name: str,
        company_data: Dict[str, Any],
        confidence_score: float,
        source_urls: list
    ) -> bool:
        """
        Store company research data in the cache.

        Args:
            normalized_company_name: Normalized company name
            company_data: Research data to cache
            confidence_score: Confidence score for the research
            source_urls: List of source URLs used

        Returns:
            True if successful, False otherwise
        """
        try:
            cache_data = {
                "company_name_normalized": normalized_company_name,
                "company_data": company_data,
                "confidence_score": max(0.0, min(1.0, confidence_score)),  # Clamp to 0-1
                "last_updated": datetime.now().isoformat(),
                "source_urls": source_urls
            }

            await (
                self.supabase.table("company_cache")
                .upsert(cache_data, on_conflict="company_name_normalized")
                .execute()
            )

            info(f"Successfully cached research data for {normalized_company_name}")
            return True

        except Exception as e:
            error(f"Error caching data for {normalized_company_name}: {e}")
            return False

    async def delete_cache(self, normalized_company_name: str) -> bool:
        """
        Delete cached data for a company.

        Args:
            normalized_company_name: Normalized company name

        Returns:
            True if successful, False otherwise
        """
        try:
            await (
                self.supabase.table("company_cache")
                .delete()
                .eq("company_name_normalized", normalized_company_name)
                .execute()
            )

            info(f"Deleted cache for {normalized_company_name}")
            return True

        except Exception as e:
            error(f"Error deleting cache for {normalized_company_name}: {e}")
            return False

    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.

        Returns:
            Dictionary with cache statistics
        """
        try:
            response = (
                await self.supabase.table("company_cache")
                .select("company_name_normalized, last_updated, confidence_score")
                .execute()
            )

            total_entries = len(response.data)
            fresh_entries = 0
            stale_entries = 0
            total_confidence = 0.0

            current_time = datetime.now()
            for entry in response.data:
                last_updated = datetime.fromisoformat(entry["last_updated"])
                age_days = (current_time - last_updated).days

                if age_days < self.cache_ttl_days:
                    fresh_entries += 1
                else:
                    stale_entries += 1

                total_confidence += entry["confidence_score"]

            avg_confidence = total_confidence / total_entries if total_entries > 0 else 0.0

            return {
                "total_entries": total_entries,
                "fresh_entries": fresh_entries,
                "stale_entries": stale_entries,
                "avg_confidence": avg_confidence,
                "cache_hit_rate_target": "40%",
                "cache_ttl_days": self.cache_ttl_days
            }

        except Exception as e:
            error(f"Error getting cache stats: {e}")
            return {
                "total_entries": 0,
                "fresh_entries": 0,
                "stale_entries": 0,
                "avg_confidence": 0.0,
                "error": str(e)
            }
