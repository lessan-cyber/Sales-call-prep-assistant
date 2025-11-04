-- backend/supabase/migrations/0002_rls.sql

-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_preps ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage_logs ENABLE ROW LEVEL SECURITY;

-- Policies for user_profiles
CREATE POLICY "Users can insert their own profile." ON user_profiles FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "Users can update their own profile." ON user_profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can view their own profile." ON user_profiles FOR SELECT USING (auth.uid() = id);

-- Policies for meeting_preps
CREATE POLICY "Users can create meeting preps." ON meeting_preps FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can view their own meeting preps." ON meeting_preps FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update their own meeting preps." ON meeting_preps FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own meeting preps." ON meeting_preps FOR DELETE USING (auth.uid() = user_id);

-- Policies for meeting_outcomes
CREATE POLICY "Users can create meeting outcomes for their preps." ON meeting_outcomes FOR INSERT WITH CHECK (auth.uid() = (SELECT user_id FROM meeting_preps WHERE id = prep_id));
CREATE POLICY "Users can view their own meeting outcomes." ON meeting_outcomes FOR SELECT USING (auth.uid() = (SELECT user_id FROM meeting_preps WHERE id = prep_id));
CREATE POLICY "Users can update their own meeting outcomes." ON meeting_outcomes FOR UPDATE USING (auth.uid() = (SELECT user_id FROM meeting_preps WHERE id = prep_id));
CREATE POLICY "Users can delete their own meeting outcomes." ON meeting_outcomes FOR DELETE USING (auth.uid() = (SELECT user_id FROM meeting_preps WHERE id = prep_id));

-- Policies for company_cache
CREATE POLICY "Authenticated users can read the company cache." ON company_cache FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Service role can write to the company cache." ON company_cache FOR ALL USING (auth.role() = 'service_role');

-- Policies for api_usage_logs
CREATE POLICY "Users can view their own usage logs." ON api_usage_logs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Service role can manage all usage logs." ON api_usage_logs FOR ALL USING (auth.role() = 'service_role');
