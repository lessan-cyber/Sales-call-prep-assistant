# Phase 1: The Foundation

This phase is all about setting up our project structure and getting the basic services online. A solid foundation makes everything else easier.

*   **Step 1: Set up Supabase**
    *   **What it is:** Supabase is our backend-as-a-service. It gives us a Postgres database, user authentication, and file storage without having to build it all from scratch.
    *   **Your task:** Create a new project on Supabase. You'll get API keys and a database URL. Keep these handy and store them securely as environment variables.

*   **Step 2: Initialize the Database Schema**
    *   **What it is:** We need to create the tables in our database that will store our data.
    *   **Your task:** Using the `PRD.md` as a guide, write the SQL statements to create the `user_profiles`, `meeting_preps`, `meeting_outcomes`, `company_cache`, and `api_usage_logs` tables. Pay close attention to the column types, relationships, and security rules (RLS).

*   **Step 3: Initialize the Frontend and Backend Projects**
    *   **What they are:** We'll have two main codebases: a Next.js app for the user interface (frontend) and a FastAPI app for our server logic (backend).
    *   **Your task:**
        *   In the `frontend` directory, initialize a new Next.js project using `pnpm`.
        *   In the `backend` directory, set up a new FastAPI project with a virtual environment.

*   **Step 4: Connect Everything**
    *   **What it is:** Our frontend and backend need to be able to talk to Supabase.
    *   **Your task:**
        *   Install the Supabase client library in both the frontend and backend projects.
        *   Use the environment variables from Step 1 to configure the clients.
        *   Create a simple test to ensure you can connect to the database from both projects.
