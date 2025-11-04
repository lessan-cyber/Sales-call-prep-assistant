-- backend/supabase/migrations/0001_tables.sql

-- Enum Types
CREATE TYPE meeting_status AS ENUM ('completed', 'cancelled', 'rescheduled');
CREATE TYPE meeting_outcome_value AS ENUM ('successful', 'needs_improvement', 'lost_opportunity');
CREATE TYPE prep_section AS ENUM ('executive_summary', 'talking_points', 'questions', 'decision_makers', 'company_intelligence');
CREATE TYPE api_operation AS ENUM ('company_research', 'prep_generation', 'cache_hit', 'pdf_export');
CREATE TYPE api_provider AS ENUM ('gemini', 'claude', 'firecrawl', 'serpapi');

-- user_profiles table
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    company_name TEXT NOT NULL,
    company_description TEXT NOT NULL,
    industries_served TEXT[] NOT NULL,
    portfolio JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- meeting_preps table
CREATE TABLE meeting_preps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    company_name TEXT NOT NULL,
    company_name_normalized TEXT NOT NULL,
    meeting_objective TEXT NOT NULL,
    meeting_date DATE,
    prep_data JSONB NOT NULL,
    overall_confidence FLOAT NOT NULL CHECK (overall_confidence >= 0 AND overall_confidence <= 1),
    cache_hit BOOLEAN NOT NULL DEFAULT FALSE,
    pdf_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ON meeting_preps (user_id, created_at DESC);
CREATE INDEX ON meeting_preps (meeting_date);
CREATE INDEX ON meeting_preps (company_name_normalized);

-- meeting_outcomes table
CREATE TABLE meeting_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prep_id UUID NOT NULL UNIQUE REFERENCES meeting_preps(id) ON DELETE CASCADE,
    meeting_status meeting_status NOT NULL,
    outcome meeting_outcome_value,
    prep_accuracy INT CHECK (prep_accuracy >= 1 AND prep_accuracy <= 5),
    most_useful_section prep_section,
    what_was_missing TEXT,
    general_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ON meeting_outcomes (prep_id);

-- company_cache table
CREATE TABLE company_cache (
    company_name_normalized TEXT PRIMARY KEY,
    company_data JSONB NOT NULL,
    confidence_score FLOAT NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    last_updated TIMESTAMPTZ NOT NULL,
    source_urls TEXT[]
);

CREATE INDEX ON company_cache (last_updated DESC);

-- api_usage_logs table
CREATE TABLE api_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    prep_id UUID REFERENCES meeting_preps(id) ON DELETE SET NULL,
    operation api_operation NOT NULL,
    provider api_provider,
    tokens_used INT,
    cost_usd DECIMAL,
    duration_ms INT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ON api_usage_logs (user_id, created_at DESC);
CREATE INDEX ON api_usage_logs (created_at DESC);
CREATE INDEX ON api_usage_logs (operation);
