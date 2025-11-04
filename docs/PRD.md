# Product Requirements Document: AI Sales Call Prep Assistant (MVP)

## 1. Product Overview

### 1.1 Vision
An AI-powered tool that helps SDRs, freelancers, and consultants prepare for sales calls in minutes instead of hours by automatically researching prospects and generating personalized talking points.

### 1.2 Success Metrics
- **Primary**: 60% time savings on call preparation (measured via user feedback)
- **Secondary**:
  - 70% of users return for 2nd prep within 7 days
  - Average confidence score > 0.75 across all preps
  - Cache hit rate > 40% (cost efficiency indicator)

### 1.3 Target Users
- **Primary**: Solo freelancers and consultants preparing for discovery/sales calls
- **Secondary**: SDRs at small companies without dedicated research tools
- **Not for**: Founders pitching their own product (different use case)

---

## 2. Core Features (MVP Scope)

### 2.1 User Authentication & Profile
**User Story**: *As a new user, I want to set up my profile once so the AI understands my context for all future preps.*

**Requirements**:
- Supabase Auth (Email/Password + Google OAuth)
- Profile fields:
  - Company name (text, required)
  - Industries served (multi-select tags: SaaS, E-commerce, Healthcare, Finance, Manufacturing, etc.)
  - Portfolio of past projects (structured list):
    - Project name
    - Client industry
    - Brief description (50 chars max)
    - Max 10 projects
  - Company description (textarea, 200 chars, required)
    - Prompt: "Describe what your company does and your typical value proposition"

**Acceptance Criteria**:
- Profile can be edited anytime from settings
- Profile completion is required before creating first prep
- AI agents receive this context in every prep generation

---

### 2.2 Create New Sales Prep
**User Story**: *As a user, I want to input a company name and meeting objective and get a comprehensive prep report in under 2 minutes.*

**Input Fields**:
- Company name (text, required)
- Company website (text, optional)
- Meeting objective (textarea, 500 chars, required)
  - Placeholder: "e.g., Discovery call to understand their marketing challenges and introduce our content strategy services"
- Meeting date (optional, for dashboard tracking)

**Processing Flow**:
1. Check company cache (< 7 days old)
2. If cache miss or stale:
   - Run web search for company overview + recent news
   - Search for decision-maker profiles (LinkedIn data)
   - Store results in cache with timestamp
3. Load user profile context
4. Generate structured output via Pydantic AI
5. Calculate confidence scores per section
6. Save to database + update cache

**Output Structure** (displayed in clean UI with shadcn/ui components):

```
1️⃣ EXECUTIVE SUMMARY (The TL;DR)
- The Client: [Company name + 1-sentence description of their strategic focus]
- Our Angle: [How their goals align with user's portfolio - specific project matches]
- The Goal of This Call: [Clear objective for this specific meeting]
- Confidence: [0.0-1.0 score with visual indicator]

2️⃣ STRATEGIC NARRATIVE
🎯 Dream Outcome: [What the prospect wants to achieve - their north star goal]

✅ Proof of Achievement (Top Portfolio Matches):
- [Project Name from user's portfolio]: [Why it's relevant + specific metric/result]
- [2-3 projects maximum, each with clear connection to prospect's needs]

⏳ Pain We're Solving:
- [3-5 specific pain points they're experiencing]
- [Connect each pain to business impact: revenue, cost, time, reputation]
- Confidence: [score]

3️⃣ KEY TALKING POINTS & PITCH ANGLES
- Opening Hook: [Specific observation about their company to start conversation]
- [4-6 talking points that connect user's experience to prospect's challenges]
- [Each point references specific portfolio projects when relevant]
- Leverage Their Context: [Competitive positioning or market dynamics insight]
- Confidence: [score]

4️⃣ INSIGHTFUL QUESTIONS TO ASK
- [8-12 discovery questions organized by type:]
  * Strategic questions (about goals, timeline, success metrics)
  * Technical questions (about current systems, data, processes)
  * Business impact questions (about cost of inaction, stakeholders)
  * Qualification questions (about budget, decision process, timeline)
- Confidence: [score]

5️⃣ KEY DECISION MAKERS
- [Name, Current Title, LinkedIn URL if available]
- [2-3 background points: previous roles, interests, recent activity]
- [Up to 3 decision makers, prioritized by relevance]
- Confidence: [score]

6️⃣ COMPANY INTELLIGENCE
- Industry: [Specific sector/vertical]
- Company Size: [Employee count estimate + revenue if available]
- Recent News & Signals: [3-5 recent events, hiring trends, product launches with dates]
- Strategic Initiatives: [Current priorities based on news/job postings]
- Confidence: [score]

⚠️ RESEARCH LIMITATIONS & RED FLAGS
- [Any data gaps, uncertainty about decision makers, or contact verification needs]
- [Only shown if confidence < 0.7 in any section or critical data is missing]
```

