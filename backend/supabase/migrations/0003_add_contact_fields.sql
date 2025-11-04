-- Migration: Add contact fields to meeting_preps table
-- Required by PRD2 for Agent A to search decision makers

ALTER TABLE meeting_preps
ADD COLUMN contact_person_name TEXT,
ADD COLUMN contact_linkedin_url TEXT;

-- Create indexes for the new fields
CREATE INDEX ON meeting_preps (contact_person_name);
