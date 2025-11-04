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

            # Run the actor
            run_input = {
                "companyName": company_name,
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
            error(f"Error scraping LinkedIn for {company_name}: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    async def search_linkedin_profile(self, person_name: str, company_name: str) -> Dict[str, Any]:
        """
        Search for a person's LinkedIn profile.

        Args:
            person_name: Name of the person to search for
            company_name: Name of their company

        Returns:
            Dictionary containing profile data
        """
        try:
            info(f"Searching LinkedIn profile for: {person_name} at {company_name}")

            run_input = {
                "profiles": [
                    {
                        "name": person_name,
                        "company": company_name
                    }
                ]
            }

            actor_id = "icypeas_official/linkedin-profile-scraper"
            run = self.client.actor(actor_id).call(run_input=run_input)

            # Get the results
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)

            if results:
                info(f"Found LinkedIn profile for {person_name}")
                return {
                    "success": True,
                    "data": results[0],
                    "source": "apify_profile_search"
                }
            else:
                error(f"No LinkedIn profile found for {person_name}")
                return {
                    "success": False,
                    "data": None,
                    "error": "Profile not found"
                }

        except Exception as e:
            error(f"Error searching LinkedIn profile for {person_name}: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
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

            run_input = {
                "startUrls": [{"url": f"https://www.linkedin.com/company/{company_name.replace(' ', '')}/posts/"}],
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
            error(f"Error scraping LinkedIn posts for {company_name}: {e}")
            return {
                "success": False,
                "data": [],
                "error": str(e)
            }


# Global instance
apify_service = ApifyService()