**UI/UX Notes**:
- Use shadcn/ui Card components for each section
- Confidence scores as Badge components with color coding (green/yellow/red)
- Collapsible sections for mobile responsiveness
- Copy-to-clipboard button for each section
- Overall prep confidence displayed prominently at top

**Acceptance Criteria**:
- Entire process completes in < 2 minutes
- All sections include confidence scores
- Low confidence triggers visible warning
- Results are immediately saved to database
- Cache is updated with 7-day TTL

---

### 2.3 Smart Caching System
**User Story**: *As a power user, I want the system to reuse recent company research to save time and costs.*

**Requirements**:
- Separate `company_cache` table in Supabase
- Cache key: Normalized company name (lowercase, stripped)
- Cache stores:
  - Company overview data
  - Decision maker profiles
  - News items
  - Last updated timestamp
  - Confidence score
- TTL: 7 days
- Cache hit displays "Using cached data from [date]" badge

**Acceptance Criteria**:
- Cache check happens before any API calls
- Users can manually "Refresh data" to bypass cache
- Cache hit reduces prep time to < 30 seconds
- Stale cache (> 7 days) triggers automatic refresh

---

### 2.4 Confidence Scoring
**User Story**: *As a user, I want to know how reliable each insight is so I can prepare backup talking points for low-confidence areas.*

**Scoring Logic**:
- **Company Overview**: Based on data freshness + source quality
- **Decision Makers**: Based on number of profiles found + data completeness
- **Pain Points**: Based on industry match + recent news relevance
- **Talking Points**: Based on portfolio project relevance + pain point alignment
- **Questions**: Always high (generated from proven frameworks)

**Confidence Levels**:
- 🟢 High (0.8-1.0): Strong data, recent sources
- 🟡 Medium (0.6-0.79): Partial data, needs validation
- 🔴 Low (0.0-0.59): Limited data, manual research recommended

**Visual Indicators**:
- Color-coded badges per section
- Tooltip explaining score factors
- Warning banner if overall prep confidence < 0.7

**Acceptance Criteria**:
- Every section displays confidence score
- Low scores trigger actionable recommendations
- Scores are persisted for post-meeting analysis

---

### 2.5 Export Options
**User Story**: *As a user, I want to export my prep report so I can reference it during the call without switching apps.*

**Export Formats**:
1. **PDF Export** (Priority 1)
   - Clean, professional layout
   - Company logo header (if available)
   - Table of contents with jump links
   - Confidence indicators preserved
   - Footer: "Generated by [App Name] on [date]"
   - Library: ReportLab or WeasyPrint

2. **Notion Export** (Priority 2)
   - ~~One-click "Send to Notion"~~
   - ~~Creates new page in user's connected Notion workspace~~
   - ~~Preserves structure with Notion blocks~~
   - ~~Requires Notion OAuth integration~~
   - **REMOVED FROM MVP** (OAuth complexity, can be V2 feature)
   - Fallback: Copy formatted markdown for manual paste

**Acceptance Criteria**:
- PDF generates in < 5 seconds
- PDF is mobile-readable
- Notion export requires one-time OAuth setup
- Export button prominently displayed on prep view

---

### 2.6 Dashboard & Meeting History
**User Story**: *As a returning user, I want to see my past preps and track which ones led to successful meetings.*

