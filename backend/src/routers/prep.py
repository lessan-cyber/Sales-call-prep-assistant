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

@router.post("/preps", status_code=status.HTTP_200_OK)
async def create_prep(
    prep_request: PrepRequest,
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

    research_data = {}
    cache_hit = False

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
