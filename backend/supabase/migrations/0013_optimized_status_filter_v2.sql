-- Migration: Add array-based status filter functions (v2)
-- This migration replaces the scalar-based functions with array-based ones
-- to handle mixed status filters (including 'pending') in a single SQL query.
-- Performance improvement: eliminates 3-4 client-side queries → 1 SQL query
-- Security: Adds authorization check to prevent privilege escalation

-- Drop existing functions if they exist (both old scalar and new array signatures)
DROP FUNCTION IF EXISTS get_preps_by_status(uuid, varchar, int, int, varchar);
DROP FUNCTION IF EXISTS get_preps_count_by_status(uuid, varchar, varchar);
DROP FUNCTION IF EXISTS get_preps_by_status(uuid, varchar[], int, int, varchar);
DROP FUNCTION IF EXISTS get_preps_count_by_status(uuid, varchar[], varchar);

CREATE OR REPLACE FUNCTION get_preps_by_status(
    p_user_id uuid,
    p_statuses VARCHAR(20)[],
    p_limit INT DEFAULT 10,
    p_offset INT DEFAULT 0,
    p_search VARCHAR DEFAULT NULL
)
RETURNS TABLE(
    id UUID,
    company_name VARCHAR,
    meeting_objective TEXT,
    meeting_date DATE,
    created_at TIMESTAMPTZ,
    overall_confidence FLOAT,
    meeting_status VARCHAR(20),
    outcome VARCHAR(20)
)
LANGUAGE sql
STABLE
SECURITY INVOKER
AS $$
    -- Authorization check: if called by an authenticated user, verify they own the data
    -- (auth.uid() IS NULL means service role or anonymous, which proceeds normally)
    SELECT
        mp.id,
        mp.company_name,
        mp.meeting_objective,
        mp.meeting_date,
        mp.created_at,
        mp.overall_confidence,
        mo.meeting_status::VARCHAR AS meeting_status,
        mo.outcome::VARCHAR AS outcome
    FROM meeting_preps mp
    LEFT JOIN meeting_outcomes mo ON mp.id = mo.prep_id
    WHERE (auth.uid() IS NULL OR auth.uid() = p_user_id)
    AND mp.user_id = p_user_id
    AND (
        CASE
            WHEN 'pending' = ANY(p_statuses) AND mo.prep_id IS NULL THEN TRUE
            WHEN mo.prep_id IS NOT NULL AND mo.meeting_status::VARCHAR = ANY(p_statuses) THEN TRUE
            ELSE FALSE
        END
    )
    AND (p_search IS NULL OR mp.company_name ILIKE '%' || p_search || '%')
    ORDER BY mp.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
$$;

GRANT EXECUTE ON FUNCTION get_preps_by_status(uuid, varchar[], int, int, varchar) TO authenticated;

CREATE OR REPLACE FUNCTION get_preps_count_by_status(
    p_user_id uuid,
    p_statuses VARCHAR(20)[],
    p_search VARCHAR DEFAULT NULL
)
RETURNS INT
LANGUAGE sql
STABLE
SECURITY INVOKER
AS $$
    -- Authorization check: if called by an authenticated user, verify they own the data
    SELECT COUNT(*)
    FROM meeting_preps mp
    LEFT JOIN meeting_outcomes mo ON mp.id = mo.prep_id
    WHERE (auth.uid() IS NULL OR auth.uid() = p_user_id)
    AND mp.user_id = p_user_id
    AND (
        CASE
            WHEN 'pending' = ANY(p_statuses) AND mo.prep_id IS NULL THEN TRUE
            WHEN 'pending' = ANY(p_statuses) AND mo.prep_id IS NOT NULL AND mo.meeting_status::VARCHAR = ANY(p_statuses) THEN TRUE
            WHEN 'pending' != ANY(p_statuses) AND mo.meeting_status::VARCHAR = ANY(p_statuses) THEN TRUE
            ELSE FALSE
        END
    )
    AND (p_search IS NULL OR mp.company_name ILIKE '%' || p_search || '%');
$$;

GRANT EXECUTE ON FUNCTION get_preps_count_by_status(uuid, varchar[], varchar) TO authenticated;

COMMENT ON FUNCTION get_preps_by_status IS
'Get preps with array of statuses. Handles pending via LEFT JOIN IS NULL pattern.
 Includes authorization check to prevent unauthorized access to other users data.';

COMMENT ON FUNCTION get_preps_count_by_status IS
'Count preps with same LEFT JOIN array pattern. Includes authorization check.';