**Dashboard Layout**:
```
📈 STATS OVERVIEW (Top Cards)
- Total Preps: [count]
- Success Rate: [% of meetings marked successful]
- Avg Confidence: [0.0-1.0]
- Est. Time Saved: [hours] (based on 60% reduction from assumed 30min/prep)

📅 UPCOMING MEETINGS (If meeting dates set)
- Next 7 days, sorted by date
- Quick access to prep reports

📋 RECENT PREPS (Table View)
- Columns: Company | Objective (truncated) | Created | Confidence | Status | Actions
- Status: Pending / Meeting Done / Outcome Recorded
- Actions: View, Export, Record Outcome
- Pagination: 10 per page
- Filter: By date range, by status
```

**Acceptance Criteria**:
- Dashboard loads in < 1 second
- Stats update in real-time after new prep
- Clicking prep opens detailed view
- Search/filter functionality works across all preps

---

### 2.7 Meeting Feedback Loop
**User Story**: *As a user, I want to record how my meeting went so the system learns what works and I can track my success rate.*

**Feedback Flow**:
1. User opens past prep
2. Clicks "Record Outcome" button
3. Modal appears:
   - **Meeting Status**: [Dropdown] Completed / Cancelled / Rescheduled
   - **Outcome**: [Radio] Successful / Needs Improvement / Lost Opportunity
   - **Prep Accuracy**: [1-5 stars] "How accurate was the research?"
   - **Most Useful Section**: [Dropdown] Company Overview / Decision Makers / Pain Points / Talking Points / Questions
   - **What Was Missing**: [Textarea, optional, 200 chars]
   - **General Notes**: [Textarea, optional, 500 chars]

**Data Usage**:
- Calculate success rate for dashboard
- Track section usefulness for future improvements
- Identify patterns (e.g., certain industries = lower accuracy)
- V2: Use feedback to fine-tune prompts

**Acceptance Criteria**:
- Feedback can be edited after submission
- Only "Completed" meetings count toward success rate
- Feedback submission updates dashboard stats immediately
- Low accuracy ratings trigger alert for manual review

---

## 3. Technical Architecture

### 3.1 Tech Stack
- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + Python 3.11+
- **AI Framework**: Pydantic AI
- **LLM**: Google Gemini 2.5 Pro (primary) / Google Gemini 2.5 Flash (fallback)
- **Web Search**: SerpAPI or Brave Search API
- **Web Scraping**: Firecrawl API (for deep company page analysis)
- **Database**: Supabase (Postgres)
- **Auth**: Supabase Auth
- **Observability**: Pydantic Logfire
- **File Storage**: Supabase Storage (for PDFs)
- **PDF Generation**: ReportLab (Python, simple programmatic generation)
- **Deployment**:
  - Backend: Railway or Render
  - Frontend: Vercel

### 3.2 Database Schema Design

**Design Principles**:
- Normalize critical entities (users, preps, outcomes) for data integrity
- Use JSONB for flexible AI output storage (schemas evolve frequently)
- Implement Row-Level Security (RLS) on all tables
- Index foreign keys and frequently queried columns
- Separate hot data (preps, profiles) from cold data (cache, usage logs)

**Required Tables**:

#### **user_profiles**
Extends Supabase auth.users with business context needed for AI generation.

**Must Have**:
- Primary key references auth.users(id) - one profile per authenticated user
- company_name (text, required) - user's company name
- company_description (text, required, max 500 chars) - value proposition context
- industries_served (text array, required) - for industry-specific insights
- portfolio (JSONB array, required) - structured list of past projects
  - Each project: {name, client_industry, description, outcomes}
  - Max 5 projects
- Timestamps: created_at, updated_at

**Security**:
- RLS: Users can only read/write their own profile
- Policy: `auth.uid() = id`

**Indexes**:
- Primary key on id (automatic)

---

#### **meeting_preps**
Stores generated sales prep reports with metadata for filtering/analytics.

**Must Have**:
- id (UUID primary key) - unique prep identifier
- user_id (UUID foreign key → auth.users) - ownership
- company_name (text, required) - prospect company
- company_name_normalized (text) - lowercase, stripped for cache lookups
- meeting_objective (text, required) - user's stated goal
- meeting_date (date, nullable) - for upcoming meeting tracking
- prep_data (JSONB, required) - full structured output matching UI format
  - Must contain: executive_summary, strategic_narrative, talking_points, questions, decision_makers, company_intelligence
  - Each section includes confidence score
