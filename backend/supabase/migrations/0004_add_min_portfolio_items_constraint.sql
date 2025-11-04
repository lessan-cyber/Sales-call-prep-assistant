-- Migration: Ensure all user profiles have at least 5 portfolio items

-- Create a function to populate portfolio with dummy items if less than 5
CREATE OR REPLACE FUNCTION ensure_min_portfolio_items()
RETURNS void AS $$
DECLARE
    profile_record RECORD;
    portfolio_count INT;
    dummy_items JSONB;
BEGIN
    -- Loop through all user profiles
    FOR profile_record IN
        SELECT id, portfolio FROM user_profiles
    LOOP
        -- Check if portfolio exists and count items
        IF profile_record.portfolio IS NOT NULL THEN
            SELECT jsonb_array_length(profile_record.portfolio) INTO portfolio_count;
        ELSE
            portfolio_count := 0;
        END IF;

        -- If less than 5 items, add dummy items
        IF portfolio_count < 5 THEN
            dummy_items := '[]'::jsonb;

            -- Add dummy portfolio items to meet the minimum
            FOR i IN (portfolio_count + 1) .. 5 LOOP
                dummy_items := dummy_items || jsonb_build_object(
                    'name', 'Sample Project ' || i,
                    'client_industry', 'Technology',
                    'description', 'A sample project description to meet the minimum portfolio requirement. Please update with your actual project details.',
                    'key_outcomes', 'Key outcomes and results from this project.'
                );
            END LOOP;

            -- Update the profile with dummy items
            UPDATE user_profiles
            SET
                portfolio = COALESCE(portfolio, '[]'::jsonb) || dummy_items,
                updated_at = NOW()
            WHERE id = profile_record.id;

            RAISE NOTICE 'Updated profile % with % dummy portfolio items', profile_record.id, (5 - portfolio_count);
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Execute the function
SELECT ensure_min_portfolio_items();

-- Drop the function as it's no longer needed
DROP FUNCTION ensure_min_portfolio_items();
