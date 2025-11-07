# Product Requirements Document: AI Sales Call Prep Assistant (MVP)

## 1. Product Overview

### 1.1 Vision
An AI-powered tool that helps SDRs, freelancers, and consultants prepare for sales calls in minutes instead of hours by intelligently researching prospects and generating personalized talking points using a tool-calling agent architecture.

### 1.2 Success Metrics
- **Primary**: 60% time savings on call preparation (measured via user feedback)
- **Secondary**:
  - 70% of users return for 2nd prep within 7 days
  - Average confidence score > 0.75 across all preps
  - Cache hit rate > 40% (cost efficiency indicator)
  - Agent completes research in < 2 minutes

### 1.3 Target Users
- **Primary**: Solo freelancers and consultants preparing for discovery/sales calls
- **Secondary**: SDRs at small companies without dedicated research tools
- **Not for**: Founders pitching their own product (different use case)

---

## 2. Core Features (MVP Scope)

### 2.1 User Authentication & Profile
**User Story**: *As a new user, I want to set up my profile once so the AI understands my context for all future preps.*

**Profile Fields**:
- **Company name** (text, required)
- **Company description** (textarea, 500 chars max, required)
  - Prompt: "Describe what your company does and your typical value proposition"
- **Industries served** (multi-select tags: SaaS, E-commerce, Healthcare, Finance, Manufacturing, Consulting, etc.)
  - User can select multiple
  - Used for industry-specific insights
- **Portfolio of past projects** (structured list, max 5 projects):
  - Project name (text, required)
  - Client industry (dropdown, required)
  - Brief description (300 chars max, required)
  - Key outcomes (text, 200 chars max, required)
    - Prompt: "What specific results did you achieve? (e.g., '15% cost reduction', '3x faster processing')"

**Acceptance Criteria**:
- Profile can be edited anytime from settings
- Profile completion is required before creating first prep
- At least 1 industry and 1 portfolio project required
- Portfolio projects stored with vector embeddings for similarity search

---

### 2.2 Create New Sales Prep (Core Workflow)

**User Story**: *As a user, I want to input meeting details and get a comprehensive prep report in under 5 minutes.*

#### **Input Fields**:

**Required**:
- **Company name** (text)
  - The prospect company you're meeting with
- **Meeting objective** (textarea, 500 chars max)
  - Free-form text describing the purpose of the call
  - Example: "Discovery call to understand their marketing challenges and introduce our content strategy services"
- **Contact person name** (text)
  - Name of the person you're meeting with
  - Used to search for decision maker profile on LinkedIn

**Optional**:
- **Contact LinkedIn URL** (text/URL)
  - Direct LinkedIn profile URL if available
  - Bypasses search, more accurate
- **Meeting date** (date picker)
  - For dashboard tracking of upcoming meetings

**UI Notes**:
- Contact fields shown in expandable "Additional Details (Optional)" section
- If user provides LinkedIn URL, name field becomes optional
- Clear help text: "Providing contact info improves research quality but is optional"

---

#### **Processing Flow**:

**Step 1: Cache Check**
- System checks if company research exists in cache
- Cache key: Normalized company name (lowercase, stripped)
- If cache is fresh (< 7 days old):
  - Load cached company data
  - Skip to Step 3
- If cache is stale or doesn't exist:
  - Proceed to Step 2

**Step 2: Research Orchestrator Agent (Agent A)**
- Agent receives:
  - Company name
  - Meeting objective
  - Contact name
  - Contact LinkedIn URL (optional)
- Agent has access to 5 tools:
  1. `web_search` - SerpAPI for general web search and finding decision makers
  2. `scrape_website` - Firecrawl for deep company page analysis
  3. `get_company_linkedin` - Apify actor for company LinkedIn page
  4. `search_linkedin_profile` - Apify actor for finding decision maker by name
  5. `scrape_linkedin_posts` - Apify actor for scrapping company recent posts
- Agent intelligently decides which tools to call and in what order
- Agent calls tools iteratively (not all at once)
- Agent analyzes results and decides if more research needed
- Agent returns structured research data with confidence scores

**Step 3: Load User Context**
- Fetch user profile from database
- Prepare portfolio summary for context