- overall_confidence (float, required, 0.0-1.0) - aggregate confidence
- cache_hit (boolean) - whether company data came from cache
- pdf_url (text, nullable) - link to generated PDF in Supabase Storage
- created_at (timestamp) - sort by recency

**Security**:
- RLS: Users can only access their own preps
- Policy: `auth.uid() = user_id`

**Indexes**:
- user_id + created_at DESC (for dashboard queries)
- meeting_date (for upcoming meetings view)
- company_name_normalized (for duplicate detection)

**Constraints**:
- overall_confidence CHECK (overall_confidence >= 0 AND overall_confidence <= 1)

---

#### **meeting_outcomes**
Captures user feedback on meeting results for analytics and learning.

**Must Have**:
- id (UUID primary key)
- prep_id (UUID foreign key → meeting_preps, UNIQUE) - one outcome per prep
- meeting_status (enum: completed, cancelled, rescheduled)
- outcome (enum: successful, needs_improvement, lost_opportunity) - only if completed
- prep_accuracy (integer 1-5) - star rating of research quality
- most_useful_section (enum: executive_summary, talking_points, questions, decision_makers, company_intelligence)
- what_was_missing (text, max 500 chars, nullable)
- general_notes (text, max 1000 chars, nullable)
- created_at, updated_at

**Security**:
- RLS: Users can only access outcomes for their own preps
- Policy: `auth.uid() = (SELECT user_id FROM meeting_preps WHERE id = prep_id)`

**Indexes**:
- prep_id (unique, automatic foreign key index)

**Constraints**:
- prep_accuracy CHECK (prep_accuracy BETWEEN 1 AND 5)
- outcome required if meeting_status = 'completed'

---

#### **company_cache**
Stores reusable company research to reduce API costs and latency.

**Must Have**:
- company_name_normalized (text primary key) - unique cache key
- company_data (JSONB, required) - raw research data
  - Must contain: industry, size, recent_news, decision_makers, scraped_urls
- confidence_score (float, required, 0.0-1.0) - data quality indicator
- last_updated (timestamp, required) - for TTL checks (7 days)
- source_urls (text array) - audit trail for research

**Security**:
- RLS: All authenticated users can read (shared cache)
- RLS: Only system/admin can write (insert via backend API only)
- Policy Read: `auth.role() = 'authenticated'`
- Policy Write: `auth.role() = 'service_role'`

**Indexes**:
- last_updated DESC (for cache invalidation queries)

**Constraints**:
- confidence_score CHECK (confidence_score >= 0 AND confidence_score <= 1)

**TTL Logic** (implemented in application):
- Cache entry is stale if `NOW() - last_updated > INTERVAL '7 days'`
- Backend checks staleness before using cache

---

#### **api_usage_logs**
Tracks AI API consumption for cost monitoring and optimization.

**Must Have**:
- id (UUID primary key)
- user_id (UUID foreign key → auth.users, nullable) - null for system operations
- prep_id (UUID foreign key → meeting_preps, nullable) - link to specific prep
- operation (enum: company_research, prep_generation, cache_hit, pdf_export)
- provider (enum: gemini, claude, firecrawl, serpapi) - which API called
- tokens_used (integer, nullable) - for LLM calls
- cost_usd (decimal, nullable) - calculated cost
- duration_ms (integer) - operation latency
- success (boolean) - for error rate tracking
- error_message (text, nullable) - if failed
- created_at (timestamp)

**Security**:
- RLS: Users can only view their own usage
- Policy: `auth.uid() = user_id OR auth.role() = 'service_role'`

**Indexes**:
- user_id + created_at DESC (for user cost dashboards)
- created_at DESC (for admin monitoring)
- operation (for aggregate queries)

**Analytics Queries**:
```sql
-- Daily cost by provider
SELECT DATE(created_at), provider, SUM(cost_usd)
FROM api_usage_logs
WHERE success = true
GROUP BY DATE(created_at), provider;

-- Cache hit rate
SELECT
  COUNT(CASE WHEN operation = 'cache_hit' THEN 1 END)::float / COUNT(*) AS cache_rate
FROM api_usage_logs
WHERE operation IN ('cache_hit', 'company_research');
```

---

### **Row-Level Security (RLS) Summary**

