# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Sales-call-prep-assistant** is an AI-powered tool that helps sales professionals (freelancers, consultants, and SDRs) prepare for sales calls in minutes instead of hours. It automatically researches prospects and generates personalized talking points using a two-agent system with tool-calling architecture.

### Key Capabilities
- Automatically researches prospect companies and decision makers
- Generates comprehensive 6-section sales prep reports with confidence scoring
- Smart caching system (7-day TTL) to reduce API costs and improve performance
- Export to PDF and Markdown formats
- Dashboard with meeting history and outcome tracking

## Architecture

### Tech Stack
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI (Python 3.11+), Pydantic AI agents, Google Gemini
- **Database**: Supabase (Postgres + Auth + Storage + RLS)
- **External APIs**: SerpAPI (web search), Firecrawl (web scraping), Google Gemini (LLM)

### Two-Agent System

**Agent A - Research Orchestrator** (`backend/src/agents/research_orchestrator/agent.py`)
- Uses Pydantic AI with Gemini model and tool-calling
- 5 available tools:
  - `web_search` - SerpAPI for web search
  - `scrape_website` - Firecrawl for deep website scraping
  - `get_company_linkedin` - Apify for company LinkedIn data
  - `search_linkedin_profile` - Apify for decision maker profiles
  - `scrape_linkedin_posts` - Apify for recent company posts
- Makes iterative tool calls based on what it learns
- Returns structured research data with confidence scores
- Implements 7-day caching system

**Agent B - Sales Brief Synthesizer** (`backend/src/agents/sales_synthesizer/agent.py`)
- Uses Pydantic AI with Gemini model
- Has 1 tool: `search_portfolio` - searches user's portfolio for relevant projects
- Receives research data + user profile + meeting objective
- Generates structured 6-section prep reports with confidence scoring
- References specific portfolio projects throughout the brief

### Data Flow
1. User submits company name + meeting objective
2. Backend checks `company_cache` table (7-day TTL)
3. Cache miss → Agent A researches (web search → scrape → LinkedIn)
4. Cache hit → Load cached data
5. Agent B synthesizes: research + user portfolio → structured prep
6. Save to `meeting_preps` table with confidence scores
7. Frontend renders 6-section report with confidence indicators

## Common Development Commands

### Frontend (Next.js)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
pnpm install

# Run development server
pnpm dev
# Opens http://localhost:3000

# Build for production
pnpm build

# Start production server
pnpm start

# Run linting
pnpm lint

# Run tests
pnpm test
```

### Backend (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Install dependencies (uses uv)
uv sync

# Install dev dependencies
uv sync --group dev

# Run development server (auto-reload)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
# Opens http://localhost:8000

# View API docs (automatic with FastAPI)
# http://localhost:8000/docs

# Run tests
pytest

# Type checking (if using pyright)
pyright src/
```

### Database (Supabase)

```bash
# Start local Supabase (if configured)
supabase start

# Apply migrations
supabase db push

# View logs
supabase logs
```

## Project Structure

### Backend (`backend/src/`)

```
src/
├── main.py                    # FastAPI app entry point, includes routers
├── config.py                  # Environment variables via pydantic-settings
├── dependencies.py            # Auth & Supabase client dependencies
├── routers/
│   ├── prep.py               # Main prep creation/retrieval routes
│   └── profile.py            # User profile CRUD operations
├── agents/                    # Two-agent system
│   ├── research_orchestrator/
│   │   ├── agent.py          # Agent A - Research Orchestrator
│   │   └── tools/            # 5 tools for Agent A
│   │       ├── web_search.py
│   │       ├── scrape_website.py
│   │       ├── get_company_linkedin.py
│   │       ├── search_linkedin_profile.py
│   │       └── scrape_linkedin_posts.py
│   └── sales_synthesizer/
│       ├── agent.py          # Agent B - Sales Brief Synthesizer
│       └── tools/
│           └── search_portfolio.py
├── services/                  # External API wrappers
│   ├── apify_service.py      # Apify client wrapper
│   ├── firecrawl_service.py  # Firecrawl client wrapper
│   ├── search_service.py     # SerpAPI wrapper
│   ├── cache_service.py      # Cache management (7-day TTL)
│   └── supabase_service.py   # Database operations
├── schemas/
│   ├── prep_report.py        # PrepRequest & PrepReport schemas
│   └── user_profile.py       # User profile schemas
├── supabase_client.py        # Supabase client initialization
└── utils/
    └── logger.py             # Structured logging utility
```

