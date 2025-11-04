<<<<<<< HEAD
"""Router for sales prep generation using two-agent system."""
import re
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from gotrue import User
from supabase import AsyncClient

from ..dependencies import get_current_user, get_supabase_client
from ..schemas.prep_report import PrepRequest
from ..services.cache_service import CacheService
from ..services.supabase_service import SupabaseService, get_supabase_service
from ..agents import research_orchestrator, sales_brief_synthesizer
from ..utils.logger import info, error


router = APIRouter()


def normalize_company_name(name: str) -> str:
    """
    Normalizes company name for consistent caching.

    Args:
        name: Original company name

    Returns:
        Normalized company name (lowercase, alphanumeric only)
    """
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

=======
from datetime import datetime, timedelta
import re

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from supabase import AsyncClient

from datetime import datetime, timedelta
import re

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from supabase import AsyncClient

from ..dependencies import get_current_user, get_supabase_client
from ..utils.logger import info
from ..schemas.prep_report import PrepReport
from ..tools.gemini_agent import generate_prep_report_with_gemini
from ..tools.serpapi_search import perform_serpapi_search
from ..tools.firecrawl_scrape import perform_firecrawl_scrape

router = APIRouter()

class PrepRequest(BaseModel):
    company_name: str
    meeting_objective: str

def normalize_company_name(name: str) -> str:
    """Normalizes company name for consistent caching."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
>>>>>>> origin/dev

@router.post("/preps", status_code=status.HTTP_200_OK)
async def create_prep(
    prep_request: PrepRequest,
<<<<<<< HEAD
    current_user: User = Depends(get_current_user),
    supabase: AsyncClient = Depends(get_supabase_client),
):
    """
    Create a new sales prep report using the two-agent system.

    Flow:
    1. Check cache for fresh company data
    2. Cache miss → Agent A researches with tool-calling
    3. Agent B synthesizes: research + user profile → sales brief
    4. Save to database

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
=======
    current_user: str = Depends(get_current_user),
    supabase: AsyncClient = Depends(get_supabase_client),
):
    """Creates a new sales prep report."""
    info(f"Received prep request for company: {prep_request.company_name} with objective: {prep_request.meeting_objective} by user: {current_user.id}")

    normalized_company_name = normalize_company_name(prep_request.company_name)
    info(f"Normalized company name: {normalized_company_name}")

    # Check cache first
    cache_response = await supabase.table("company_cache").select("*").eq("company_name_normalized", normalized_company_name).limit(1).execute()
    cached_data = cache_response.data[0] if cache_response.data else None
>>>>>>> origin/dev

    research_data = {}
    cache_hit = False

<<<<<<< HEAD
    if cached_data and cached_data.get("cache_status") == "fresh":
        # Cache hit - use cached data
        info(f"✓ Cache hit for {normalized_company_name}. Using cached data.")
        research_data = cached_data["company_data"]
        cache_hit = True
    else:
        # Cache miss or stale - run Agent A
        info(f"Cache miss or stale for {normalized_company_name}. Running Agent A (Research Orchestrator).")

        try:
            # Agent A: Research Orchestrator
            research_result = await research_orchestrator.research_company(
                company_name=prep_request.company_name,
                meeting_objective=prep_request.meeting_objective,
                contact_person_name=prep_request.contact_person_name,
                contact_linkedin_url=prep_request.contact_linkedin_url
            )

            if not research_result["success"]:
                error(f"Agent A failed for {normalized_company_name}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Research failed: {research_result.get('error', 'Unknown error')}"
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
                    source_urls=source_urls
                )

        except Exception as e:
            error(f"Error during research phase: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Research error: {str(e)}"
            )

    # Step 2: Get user profile
    info(f"Fetching user profile for user {current_user.id}")
    user_profile = await supabase_service.get_user_profile(str(current_user.id))

    if not user_profile:
        error(f"User profile not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please complete your profile before creating preps."
        )

    # Step 3: Agent B - Sales Brief Synthesizer
    info("Running Agent B (Sales Brief Synthesizer)")
    try:
        prep_report = await sales_brief_synthesizer.synthesize_sales_brief(
            research_data=research_data,
            user_profile=user_profile,
            meeting_objective=prep_request.meeting_objective
        )

        info(f"✓ Sales brief synthesized successfully with confidence: {prep_report.overall_confidence}")

    except Exception as e:
        error(f"Error during synthesis phase: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Synthesis error: {str(e)}"
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
            cache_hit=cache_hit
        )

        if not prep_id:
            raise Exception("Failed to save prep to database")

        info(f"✓ Prep report saved successfully with ID: {prep_id}")

        return {
            "message": "Prep report generated and saved successfully",
            "prep_id": prep_id,
            "report": prep_report.model_dump(),
            "cache_hit": cache_hit
        }

    except Exception as e:
        error(f"Error saving prep to database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
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
            detail="Prep report not found or not authorized."
        )

    try:
        prep_report = PrepReport.model_validate_json(prep_data["prep_data"])
        return prep_report
    except Exception as e:
        error(f"Error parsing prep_data from database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing report data."
        )