**Critical Requirements**:
1. **Enable RLS on all tables** - `ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;`
2. **Users own their data** - user_profiles, meeting_preps, meeting_outcomes scoped to auth.uid()
3. **Shared cache** - company_cache readable by all, writable by service role only
4. **Usage logs** - users see own data, admins see all
5. **No default policies** - explicit allow-list approach (more secure than deny-list)

**Service Role vs User Role**:
- **User role** (auth.uid()): CRUD on own preps/profiles/outcomes
- **Service role** (backend API): Can write to cache, read all data for admin features

**Testing RLS**:
```sql
-- Test as user (should only see own data)
SET LOCAL ROLE authenticated;
SET LOCAL request.jwt.claim.sub = 'user-uuid-here';
SELECT * FROM meeting_preps; -- Should only return user's preps
```

---

### **Migration Strategy**

**Order of Table Creation**:
1. user_profiles (extends auth)
2. meeting_preps (references users)
3. meeting_outcomes (references preps)
4. company_cache (independent)
5. api_usage_logs (references users + preps)

**Initial Data**:
- No seed data needed (user-generated content)
- Consider adding sample industries list for dropdown

**Backup Strategy**:
- Supabase handles automated backups
- Implement weekly manual exports of preps (user data preservation)

### 3.3 API Endpoints

```
POST   /api/auth/profile          # Create/update user profile
GET    /api/auth/profile          # Get current user profile

POST   /api/preps                 # Create new prep
GET    /api/preps                 # List user's preps (paginated)
GET    /api/preps/{id}            # Get specific prep
DELETE /api/preps/{id}            # Delete prep

POST   /api/preps/{id}/export/pdf    # Generate PDF
POST   /api/preps/{id}/export/notion # Export to Notion

POST   /api/preps/{id}/outcome    # Record meeting outcome
PUT    /api/preps/{id}/outcome    # Update outcome

GET    /api/dashboard/stats       # Get dashboard metrics

POST   /api/cache/refresh/{company} # Force cache refresh
```

### 3.4 Data Models & Schema Design

Instead of rigid Pydantic classes, we define **flexible data schemas** that balance structure with adaptability as the AI output evolves.

---

#### **Why JSONB Storage for AI Outputs?**

**Advantages**:
- AI outputs change frequently during development (new sections, renamed fields)
- Avoids database migrations every time we improve prompts
- Queryable with Postgres JSONB operators (`->`, `->>`, `@>`)
- Can validate shape in application layer, not database layer

**Trade-offs**:
- Less type safety at DB level (compensated by Pydantic validation before save)
- Requires clear documentation of expected schema

---

#### **Core Data Schemas to Define**

These are **logical schemas** validated in the application, stored as JSONB in database.

---

##### **1. UserProfile Schema**
**Purpose**: Provide AI agents with user context to personalize outputs.

```python
{
  "company_name": str,           # Required: "Acme Consulting"
  "company_description": str,    # Required: Max 500 chars
  "industries_served": [str],    # Required: ["SaaS", "E-commerce"]
  "portfolio": [
    {
      "name": str,               # "AI Route Optimizer"
      "client_industry": str,    # "Logistics"
      "description": str,        # Max 200 chars
      "key_outcomes": str        # "Improved delivery time by 15%"
    }
  ]  # Max 5 projects
}
```

**Validation Rules**:
- At least 1 industry selected
- At least 1 portfolio project (minimum viable context)
- Description fields sanitized (no HTML/scripts)