### Frontend (`frontend/src/`)

```
src/
├── app/                      # Next.js App Router
│   ├── page.tsx             # Landing page
│   ├── login/               # Authentication pages
│   ├── signup/
│   ├── profile/             # User profile management
│   ├── new-prep/            # Create new sales prep form
│   └── prep/[id]/           # View specific prep report
├── components/
│   ├── ui/                  # shadcn/ui components
│   └── providers/           # Context providers (auth)
├── lib/
│   ├── supabase/            # Supabase client & auth
│   ├── utils.ts             # Utility functions
│   └── logger.ts            # Logging
└── types/                   # TypeScript type definitions
```

### Database Schema

Key tables (see `backend/supabase/migrations/0001_tables.sql:11-84`):

- **user_profiles**: User business context (company, portfolio)
- **meeting_preps**: Generated prep reports with confidence scores
- **meeting_outcomes**: User feedback on meeting results
- **company_cache**: 7-day cached company research data
- **api_usage_logs**: API cost & performance monitoring

## Development Environment Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- pnpm
- uv (Python package manager)
- Supabase account

### Environment Variables

Create `backend/.env` (see `.env.example`):

```bash
SUPABASE_URL=your-supabase-project-url
PUSHABLE_KEY=your-supabase-pushable-key  # anon key
SECRET_KEY=your-supabase-secret-key      # service role key
GOOGLE_API_KEY=your-google-api-key
SERP_API_KEY=your-serpapi-key
FIRECRAWL_API_KEY=your-firecrawl-key
APIFY_API_KEY=your-apify-key
GEMINI_MODEL=gemini-2.0-flash-exp
```

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=your-supabase-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-pushable-key
```

### Database Setup

1. Create Supabase project
2. Run migrations:
```bash
supabase db push
```

3. Configure RLS policies (see `backend/supabase/migrations/0002_rls.sql`)

## Key Implementation Details

### API Endpoints

- `POST /api/preps` - Create new prep report (uses two-agent system)
  - Body: PrepRequest with fields:
    - `company_name` (required)
    - `meeting_objective` (required)
    - `contact_person_name` (optional)
    - `contact_linkedin_url` (optional)
    - `meeting_date` (optional)
- `GET /api/preps/{id}` - Retrieve prep report
- `GET /api/auth/profile` - Get user profile
- `POST /api/auth/profile` - Upsert user profile
- `GET /health` - Health check with Supabase connectivity

See `backend/src/routers/prep.py` for implementation.

### Caching Strategy

Cache key: `company_name_normalized` (lowercase, alphanumeric only)
TTL: 7 days
Table: `company_cache`
Location: `backend/src/routers/prep.py:49-72`

### Confidence Scoring

Each section of the prep report has a 0.0-1.0 confidence score based on:
- Data completeness
- Source quality (LinkedIn profile vs. web search)
- Portfolio relevance
- Recent data (news < 30 days)

Overall score is weighted average:
- Executive Summary: 15%
- Strategic Narrative: 25%
- Talking Points: 20%
- Questions: 10%
- Decision Makers: 15%
- Company Intelligence: 15%

### Authentication Flow

Supabase Auth with:
- JWT tokens
- Row-Level Security (RLS) on all tables
- User ID linked to `auth.users.id`
- Profile creation required before first prep

## Important Configuration

### Backend Settings (`backend/src/config.py:5-17`)

- Uses pydantic-settings for environment variable management
- Required variables defined with Field() and aliases
- Supports .env file loading

### Supabase Client (`backend/src/supabase_client.py`)

- Async client for FastAPI
- Attached to app state for lifecycle management
- Health check endpoint validates connectivity (`backend/src/main.py:56`)

### Logging (`backend/src/utils/logger.py`)

- Structured logging with contextual info
- Used throughout routers and agents
- Frontend has similar logger (`frontend/src/lib/logger.ts`)

## Development Practices

### Code Style

- **Python**: Google Python Style Guide (see `GEMINI.md:41`)
- **TypeScript**: Google TypeScript Style Guide (see `GEMINI.md:42`)
- **Formatting**: Formatters should be configured per project standards
- **Type Safety**: Extensive use of Pydantic models for validation

### Automated Code Reviews with CodeRabbit

This project uses [CodeRabbit](https://coderabbit.ai/) for automated AI-powered code reviews on all pull requests to the main branch.

#### Setup

1. Install CodeRabbit GitHub App on your repository:
   - Visit [https://coderabbit.ai/](https://coderabbit.ai/)
   - Click "Get Started" or "Install App"
   - Select your repository
   - Grant necessary permissions

2. Configuration is already set up in `.coderabbit.yaml`:
   - Optimized for Python/FastAPI backend
   - Optimized for TypeScript/Next.js frontend
   - Includes security scanning (gitleaks, semgrep, osv-scanner)
   - Enforces code style (ruff, flake8, pylint, eslint)
   - Custom checks for environment variables and security
   - Docstring and test generation enabled

#### Features

- **Auto Review**: Automatically reviews PRs when opened or updated
- **Security Scanning**: Detects secrets, vulnerabilities, and insecure patterns
- **Linting Integration**: Runs ruff, flake8, pylint for Python; eslint, biome for TypeScript
- **Custom Checks**:
  - Environment variables validation
  - Security vulnerability scanning
  - Database migration verification
- **Smart Insights**: Provides high-level summaries, sequence diagrams, and effort estimates
- **Knowledge Base**: Learns from your coding standards (CLAUDE.md, GEMINI.md)

#### CodeRabbit Commands

Use these commands in PR comments:

- `@coderabbitai summary` - Generate a high-level summary of changes
- `@coderabbitai outline` - Create an outline of the changes
- `@coderabbitai sequence-diagrams` - Generate sequence diagrams
- `@coderabbitai review` - Request a fresh review
- `@coderabbitai faq` - Answer questions about the changes
- `@coderabbitai configuration` - Get current configuration as YAML

#### Review Workflow

1. Create a pull request to `main` branch
2. CodeRabbit automatically starts reviewing
3. Review summary and comments appear within minutes
4. Address comments and push fixes
5. CodeRabbit updates the review status
6. Merge when all checks pass

#### Custom Path Instructions

CodeRabbit applies specific guidelines based on file paths:

- **Python files** (`**/*.py`): Google Python Style, type hints, docstrings
- **FastAPI routers** (`backend/src/routers/*.py`): API best practices, proper status codes
- **Agent code** (`backend/src/agents/**/*.py`): Tool usage, error handling, caching
- **TypeScript files** (`**/*.ts`): Google TypeScript Style, types, performance
- **React components** (`**/*.tsx`): Hooks usage, a11y, Tailwind best practices

See `.coderabbit.yaml` for complete configuration.

### Testing

- **Frontend**: Jest + Testing Library (`frontend/package.json:28-38`)
- **Backend**: pytest in dev dependencies (`backend/pyproject.toml:24`)

### Prompt Engineering

- Prompts stored in `backend/src/prompts/` as markdown templates
- Dynamic values injected via `format()` method
- Location: `backend/src/tools/gemini_agent.py:27-39`

### Error Handling

- Agents implement graceful degradation (try alternatives if tool fails)
- All API calls wrapped in try-except with HTTPException
- Cache failures don't block prep generation
- API usage logged for monitoring

## External API Dependencies

1. **Google Gemini** - LLM for agent reasoning and report generation
2. **SerpAPI** - Web search for company discovery
3. **Firecrawl** - Deep website scraping for detailed company data
4. **Supabase** - Database, auth, storage, and row-level security

## Performance Considerations

- **Caching**: 7-day cache reduces API costs by 40%+ (target)
- **Cache hit time**: ~30 seconds (vs. 2+ minutes cache miss)
- **Database indexes**: Optimized for dashboard queries and cache lookups
- **Frontend**: Next.js App Router for optimized loading

## Future Enhancements (Not Yet Implemented)

According to the PRD (`docs/PRD.md`):

- LinkedIn scraping via Apify actors
- Portfolio vector embeddings for similarity search
- PDF export generation with ReportLab
- Dashboard with stats and meeting history
- Meeting feedback and outcome recording
- Advanced confidence scoring algorithms

## Troubleshooting

### Backend won't start
- Verify all environment variables are set
- Check Supabase credentials are valid
- Ensure port 8000 is available

### Frontend build fails
- Clear `.next` cache: `rm -rf .next`
- Reinstall dependencies: `pnpm install`
- Check Node.js version (requires 18+)

### Database connection issues
- Verify Supabase URL and keys in .env
- Check RLS policies are applied
- Ensure migrations ran successfully

### API rate limits
- SerpAPI and Firecrawl have rate limits
- Cache hits reduce API calls significantly
- Monitor usage in `api_usage_logs` table
- stop putting your name in the commit messages