=======
    if cached_data:
        last_updated = datetime.fromisoformat(cached_data["last_updated"])
        if datetime.now(last_updated.tzinfo) - last_updated < timedelta(days=7):
            info(f"Cache hit for {normalized_company_name}. Using cached data.")
            research_data = cached_data["company_data"]
            cache_hit = True
        else:
            info(f"Cache for {normalized_company_name} is stale. Proceeding with research.")
    else:
        info(f"Cache miss for {normalized_company_name}. Proceeding with research.")

    if not cache_hit:
        # Perform web search
        search_query = f"{prep_request.company_name} official website"
        search_results = await perform_serpapi_search(search_query)
        
        # Extract relevant URLs and scrape
        # For simplicity, let's just take the first organic result URL
        company_url = None
        if "organic_results" in search_results and len(search_results["organic_results"]) > 0:
            company_url = search_results["organic_results"][0]["link"]
            info(f"Found company URL: {company_url}")
            
            scraped_content = await perform_firecrawl_scrape(company_url)
            research_data = {
                "search_results": search_results,
                "scraped_content": scraped_content,
            }
            
            # Store research data in cache
            try:
                insert_cache_data = {
                    "company_name_normalized": normalized_company_name,
                    "company_data": research_data,
                    "confidence_score": 0.5, # Placeholder, will be refined later
                    "last_updated": datetime.now().isoformat(),
                    "source_urls": [company_url]
                }
                await supabase.table("company_cache").upsert(insert_cache_data, on_conflict="company_name_normalized").execute()
                info(f"Research data for {normalized_company_name} saved to cache.")
            except Exception as e:
                info(f"Error saving research data to cache: {e}")
        else:
            info(f"No organic search results found for {search_query}.")
            research_data = {"search_results": search_results} # Store search results even if no URL found

    # Call the new gemini agent to generate the report
    prep_report: PrepReport = await generate_prep_report_with_gemini(prep_request, current_user, research_data)

    # Save the generated report to the meeting_preps table
    try:
        insert_data = {
            "user_id": str(current_user.id),
            "company_name": prep_request.company_name,
            "company_name_normalized": normalized_company_name,
            "meeting_objective": prep_request.meeting_objective,
            "prep_data": prep_report.model_dump_json(),
            "overall_confidence": prep_report.overall_confidence,
            "cache_hit": cache_hit, # Use actual cache_hit status
        }
        response = await supabase.table("meeting_preps").insert(insert_data).execute()
        if not response.data:
            raise Exception("No data returned from Supabase insert.")
        info(f"Prep report saved to database with ID: {response.data[0]['id']}")
        return {
            "message": "Prep report generated and saved successfully",
            "prep_id": response.data[0]["id"],
            "report": prep_report.model_dump(),
        }
    except Exception as e:
        info(f"Error saving prep report to database: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error saving prep report: {e}")

@router.get("/preps/{prep_id}", response_model=PrepReport)
async def get_prep_report(
    prep_id: str,
    current_user: str = Depends(get_current_user),
    supabase: AsyncClient = Depends(get_supabase_client),
):
    """Fetches a saved sales prep report by ID."""
    info(f"Received request to fetch prep report with ID: {prep_id} by user: {current_user.id}")

    response = await supabase.table("meeting_preps").select("*").eq("id", prep_id).eq("user_id", current_user.id).limit(1).execute()
    report_data = response.data[0] if response.data else None

    if not report_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prep report not found or not authorized.")

    # The prep_data is stored as JSONB, so it needs to be parsed back into PrepReport model
    try:
        prep_report = PrepReport.model_validate_json(report_data["prep_data"])
        return prep_report
    except Exception as e:
        info(f"Error parsing prep_data from database: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing report data.")
>>>>>>> origin/dev