**Used By**:
- AI prompt construction (system context)
- Dashboard personalization (show user's specialties)

---

##### **2. PrepData Schema** (The Main AI Output)
**Purpose**: Structured sales brief matching the UI sections.

```python
{
  "executive_summary": {
    "the_client": str,           # 1-2 sentences about prospect
    "our_angle": str,            # How user's portfolio matches their needs
    "call_goal": str,            # Clear objective for this meeting
    "confidence": float          # 0.0-1.0
  },

  "strategic_narrative": {
    "dream_outcome": str,        # Prospect's north star goal
    "proof_of_achievement": [
      {
        "project_name": str,     # From user's portfolio
        "relevance": str,        # Why it matters + metric
      }
    ],  # 2-3 projects
    "pain_points": [str],        # 3-5 specific pains with business impact
    "confidence": float
  },

  "talking_points": {
    "opening_hook": str,         # Conversation starter
    "key_points": [str],         # 4-6 talking points
    "competitive_context": str,  # How to position vs competitors
    "confidence": float
  },

  "questions_to_ask": {
    "strategic": [str],          # About goals, timeline
    "technical": [str],          # About systems, data
    "business_impact": [str],    # About cost of inaction
    "qualification": [str],      # About budget, decision process
    "confidence": float
  },  # Total 8-12 questions

  "decision_makers": {
    "profiles": [
      {
        "name": str,
        "title": str,
        "linkedin_url": str | null,
        "background_points": [str]  # 2-3 points
      }
    ],  # Max 3 people
    "confidence": float
  },

  "company_intelligence": {
    "industry": str,
    "company_size": str,         # e.g., "500-1000 employees"
    "recent_news": [
      {
        "headline": str,
        "date": str,             # ISO format
        "significance": str      # Why it matters
      }
    ],  # 3-5 items
    "strategic_initiatives": [str],  # Current priorities
    "confidence": float
  },

  "research_limitations": [str],  # Only if confidence < 0.7 anywhere
  "overall_confidence": float,    # Weighted average
  "sources": [str]                # URLs used for research
}
```

**Validation Strategy**:
1. **Application-level Pydantic models** validate before DB insert
2. If validation fails → log error to Logfire + show user-friendly message
3. Store validated JSONB in `meeting_preps.prep_data`

**Why This Structure**:
- Matches example output from Relevance AI prototype
- Each section has independent confidence score (granular trust signals)
- Questions categorized by type (helps user prepare strategically)
- Sources tracked for transparency/debugging

---

##### **3. CompanyCache Schema**
**Purpose**: Store reusable research data to avoid redundant API calls.

```python
{
  "industry": str,
  "company_size": str,
  "founded_year": int | null,
  "website": str,
  "description": str,           # Scraped from about page
  "recent_news": [
    {
      "headline": str,
      "url": str,
      "date": str,
      "source": str
    }
  ],
  "decision_makers": [
    {
      "name": str,
      "title": str,
      "linkedin_url": str | null,
      "recent_activity": str     # e.g., "Posted about AI adoption"
    }
  ],
  "strategic_signals": [str],    # Job postings, product launches
  "scraped_urls": [str],         # Audit trail
  "scrape_timestamp": str        # ISO format
}
```

**Cache Invalidation**:
- TTL: 7 days from `last_updated`
- User can force refresh with "Update Research" button
- Stale cache used as fallback if API fails

---

##### **4. MeetingOutcome Schema**
**Purpose**: Capture structured feedback for analytics.

```python
{
  "meeting_status": "completed" | "cancelled" | "rescheduled",
  "outcome": "successful" | "needs_improvement" | "lost_opportunity" | null,
  "prep_accuracy": 1 | 2 | 3 | 4 | 5,
  "most_useful_section": str,    # Enum from prep sections
  "what_was_missing": str | null,
  "general_notes": str | null,
  "submitted_at": str            # ISO timestamp
}
```

**Analytics Queries Enabled**:
- Success rate by industry
- Most useful sections (prioritize in future versions)
- Common gaps in research (improve prompts)

---

#### **Schema Evolution Strategy**

**Version 1 (MVP)**: Current schema as defined above

**Future Additions** (stored as new keys in JSONB, backward compatible):
- `prep_data.competitive_analysis` (detailed competitor comparison)
- `prep_data.risk_factors` (red flags about the deal)
- `company_cache.financial_data` (revenue, funding rounds)

**Migration Path**:
- No database migrations needed
- Application code checks for key existence: `data.get("new_field", default_value)`
- Logfire tracks which prep versions are in use

---

#### **Confidence Score Calculation**

**Formula** (weighted average):
```
overall_confidence = (
  executive_summary.confidence * 0.15 +
  strategic_narrative.confidence * 0.25 +
  talking_points.confidence * 0.20 +
  questions.confidence * 0.10 +
  decision_makers.confidence * 0.15 +
  company_intelligence.confidence * 0.15
)
```

**Per-Section Confidence Logic**:
- **Company Intelligence**: Based on data freshness (news < 30 days = higher), number of sources
- **Decision Makers**: Based on LinkedIn profile completeness, recency of activity
- **Strategic Narrative**: Based on portfolio project relevance score (semantic similarity)
- **Talking Points**: Based on pain point → portfolio match quality
- **Questions**: Always high (generated from frameworks, not data-dependent)

---

#### **Why Not Strict Pydantic Models in Database?**

**Considered Approach**: Store structured columns (e.g., `executive_summary_text`, `confidence_score`)

**Why JSONB is Better for This Use Case**:
1. **Rapid Iteration**: Change prompt → change output schema in hours, not days
2. **Complex Nested Data**: Questions have 4 subcategories, hard to normalize
3. **Schema Versioning**: Can store `schema_version` key, query old/new formats
4. **Postgres JSONB Performance**: Indexed JSONB queries are fast enough (<100ms)

**Safety Net**: Pydantic validation happens in FastAPI before database insert, so we get type safety where it matters (API boundary), not in storage layer.

---

## 4. MVP Development Phases

### Phase 1: Foundation (Week 1)
- [ ] Supabase project setup + schema
- [ ] FastAPI boilerplate + Supabase integration
- [ ] Next.js project + Supabase Auth
- [ ] User profile CRUD (backend + frontend)
- [ ] Basic dashboard UI (no data yet)

### Phase 2: Core AI Pipeline (Week 2)
- [ ] Pydantic AI agent setup + Logfire integration
- [ ] Company research function (web search integration)
- [ ] Decision maker search function
- [ ] Output generation with confidence scoring
- [ ] Cache system implementation
- [ ] API endpoint: POST /api/preps

### Phase 3: Frontend Features (Week 3)
- [ ] Create prep form + flow
- [ ] Prep detail view with structured output
- [ ] Confidence score UI components
- [ ] Dashboard stats implementation
- [ ] Prep list with filters/search

### Phase 4: Export & Feedback (Week 4)
- [ ] PDF generation (ReportLab)
- [ ] Notion OAuth + export logic
- [ ] Meeting outcome modal + API
- [ ] Dashboard stats recalculation
- [ ] Mobile responsiveness

### Phase 5: Polish & Deploy (Week 5)
- [ ] Error handling + loading states
- [ ] Logfire dashboard setup
- [ ] Cost monitoring queries
- [ ] User testing + bug fixes
- [ ] Deployment (Railway + Vercel)
- [ ] Basic landing page

---

## 5. Non-Functional Requirements

### 5.1 Performance
- Prep generation (cache miss): < 2 minutes
- Prep generation (cache hit): < 30 seconds
- Dashboard load: < 1 second
- PDF export: < 5 seconds

### 5.2 Reliability
- 99% uptime target
- Graceful API failure handling (retry with exponential backoff)
- Rate limiting to prevent abuse
- All user inputs validated
- Error messages are actionable

### 5.3 Security
- All API routes require authentication
- Row-level security on Supabase tables
- API keys stored in environment variables
- HTTPS only in production

### 5.4 Cost Management
- Cache hit rate > 40% (reduces API costs)
- Track token usage per user
- Alert if daily API costs > $10

---

## 6. Out of Scope (V2 Features)

- ❌ Multi-user teams / sharing preps
- ❌ Calendar integration (auto-create preps from meetings)
- ❌ Real-time news alerts for upcoming meetings
- ❌ Mobile app
- ❌ CRM integrations (Salesforce, HubSpot)
- ❌ Voice notes / call recording analysis
- ❌ AI chat interface for follow-up questions
- ❌ Custom prompt templates
- ❌ Fine-tuning based on feedback data

---

## 7. Success Criteria for Portfolio

**What impresses potential clients**:
1. ✅ **Production quality**: Clean UI, error handling, loading states
2. ✅ **Smart engineering**: Caching strategy shows cost awareness
3. ✅ **Observability**: Logfire dashboard demonstrates monitoring skills
4. ✅ **Real AI value**: Not just a ChatGPT wrapper—structured output, confidence scores
5. ✅ **Feedback loop**: Shows understanding of continuous improvement
6. ✅ **Complete docs**: README with architecture diagram, setup instructions
---

**Document Version**: 1.0
**Last Updated**: October 28, 2025
**Owner**: Lessan
**Status**: Ready for Development
