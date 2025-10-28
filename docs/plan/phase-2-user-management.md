# Phase 2: User Authentication and Profiles

Now we'll let users sign up and manage their profiles. This is a critical step because the user's profile information is used by the AI.

*   **Step 1: Implement Sign-up and Login**
    *   **What it is:** The first thing a user sees. We'll use Supabase Auth for this.
    *   **Your task:** On the frontend, create sign-up and login pages. Use the Supabase client to handle user authentication (email/password and Google OAuth).

*   **Step 2: Create the User Profile Page**
    *   **What it is:** A page where users can enter their company information, portfolio, etc.
    *   **Your task:**
        *   Build the UI for the user profile page in Next.js. Use `shadcn/ui` components to make it look good.
        *   Create the backend API endpoints (`POST` and `GET` for `/api/auth/profile`) that will handle creating, reading, and updating user profiles in the database.
        *   Connect the frontend page to the backend API. When a user saves their profile, it should be stored in the `user_profiles` table.
