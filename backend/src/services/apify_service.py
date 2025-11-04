"""Apify client wrapper for LinkedIn scraping."""
from typing import Optional, Dict, Any
from apify_client import ApifyClient
from ..config import settings
from ..utils.logger import info, error


class ApifyService:
    """Service for interacting with Apify actors for LinkedIn data scraping."""

    def __init__(self):
        """Initialize the Apify client."""
        self.client = ApifyClient(token=settings.APIFY_API_KEY)

    async def scrape_company_linkedin(self, company_name: str) -> Dict[str, Any]:
        """
        Scrape company LinkedIn page using Apify actor.

        Args:
            company_name: Name of the company to scrape

        Returns:
            Dictionary containing company LinkedIn data
        """
        try:
            info(f"Scraping LinkedIn data for company: {company_name}")

            # Run the actor - try without companyName first (some actors use different params)
            # Many LinkedIn company scrapers need the company URL, not name
            clean_name = ''.join(c for c in company_name if c.isalnum())
            company_url = f"https://www.linkedin.com/company/{clean_name}/"

            run_input = {
                "startUrls": [{"url": company_url}],
                "maxResults": 1
            }

            actor_id = "scrapeverse/linkedin-company-profile-scraper"
            run = self.client.actor(actor_id).call(run_input=run_input)

            # Get the results
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)

            if results:
                info(f"Successfully scraped LinkedIn data for {company_name}")
                return {
                    "success": True,
                    "data": results[0],
                    "source": "apify_company_linkedin"
                }
            else:
                error(f"No LinkedIn data found for {company_name}")
                return {
                    "success": False,
                    "data": None,
                    "error": "No data found"
                }

        except Exception as e:
            error_msg = str(e).lower()
            error(f"Error scraping LinkedIn for {company_name}: {e}")

            # Check for specific error types
            if "trial" in error_msg and "expired" in error_msg:
                return {
                    "success": False,
                    "data": None,
                    "error": "Apify trial expired. Please rent the paid actor to continue using LinkedIn company scraping."
                }
            elif "quota" in error_msg or "billing" in error_msg:
                return {
                    "success": False,
                    "data": None,
                    "error": "Apify quota exceeded. Please check your billing or upgrade your plan."
                }
            elif "rate limit" in error_msg or "429" in error_msg:
                return {
                    "success": False,
                    "data": None,
                    "error": "Apify rate limit exceeded. Please try again later."
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": f"LinkedIn company scraping failed: {str(e)}"
                }

    async def search_linkedin_profile(self, person_name: str, company_name: str) -> Dict[str, Any]:
        """
        Search for a person's LinkedIn profile by first finding their URL, then scraping it.

        Args:
            person_name: Name of the person to search for
            company_name: Name of their company

        Returns:
            Dictionary containing profile data
        """
        try:
            info(f"Searching LinkedIn profile for: {person_name} at {company_name}")

            # First, we need to find the LinkedIn URL
            # Use a simple query to find the profile
            query = f'"{person_name}" "{company_name}" site:linkedin.com/in'
            info(f"Searching for LinkedIn profile URL with query: {query}")

            # Note: This would need to be implemented with the search service
            # For now, we'll try using the profile scraper with a search
            # The icypeas_official actor can search if given the right input format

            # Try using a different approach - search for profile URL first
            # Then scrape it with the actor
            search_query = f'"{person_name}" "{company_name}" LinkedIn'

            # Import search service here to avoid circular imports
            from .search_service import search_service

            # Search for the LinkedIn profile URL
            search_results = await search_service.search(search_query, num_results=5)

            if not search_results.get("success") or not search_results.get("organic_results"):
                error(f"No search results found for {person_name}")
                return {
                    "success": False,
                    "data": None,
                    "error": "Profile not found - no search results"
                }

            # Find the LinkedIn profile URL from search results
            linkedin_url = None
            for result in search_results["organic_results"]:
                if "linkedin.com/in/" in result.get("link", ""):
                    linkedin_url = result["link"]
                    break

            if not linkedin_url:
                error(f"No LinkedIn profile URL found for {person_name}")
                return {
                    "success": False,
                    "data": None,
                    "error": "No LinkedIn profile URL found"
                }

            info(f"Found LinkedIn URL for {person_name}: {linkedin_url}")

            # Now scrape the profile using the URL
            run_input = {
                "linkedinUrls": [linkedin_url]
            }

            actor_id = "icypeas_official/linkedin-profile-scraper"
            run = self.client.actor(actor_id).call(run_input=run_input)

            # Get the results
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)

            if results:
                info(f"Successfully scraped LinkedIn profile for {person_name}")
                return {
                    "success": True,
                    "data": results[0],
                    "source": "apify_profile_scraper"
                }
            else:
                error(f"No data returned from scraper for {person_name}")
                return {
                    "success": False,
                    "data": None,
                    "error": "Profile scraping returned no data"
                }

        except Exception as e:
            error_msg = str(e).lower()
            error(f"Error searching LinkedIn profile for {person_name}: {e}")

            # Check for specific error types
            if "trial" in error_msg and "expired" in error_msg:
                return {
                    "success": False,
                    "data": None,
                    "error": "Apify trial expired. Please rent the paid actor to continue using LinkedIn profile scraping."
                }
            elif "quota" in error_msg or "billing" in error_msg:
                return {
                    "success": False,
                    "data": None,
                    "error": "Apify quota exceeded. Please check your billing or upgrade your plan."
                }
            elif "rate limit" in error_msg or "429" in error_msg:
                return {
                    "success": False,
                    "data": None,
                    "error": "Apify rate limit exceeded. Please try again later."
                }
            elif "invalid" in error_msg and "argument" in error_msg:
                return {
                    "success": False,
                    "data": None,
                    "error": f"Invalid input for profile search: {str(e)}"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": f"LinkedIn profile search failed: {str(e)}"
                }

    async def scrape_linkedin_posts(self, company_name: str, limit: int = 10) -> Dict[str, Any]:
        """
        Scrape recent LinkedIn posts from a company.

        Args:
            company_name: Name of the company
            limit: Maximum number of posts to scrape

        Returns:
            Dictionary containing recent posts
        """
        try:
            info(f"Scraping LinkedIn posts for: {company_name}")

            # Clean company name for URL (remove spaces, special chars)
            clean_name = ''.join(c for c in company_name if c.isalnum())
            company_url = f"https://www.linkedin.com/company/{clean_name}/"

            run_input = {
                "urls": [company_url],
                "maxPosts": limit
            }

            actor_id = "supreme_coder/linkedin-post"
            run = self.client.actor(actor_id).call(run_input=run_input)

            # Get the results
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)

            if results:
                info(f"Successfully scraped {len(results)} LinkedIn posts for {company_name}")
                return {
                    "success": True,
                    "data": results,
                    "source": "apify_posts"
                }
            else:
                error(f"No LinkedIn posts found for {company_name}")
                return {
                    "success": False,
                    "data": [],
                    "error": "No posts found"
                }

        except Exception as e:
            error_msg = str(e).lower()
            error(f"Error scraping LinkedIn posts for {company_name}: {e}")

            # Check for specific error types
            if "trial" in error_msg and "expired" in error_msg:
                return {
                    "success": False,
                    "data": [],
                    "error": "Apify trial expired. Please rent the paid actor to continue using LinkedIn posts scraping."
                }
            elif "quota" in error_msg or "billing" in error_msg:
                return {
                    "success": False,
                    "data": [],
                    "error": "Apify quota exceeded. Please check your billing or upgrade your plan."
                }
            elif "rate limit" in error_msg or "429" in error_msg:
                return {
                    "success": False,
                    "data": [],
                    "error": "Apify rate limit exceeded. Please try again later."
                }
            else:
                return {
                    "success": False,
                    "data": [],
                    "error": f"LinkedIn posts scraping failed: {str(e)}"
                }


# Global instance
apify_service = ApifyService()