**Step 4: Sales Brief Synthesizer Agent (Agent B)**
- Agent receives:
  - Research data from Agent A (or cache)
  - User profile
  - Meeting objective
- Agent has access to 1 tool:
  - `search_portfolio` - search through user's portfolio projects for the most relevant projects based on the meeting objective
- Agent generates each section of the sales brief sequentially
- Agent calls portfolio search when it understands pain points
- Agent calculates confidence scores per section
- Agent returns complete PrepData JSON

**Step 5: Validation & Storage**
- Validate output against expected schema
- Calculate overall confidence score (weighted average)
- Save to `meeting_preps` table
- Update `company_cache` table with new research
- Store source URLs for transparency

**Step 6: Display Results**
- Render structured sales brief in UI using shadcn/ui components
- Show confidence indicators per section
- Provide export options

**Performance Target**: Entire flow completes in < 5 minutes (cache hit: < 30 seconds)

---

#### **Output Structure**

The sales brief is displayed in 6 collapsible sections:

**1. Executive Summary (The TL;DR)**
- **The Client**: [Company name + 1-sentence strategic focus]
- **Our Angle**: [How their goals align with user's portfolio - specific project matches]
- **The Goal of This Call**: [Clear objective for this specific meeting]
- **Confidence**: [Visual badge: green/yellow/red]

**2. Strategic Narrative**
- **🎯 Dream Outcome**: [What the prospect wants to achieve - their north star]
- **✅ Proof of Achievement** (Top Portfolio Matches):
  - [Project Name]: [Why it's relevant + specific result]
  - [2-3 projects maximum, ranked by relevance]
- **⏳ Pain We're Solving**:
  - [3-5 specific pain points with business impact]
  - Each pain ranked by urgency and impact
- **Confidence**: [Score]

**3. Key Talking Points & Pitch Angles**
- **Opening Hook**: [Specific observation to start conversation]
- **Core Talking Points**: [4-6 points connecting user's experience to prospect's challenges]
  - Each references specific portfolio projects when relevant
- **Leverage Their Context**: [Competitive positioning or market dynamics]
- **Confidence**: [Score]

**4. Insightful Questions to Ask**
Questions organized by category (8-12 total):
- **Strategic**: About goals, timeline, success metrics
- **Technical**: About current systems, data, processes
- **Business Impact**: About cost of inaction, stakeholders
- **Qualification**: About budget, decision process, timeline
- **Confidence**: [Score]

**5. Key Decision Maker**
- [Name, Current Title, LinkedIn URL if available]
- [2-3 background points: previous roles, interests, recent activity]
- **Note**: Only shown if contact information was provided
- **Confidence**: [Score]

**6. Company Intelligence**
- **Industry**: [Specific sector/vertical]
- **Company Size**: [Employee count estimate + revenue if available]
- **Recent News & Signals**: [3-5 recent events with dates]
  - Product launches, funding rounds, leadership changes, hiring trends
- **Strategic Initiatives**: [Current priorities based on news/job postings]
- **Confidence**: [Score]

**⚠️ Research Limitations & Red Flags** (conditionally shown)
- Only displayed if overall confidence < 0.7 or critical data missing
- Lists specific gaps: "LinkedIn profile not found - decision maker data is inferred"
- Contact verification needs: "Unable to confirm current role - verify before call"

**UI/UX Requirements**:
- Each section uses shadcn/ui Card component
- Confidence badges color-coded:
  - 🟢 High (0.8-1.0): Green
  - 🟡 Medium (0.6-0.79): Yellow
  - 🔴 Low (0.0-0.59): Red
- Sections collapsible on mobile
- Copy-to-clipboard button per section
- Overall prep confidence displayed prominently at top
- Export buttons (PDF, Copy All) at top and bottom

---

### 2.3 Smart Caching System

**User Story**: *As a power user, I want the system to reuse recent company research to save time and costs.*

**How It Works**:
- After Agent A completes research, data is stored in `company_cache` table
- Cache key: Normalized company name
- Cache includes:
  - Company intelligence data
  - Decision maker profiles (if found)
  - Recent news items
  - Source URLs
  - Confidence score
  - Last updated timestamp
- **TTL**: 7 days from last update

**Cache Behavior**:
- Before Agent A runs, system checks cache
- If cache exists and is fresh (< 7 days):
  - Load cached data
  - Display "Using cached data from [date]" badge
  - Skip directly to Agent B (synthesis)
- If cache is stale (> 7 days):
  - Run Agent A to refresh
  - Update cache with new data
- User can manually force refresh with "Update Research" button

**Benefits**:
- Reduces prep time from 2 min → 30 sec (cache hit)
- Saves API costs (Firecrawl, Apify, LLM tokens)
- Target cache hit rate: 40%+

**Acceptance Criteria**:
- Cache check happens automatically before research
- Cache hit clearly indicated to user
- Manual refresh option always available
- Stale cache automatically triggers refresh

---

### 2.4 Confidence Scoring System

**User Story**: *As a user, I want to know how reliable each insight is so I can prepare backup talking points for low-confidence areas.*

**Scoring Approach**:
Each section of the sales brief gets an independent confidence score (0.0-1.0).

**Scoring Logic by Section**:

**Executive Summary** (0.0-1.0):
- Based on completeness of research data
- Higher if both company data and decision maker found
- Lower if limited to web search only

**Strategic Narrative** (0.0-1.0):
- Based on portfolio project match quality
- Higher if multiple high-relevance projects (similarity > 0.8)
- Lower if no portfolio or weak matches

**Talking Points** (0.0-1.0):
- Based on alignment between pain points and portfolio
- Higher if specific metrics/outcomes available
- Lower if generic industry insights only

**Questions to Ask** (0.8-1.0):
- Always high (generated from proven frameworks)
- Not data-dependent

**Decision Makers** (0.0-1.0 or N/A):
- N/A if no contact info provided
- High (0.85-0.95) if LinkedIn profile scraped directly
- Medium (0.6-0.79) if found via search
- Low (0.3-0.59) if inferred from job title/web mentions only

**Company Intelligence** (0.0-1.0):
- Based on data freshness and source quality
- Higher if recent news (< 30 days) and multiple sources
- Lower if only website data or old news

**Overall Confidence** (0.0-1.0):
- Weighted average of all section scores
- Formula:
  ```
  overall = (
    executive_summary * 0.15 +
    strategic_narrative * 0.25 +
    talking_points * 0.20 +
    questions * 0.10 +
    decision_makers * 0.15 +  (0 if N/A)
    company_intelligence * 0.15
  )
  ```

**Visual Indicators**:
- Each section shows confidence badge with color
- Tooltip on hover explains score factors
- Low overall confidence (< 0.7) triggers warning banner:
  - "Research confidence is moderate - some data may be incomplete"
  - Lists specific gaps in Research Limitations section

**Acceptance Criteria**:
- Every section displays confidence score
- Overall score calculated correctly
- Low scores trigger actionable warnings
- Confidence scores persisted for post-meeting analysis

---

### 2.5 Export Options

**User Story**: *As a user, I want to export my prep report so I can reference it during the call without switching apps.*

**Export Formats**:

**1. PDF Export** (Priority 1)
- Library: ReportLab (Python)
- Generation approach: Programmatic (no HTML templates)
- Layout:
  - Header: Company name + Meeting date + Overall confidence badge
  - Six main sections in order
  - Confidence indicators as colored text/boxes
  - Footer: "Generated by [App Name] on [date]"
- Simple, clean design (black text, white background, minimal styling)
- Stored in Supabase Storage bucket with 30-day retention
- Download link provided immediately after generation
- File naming: `[date]-[company_name]-sales_prep.pdf`

**2. Copy to Clipboard** (Priority 2)
- Formatted markdown version of entire prep
- Preserves structure with headers (##), bullet points, bold text
- User can paste into Notion, Google Docs, email, Obsidian, etc.
- Toast notification confirms successful copy
- Button text: "Copy as Markdown"

**UI Placement**:
- Export buttons in sticky header when viewing prep
- Also at bottom of prep report
- shadcn/ui Button component with icons

**Acceptance Criteria**:
- PDF generates in < 5 seconds
- PDF is mobile-readable (responsive layout)
- Copy button provides immediate feedback
- PDF stored securely (only accessible to owner via signed URL)

---

### 2.6 Dashboard & Meeting History

**User Story**: *As a returning user, I want to see my past preps and track which ones led to successful meetings.*

**Dashboard Layout**:

**Top Section: Stats Overview** (4 cards)
- **Total Preps**: [Count of all preps created]
- **Success Rate**: [% of meetings marked as "successful"]
  - Only counts completed meetings with recorded outcomes
- **Avg Confidence**: [Average overall confidence across all preps]
  - Visual: Progress bar or gauge
- **Est. Time Saved**: [Total hours saved]
  - Calculation: Number of preps × 18 minutes (60% of assumed 30 min)
  - Display: "42 hours saved" with tooltip explaining calculation

**Middle Section: Upcoming Meetings** (if meeting dates set)
- Shows preps with meeting_date in next 7 days
- Sorted by date (soonest first)
- Each row shows:
  - Company name
  - Meeting date
  - Meeting objective (truncated)
  - Quick action: "View Prep" button
- Limit: 5 upcoming meetings shown

**Bottom Section: Recent Preps** (Table View)
- Columns:
  - **Company**: [Name, clickable]
  - **Objective**: [First 50 chars...]
  - **Created**: [Relative time: "2 days ago"]
  - **Confidence**: [Badge with color]
  - **Status**: [Badge]
    - "Pending" (default, gray)
    - "Meeting Done" (blue)
    - "Outcome Recorded" (green)
  - **Actions**: [Dropdown menu]
    - View
    - Export PDF
    - Record Outcome
    - Delete
- Pagination: 10 preps per page
- Filters:
  - Date range picker
  - Status dropdown (All, Pending, Completed)
  - Search by company name
- Default sort: Created date DESC (newest first)

**Empty States**:
- No preps yet: "Create your first sales prep to get started" + CTA button
- No upcoming meetings: "No scheduled meetings in the next 7 days"

**Acceptance Criteria**:
- Dashboard loads in < 1 second
- Stats update immediately after new prep created
- Clicking company name opens prep detail view
- Filters work without page reload (client-side)
- Mobile responsive (cards stack vertically)

---

### 2.7 Meeting Feedback Loop

**User Story**: *As a user, I want to record how my meeting went so the system learns what works and I can track my success rate.*

**Feedback Collection Flow**:

**Trigger**: User clicks "Record Outcome" from dashboard or prep detail view

**Modal Form** (shadcn/ui Dialog component):

**Field 1: Meeting Status** (Radio buttons, required)
- ○ Completed
- ○ Cancelled
- ○ Rescheduled

**Fields 2-6** (only shown if "Completed" selected):

**2. Outcome** (Radio buttons, required)
- ○ Successful (positive progress made)
- ○ Needs Improvement (neutral, learning opportunity)
- ○ Lost Opportunity (decided not to move forward)

**3. Prep Accuracy** (Star rating, required)
- ⭐⭐⭐⭐⭐ (1-5 stars)
- Label: "How accurate was the research?"

**4. Most Useful Section** (Dropdown, required)
- Executive Summary
- Strategic Narrative
- Talking Points
- Questions to Ask
- Decision Makers
- Company Intelligence

**5. What Was Missing?** (Textarea, optional, 200 chars)
- Placeholder: "Was there anything important the research missed?"

**6. General Notes** (Textarea, optional, 500 chars)
- Placeholder: "Any other observations about the meeting or prep quality?"

**Actions**:
- [Cancel] button (secondary)
- [Save Outcome] button (primary)

**After Submission**:
- Success toast: "Outcome recorded"
- Modal closes
- Dashboard stats update immediately
- Prep status changes to "Outcome Recorded"

**Editing**:
- User can edit outcome anytime
- Click "Edit Outcome" from prep detail view
- Same modal, pre-filled with existing data

**Data Usage**:
- Calculate success rate for dashboard
- Track most useful sections (inform future improvements)
- Identify patterns (e.g., certain industries = lower accuracy)
- **V2 Feature**: Use feedback to fine-tune prompts/agents

**Acceptance Criteria**:
- Feedback can be submitted within 30 seconds
- Feedback can be edited after submission
- Only "Completed" meetings count toward success rate
- Dashboard updates reflect new outcome immediately
- Optional fields can be skipped

---

## 3. Technical Architecture

### 3.1 Tech Stack

**Frontend**:
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Deployment: Vercel

**Backend**:
- FastAPI (Python 3.11+)
- Pydantic AI (agent framework)
- Deployment: Railway or Render

**AI & APIs**:
- **Primary LLM**: Google Gemini 2.5 Pro
- **Web Search**: SerpAPI or Brave Search API
- **Web Scraping**: Firecrawl API
- **LinkedIn Scraping**: Apify (two actors)
  - `icypeas_official/linkedin-profile-scraper`
  - `scrapeverse/linkedin-company-profile-scraper`
  - `supreme_coder/linkedin-post`

**Database & Auth**:
- Supabase (Postgres + Auth + Storage)
- Row-Level Security (RLS) enabled on all tables

**Observability**:
- Pydantic Logfire (future phase - not MVP)

---

### 3.2 Agent Architecture

**Two-Agent System with Tool-Calling**

This architecture uses **intelligent tool-calling** instead of pre-fetching all data. Agents decide which tools to call and when, based on the information they've gathered so far.

---

#### **Agent A: Research Orchestrator**

**Purpose**: Intelligently gather data about the prospect company and decision maker.

**Model**: Gemini 2.5 flash

**Input**:
- Company name (required)
- Meeting objective (required)
- Contact person name (required)
- Contact LinkedIn URL (optional)

**Available Tools** (5 tools):

1. **web_search**
   - Purpose: General web search for company info, news, trends
   - API: SerpAPI or Brave Search
   - When to use: Company overview, recent news, industry research
   - Example query: "Flexport logistics news 2025"

2. **scrape_website**
   - Purpose: Deep scrape company website for detailed info
   - API: Firecrawl
   - When to use: Company services, team info, blog posts
   - Example target: Company's about page, services page

3. **get_company_linkedin**
   - Purpose: Scrape company LinkedIn page
   - API: Apify (`scrapeverse/linkedin-company-profile-scraper`)
   - When to use: Company size, industry, recent posts, job openings
   - Returns: Employee count, headquarters, recent activity, hiring signals

4. **scrape_linkedin_post**
   - Purpose: Scrape LinkedIn post by profile URL
   - API: Apify (`apify/linkedin-post-scraper`)
   - When to use: User provided LinkedIn post URL
   - Returns: Post details with high confidence

5. **scrape_linkedin_profile_url**
   - Purpose: Scrape specific LinkedIn profile by URL
   - API: Apify (`icypeas_official/linkedin-profile-scraper`)
   - When to use: User provided direct LinkedIn URL
   - Returns: Profile details with high confidence

**Behavior**:
- Agent receives input and decides which tools to call first
- Agent makes iterative tool calls (not all at once)
- Agent analyzes each tool result before deciding next action
- Agent stops when sufficient context gathered
- Agent assigns confidence scores to collected data
- Agent returns structured research package

**Typical Tool Call Sequence Example**:
```
1. Agent thinks: "Need basic company info"
   → Calls: web_search("Company X overview")

2. Agent analyzes: "Found website URL, need more details"
   → Calls: scrape_website("companyX.com")

3. Agent analyzes: "Website mentions 500+ employees, verify size"
   → Calls: get_company_linkedin("Company X")

4. Agent analyzes: "User provided contact name 'Jane Smith', find her"
   → Calls: search_linkedin_profile("Jane Smith", "Company X")

5. Agent analyzes: "Found profile, sufficient data collected"
   → Returns research package
```

**Output Structure**:
```
{
  "company_intelligence": {
    "name": str,
    "industry": str,
    "company_size": str,
    "website": str,
    "description": str,
    "recent_news": [
      {"headline": str, "date": str, "significance": str}
    ],
    "strategic_initiatives": [str],
    "job_openings_count": int,
    "confidence": float
  },
  "decision_makers": [
    {
      "name": str,
      "title": str,
      "linkedin_url": str | null,
      "background": str,
      "recent_activity": [str],
      "confidence": float
    }
  ],
  "research_limitations": [str],
  "overall_confidence": float,
  "sources_used": [str],
  "cache_status": "fresh" | "stale" | "miss"
}
```

**Error Handling**:
- If tool fails, agent tries alternative approach
- Example: Firecrawl fails → use web_search instead
- Example: Apify rate limit → note in limitations, continue without LinkedIn data
- Agent never stops completely; returns best available data

---

#### **Agent B: Sales Brief Synthesizer**

**Purpose**: Generate structured sales brief from research data and user context.

**Model**: Gemini 2.5 Pro
**Input**:
- Research data from Agent A (or cache)
- User profile (company, description, industries, portfolio)
- Meeting objective

**Available Tools** (1 tool):

1. **search_portfolio**
   - Purpose: Vector similarity search through user's portfolio projects
   - Search query: Combines prospect's pain points + industry + required services
   - Returns: Top 5 most relevant projects with relevance scores
   - When to use: After understanding prospect's challenges, to find matching case studies

**Behavior**:
- Agent receives all context at once
- Agent generates sales brief section by section in order:
  1. Executive Summary
  2. Strategic Narrative (calls search_portfolio here)
  3. Talking Points
  4. Questions to Ask
  5. Decision Makers (if available)
  6. Company Intelligence
- Agent calculates confidence score for each section
- Agent flags research limitations if confidence < 0.7
- Agent returns complete PrepData JSON

**Generation Strategy**:
- Agent first identifies prospect's pain points from research
- Agent then calls search_portfolio to find relevant user projects
- Agent creates talking points connecting portfolio projects to pain points
- Agent references specific portfolio projects by name throughout brief

**Output Structure**:
```
{
  "executive_summary": {
    "the_client": str,
    "our_angle": str,
    "call_goal": str,
    "confidence": float
  },
  "strategic_narrative": {
    "dream_outcome": str,
    "proof_of_achievement": [
      {"project_name": str, "relevance": str, "relevance_score": float}
    ],
    "pain_points": [
      {"pain": str, "urgency": int, "impact": int, "evidence": [str]}
    ],
    "confidence": float
  },
  "talking_points": {
    "opening_hook": str,
    "key_points": [str],
    "competitive_context": str,
    "confidence": float
  },
  "questions_to_ask": {
    "strategic": [str],
    "technical": [str],
    "business_impact": [str],
    "qualification": [str],
    "confidence": float
  },
  "decision_makers": {
    "profiles": [
      {"name": str, "title": str, "linkedin_url": str, "background_points": [str]}
    ] | null,
    "confidence": float
  },
  "company_intelligence": {
    "industry": str,
    "company_size": str,
    "recent_news": [
      {"headline": str, "date": str, "significance": str}
    ],
    "strategic_initiatives": [str],
    "confidence": float
  },
  "research_limitations": [str],
  "overall_confidence": float,
  "sources": [str]
}
```

**Error Handling**:
- If section generation fails, retry once
- If retry fails, use generic template for that section
- Mark low confidence and note in limitations

---

### 3.3 Project Structure

**Backend Directory Structure**:
```
app/
├── main.py                    # FastAPI app entry point
├── config.py                  # Environment variables, settings
├── routes/
│   ├── auth.py               # Auth routes (handled by Supabase mostly)
│   ├── profiles.py           # User profile CRUD
│   ├── preps.py              # Main prep creation/retrieval routes
│   ├── outcomes.py           # Meeting outcome recording
│   └── dashboard.py          # Dashboard stats queries
├── agents/
│   ├── research_orchestrator/
│   │   ├── agent.py          # Agent A definition and system prompt
│   │   └── tools/
│   │       ├── web_search.py         # Tool 1
│   │       ├── scrape_website.py     # Tool 2
│   │       ├── scrape_company_linkedin.py   # Tool 3
│   │       ├── scrape_linkedin_profile.py  # Tool 4
│   │       └── scrape_likedin_posts.py  # Tool 5
│   └── sales_synthesizer/
│       ├── agent.py          # Agent B definition and system prompt
│       └── tools/
│           └── search_portfolio.py   # Tool 1
├── services/
│   ├── apify_service.py      # Apify client wrapper
│   ├── firecrawl_service.py  # Firecrawl client wrapper
│   ├── search_service.py     # SerpAPI/Brave client wrapper
│   ├── supabase_service.py   # Supabase client
│   ├── cache_service.py      # Cache management logic
│   └── pdf_service.py        # PDF generation with ReportLab
├── models/
│   ├── prep_schemas.py       # Pydantic models for validation
│   └── user_schemas.py       # User profile schemas
├── utils/
│   ├── confidence_calculator.py  # Confidence scoring logic
│   └── validators.py         # Input validation helpers
└── tests/
    ├── test_agents.py
    ├── test_tools.py
    └── test_routes.py
```

**Key Principles**:
- Each agent has its own folder
- Tools are isolated in subfolders per agent
- Services handle external API interactions
- Clear separation: routes → agents → tools → services

---

### 3.4 Database Schema Requirements

**Design Principles**:
- Row-Level Security (RLS) enabled on all tables
- Users can only access their own data (except shared cache)
- JSONB used for flexible AI output storage
- Indexes on foreign keys and frequently queried columns
- Timestamps for all records

**Required Tables**:

#### **1. user_profiles**
Extends Supabase auth.users with business context.

**Key Fields**:
- `id` (UUID, primary key, references auth.users)
- `company_name` (text, required)
- `company_description` (text, max 500 chars, required)
- `industries_served` (text array, required, at least 1)
- `portfolio` (JSONB array, required, max 5 items)
  - Structure: `[{name, client_industry, description, key_outcomes}, ...]`
- `created_at`, `updated_at` (timestamps)

**RLS Policy**:
- Users can only read/write their own profile
- Policy: `auth.uid() = id`

**Indexes**:
- Primary key on `id` (automatic)

---

#### **2. meeting_preps**
Stores generated sales prep reports.

**Key Fields**:
- `id` (UUID, primary key)
- `user_id` (UUID, foreign key to auth.users, required)
- `company_name` (text, required)
- `company_name_normalized` (text, lowercase for cache lookups)
- `meeting_objective` (text, required)
- `meeting_date` (date, nullable)
- `contact_person_name` (text, nullable)
- `contact_linkedin_url` (text, nullable)
- `prep_data` (JSONB, required) - Full structured output
- `overall_confidence` (float, 0.0-1.0, required)
- `cache_hit` (boolean, default false)
- `pdf_url` (text, nullable) - Supabase Storage signed URL
- `created_at` (timestamp)

**RLS Policy**:
- Users can only access their own preps
- Policy: `auth.uid() = user_id`

**Indexes**:
- `user_id + created_at DESC` (dashboard queries)
- `meeting_date` (upcoming meetings)
- `company_name_normalized` (duplicate detection)

**Constraints**:
- `overall_confidence CHECK (overall_confidence >= 0 AND overall_confidence <= 1)`

---

#### **3. meeting_outcomes**
Captures user feedback on meeting results.

**Key Fields**:
- `id` (UUID, primary key)
- `prep_id` (UUID, foreign key to meeting_preps, UNIQUE)
- `meeting_status` (enum: 'completed', 'cancelled', 'rescheduled', required)
- `outcome` (enum: 'successful', 'needs_improvement', 'lost_opportunity', nullable)
  - Required only if meeting_status = 'completed'
- `prep_accuracy` (integer, 1-5, nullable)
- `most_useful_section` (enum: 'executive_summary', 'strategic_narrative', 'talking_points', 'questions', 'decision_makers', 'company_intelligence', nullable)
- `what_was_missing` (text, max 200 chars, nullable)
- `general_notes` (text, max 500 chars, nullable)
- `created_at`, `updated_at` (timestamps)

**RLS Policy**:
- Users can only access outcomes for their own preps
- Policy: `auth.uid() = (SELECT user_id FROM meeting_preps WHERE id = prep_id)`

**Indexes**:
- `prep_id` (unique, automatic foreign key index)

**Constraints**:
- `prep_accuracy CHECK (prep_accuracy BETWEEN 1 AND 5)`
- `outcome` required when `meeting_status = 'completed'`

---

#### **4. company_cache**
Stores reusable company research data (shared across users).

**Key Fields**:
- `company_name_normalized` (text, primary key)
- `company_data` (JSONB, required) - Raw research from Agent A
  - Structure: `{industry, size, description, recent_news, decision_makers, scraped_urls, ...}`
- `confidence_score` (float, 0.0-1.0, required)
- `last_updated` (timestamp, required)
- `source_urls` (text array) - Audit trail

**RLS Policy**:
- All authenticated users can READ (shared cache)
- Only service role can WRITE (backend API only)
- Read Policy: `auth.role() = 'authenticated'`
- Write Policy: `auth.role() = 'service_role'`

**Indexes**:
- `last_updated DESC` (for cache invalidation queries)

**Constraints**:
- `confidence_score CHECK (confidence_score >= 0 AND confidence_score <= 1)`

**TTL Logic** (implemented in application, not database):
- Cache is stale if `NOW() - last_updated > INTERVAL '7 days'`
- Stale cache triggers Agent A refresh

---

#### **5. api_usage_logs**
Tracks API consumption for cost monitoring.

**Key Fields**:
- `id` (UUID, primary key)
- `user_id` (UUID, foreign key to auth.users, nullable)
- `prep_id` (UUID, foreign key to meeting_preps, nullable)
- `operation` (enum: 'company_research', 'prep_generation', 'cache_hit', 'pdf_export')
- `provider` (enum: 'gemini', 'claude', 'firecrawl', 'serpapi', 'brave', 'apify')
- `tokens_used` (integer, nullable) - For LLM calls
- `cost_usd` (decimal, nullable) - Calculated cost
- `duration_ms` (integer) - Operation latency
- `success` (boolean)
- `error_message` (text, nullable)
- `created_at` (timestamp)

**RLS Policy**:
- Users can view their own usage
- Admins can view all usage
- Policy: `auth.uid() = user_id OR auth.role() = 'service_role'`

**Indexes**:
- `user_id + created_at DESC` (user cost dashboards)
- `created_at DESC` (admin monitoring)
- `operation` (aggregate queries)

**Analytics Queries Enabled**:
- Daily cost by provider
- Cache hit rate (operations = 'cache_hit' vs 'company_research')
- Average prep generation time
- Error rate by tool/provider

---

#### **6. portfolio_embeddings** (optional, if using vector search)
Stores vector embeddings for portfolio projects.

**Key Fields**:
- `id` (UUID, primary key)
- `user_id` (UUID, foreign key to auth.users, required)
- `project_index` (integer) - Index in user's portfolio array (0-4)
- `embedding` (vector, dimension 1536 or 768) - From OpenAI/other embedding model
- `project_data` (JSONB) - Denormalized project for fast retrieval
- `created_at`, `updated_at` (timestamps)

**RLS Policy**:
- Users can only access their own embeddings
- Policy: `auth.uid() = user_id`

**Indexes**:
- `user_id` (for user-scoped searches)
- Vector index on `embedding` column (for similarity search)

**Alternative**: Store embeddings in `user_profiles.portfolio` JSONB directly if using external vector DB (Pinecone, Qdrant).

---

### 3.5 Data Flow Summary

**Complete Request Flow**:

1. **User submits request** via frontend form
2. **API receives request** at `POST /api/preps`
3. **Validate input** (Pydantic schemas)
4. **Check cache** (`company_cache` table)
5. **If cache miss or stale**:
   - Instantiate Agent A (Research Orchestrator)
   - Agent A calls tools iteratively:
     - `web_search` → Company overview, news
     - `scrape_website` → Company details
     - `get_company_linkedin` → Company size, activity
     - `search_linkedin_profile` (if contact name provided)
     - Or `scrape_linkedin_profile_url` (if LinkedIn URL provided)
   - Agent A returns research data
   - Save to `company_cache`
6. **If cache hit**: Load cached data
7. **Load user context** from `user_profiles`
8. **Instantiate Agent B** (Sales Brief Synthesizer)
9. **Agent B generates sales brief**:
   - Analyzes research + user context
   - Calls `search_portfolio` tool
   - Generates each section with confidence scores
   - Returns complete PrepData JSON
10. **Validate output** against PrepData schema
11. **Calculate overall confidence** (weighted average)
12. **Save to database**:
    - Insert into `meeting_preps`
    - Log API usage to `api_usage_logs`
13. **Return response** to frontend
14. **Frontend displays** structured sales brief
15. **User can export** (PDF/Markdown) or record outcome later

**Timing Breakdown**:
- Cache check: < 100ms
- Agent A (cache miss): 60-90 seconds
- Agent B: 30-40 seconds
- Validation + save: < 1 second
- **Total (cache miss)**: ~2 minutes
- **Total (cache hit)**: ~30 seconds
