# Phase 5: Finishing Touches

Let's add the final features to make this a complete product.

*   **Step 1: PDF Export**
    *   **What it is:** A feature to let users download their prep reports as PDFs.
    *   **Your task:**
        *   On the backend, create the `POST /api/preps/{id}/export/pdf` endpoint. Use the ReportLab library to generate a PDF from the prep data.
        *   On the frontend, add an "Export to PDF" button to the prep report page.

*   **Step 2: The Feedback Loop**
    *   **What it is:** A way for users to give feedback on how their meetings went.
    *   **Your task:**
        *   Create the "Record Outcome" modal on the frontend.
        *   Create the `POST /api/preps/{id}/outcome` endpoint on the backend to save the feedback to the `meeting_outcomes` table.
