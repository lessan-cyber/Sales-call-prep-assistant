# Gemini Code Assistant Context

This document provides context for the AI-powered Sales Call Prep Assistant project. The project is currently in the planning phase, and the code has not yet been implemented.

## Project Overview

The project is an AI-powered tool designed to assist sales professionals in preparing for sales calls. It automates the process of researching prospects and generates personalized talking points, aiming to significantly reduce preparation time. The target users are solo freelancers, consultants, and SDRs at small companies.

The core functionality involves taking a company name and meeting objective as input, and generating a comprehensive prep report. This report includes an executive summary, strategic narrative, key talking points, insightful questions to ask, information on key decision-makers, and general company intelligence.

## Architecture

The application is designed with a modern web stack:

*   **Frontend:** Next.js 14 (with App Router), TypeScript, Tailwind CSS, and shadcn/ui. To be deployed on Vercel.
*   **Backend:** FastAPI (Python 3.11+) for the API. To be deployed on Railway or Render.
*   **Database:** Supabase (Postgres) for data storage, user authentication, and file storage.
*   **AI & Machine Learning:**
    *   **LLM:** Google Gemini 2.5 Pro (primary) and Flash (fallback).
    *   **Framework:** Pydantic AI for structured output generation.
    *   **Data Services:** SerpAPI or Brave Search for web searches, and Firecrawl API for web scraping.
*   **Observability:** Pydantic Logfire.
*   **PDF Generation:** ReportLab (Python).

## Key Features

The MVP (Minimum Viable Product) includes the following features:

*   **User Authentication & Profile:** Users can create a profile with their company information and portfolio, which the AI uses for context.
*   **Sales Prep Generation:** The core feature to generate detailed prep reports.
*   **Smart Caching:** A system to cache company research data to improve performance and reduce costs.
*   **Confidence Scoring:** Each section of the prep report will have a confidence score to indicate the reliability of the information.
*   **Export Options:** Users can export reports to PDF.
*   **Dashboard & History:** A dashboard to view past preps and track meeting outcomes.
*   **Feedback Loop:** Users can provide feedback on the accuracy and usefulness of the prep reports.

## Development Conventions

### Coding Style

*   **Backend (Python):** Adhere to the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
*   **Frontend (TypeScript):** Adhere to the [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html).

### Best Practices

*   **Test-Driven Development (TDD):** Development should follow a TDD approach. Write tests before writing the implementation code.
*   **Continuous Integration (CI):** A CI pipeline should be set up to run tests and linting on every commit.
*   **Code Reviews:** Code reviews are mandatory for all pull requests.
*   **Documentation:** Maintain clear and concise documentation for all code and features.
*   Use async functions for asynchronous operations.

## Development Setup (TODO)

The project is not yet initialized. Here are the proposed steps to set up the development environment:

### Backend (FastAPI)

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
2.  **Install dependencies:**
    ```bash
    # TODO: add dependencies from the PRD
    uv add ...
    ```
3.  **Configure environment variables:**
    ```bash
    # TODO: Create a .env.example file
    cp .env.example .env
    ```

### Frontend (Next.js)

1.  **Initialize Next.js app:**
    ```bash
    pnpm create next-app@latest frontend --typescript --tailwind --eslint
    ```
2.  **Install additional dependencies:**
    ```bash
    # TODO: Add dependencies like shadcn/ui
    cd frontend && pnpm install
    ```

## Building and Running (TODO)

### Backend

```bash
# TODO: Confirm run command
uvicorn backend.main:app --reload
```

### Frontend

```bash
# TODO: Confirm run command
cd frontend && pnpm run dev
```
