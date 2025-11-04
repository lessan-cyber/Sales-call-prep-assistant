# Phase 3: The Core AI Pipeline

This is the most exciting (and complex) part. We'll build the feature that generates the sales prep reports.

*   **Step 1: The "New Prep" Form**
    *   **What it is:** A simple form where the user inputs the company name and meeting objective.
    *   **Your task:** Create this form on the frontend.

*   **Step 2: The Backend AI Service**
    *   **What it is:** A service in our FastAPI backend that orchestrates the AI generation process.
    *   **Your task:** This is a big one, so break it down:
        1.  **Create the main API endpoint:** `POST /api/preps`.
        2.  **Implement the caching logic:** Before doing any work, check the `company_cache` table to see if we have recent data for this company.
        3.  **Build the research module:** If it's a cache miss, use the SerpAPI/Brave Search and Firecrawl APIs to research the company.
        4.  **Integrate with Gemini:** Use Pydantic AI to create a structured prompt for the Gemini LLM. Pass the user's profile and the research data to the LLM.
        5.  **Process the output:** Take the JSON output from Gemini, calculate the confidence scores, and save the entire report to the `meeting_preps` table.

*   **Step 3: Display the Report**
    *   **What it is:** A page on the frontend to display the generated report in a clean, readable format.
    *   **Your task:** Create a new page that takes a prep ID, fetches the data from the backend (`GET /api/preps/{id}`), and displays it using the `shadcn/ui` components as described in the PRD.
