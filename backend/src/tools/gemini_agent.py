import google.generativeai as genai
from pydantic import BaseModel
from pydantic_ai import Agent
from fastapi import HTTPException, status
from ..utils.prompt_loader import load_prompt_template
from ..utils.logger import info
from ..schemas.prep_report import PrepReport
from ..config import settings
import os


async def generate_prep_report_with_gemini(
    prep_request: BaseModel,
    current_user: BaseModel,
    research_result: dict,
) -> PrepReport:
    """Generates a sales prep report using Google Gemini AI."""
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_API_KEY not set in settings.",
        )

    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY # Explicitly set environment variable
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel(
        "gemini-pro"
    )  # Using gemini-pro for now, will switch to 2.5 Pro later

    # Construct the prompt
    prompt_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "prompts",
        "prep_report_prompt.md",
    )
    prompt_template = await load_prompt_template(prompt_file_path)
    prompt = prompt_template.format(
        company_name=prep_request.company_name,
        meeting_objective=prep_request.meeting_objective,
        user_profile=current_user.model_dump_json(),
        research_data=research_result,
    )

    try:
        ai_agent = Agent(model='gemini-2.5-pro', output_type=PrepReport)
        run_result = await ai_agent.run(prompt)
        prep_report: PrepReport = run_result.output
        info("Gemini generated prep report successfully.")
        return prep_report
    except Exception as e:
        info(f"Error generating prep report with Gemini: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating prep report: {e}",
        )
