-- Migration: Add automatic updated_at trigger for all tables with updated_at column

-- Create a function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add trigger to user_profiles table
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add trigger to meeting_preps table
CREATE TRIGGER update_meeting_preps_updated_at
    BEFORE UPDATE ON meeting_preps
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add trigger to meeting_outcomes table
CREATE TRIGGER update_meeting_outcomes_updated_at
    BEFORE UPDATE ON meeting_outcomes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
