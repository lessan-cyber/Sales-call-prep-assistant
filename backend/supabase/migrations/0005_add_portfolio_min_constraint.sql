-- Migration: Add database-level constraint for minimum portfolio items

-- Add check constraint to enforce minimum 5 portfolio items at database level
ALTER TABLE user_profiles
ADD CONSTRAINT portfolio_min_items
CHECK (
    jsonb_array_length(COALESCE(portfolio, '[]'::jsonb)) >= 5
    OR portfolio IS NULL  -- Allow NULL during initial profile creation
);

-- Create index to help with constraint validation performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_portfolio_length
ON user_profiles
USING btree (
    jsonb_array_length(COALESCE(portfolio, '[]'::jsonb))
);
