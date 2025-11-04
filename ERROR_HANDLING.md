# Error Handling & Edge Cases Implementation

## Overview
Added comprehensive error handling to the AI agent system to gracefully handle API quotas, rate limits, server overloads, and other edge cases.

## Changes Made

### 1. AI Agents (Research & Sales Synthesizer)

**Files Modified:**
- `backend/src/agents/research_orchestrator/agent.py`
- `backend/src/agents/sales_synthesizer/agent.py`

**Features Added:**
- **Exponential Backoff Retry Logic**: 3 retry attempts with 1s, 2s, 4s delays
- **Smart Error Classification**:
  - Rate Limits (429): Extended delay (up to 30s), automatic retry
  - Quota Exceeded: No retry, immediate failure with clear message
  - Server Errors (500-504): Retry with exponential backoff
  - Server Overload: Retry with extended delay
  - Invalid Arguments: No retry (user error)
- **Detailed Logging**: All retry attempts and failures are logged
- **Pydantic AI Version Compatibility**: Handles both `.data` and `.output` attributes

**Error Handling Flow:**
```
Request → Agent Run
         ↓
    Failure Detected?
         ↓
    Check Error Type
         ↓
    Quota Exceeded? → Fail immediately
         ↓
    Rate Limit? → Wait (2x delay, max 30s), Retry
         ↓
    Server Error? → Wait (exponential), Retry
         ↓
    Max Retries? → Fail with detailed error
         ↓
    Success? → Return result
```

### 2. External API Services

**Files Modified:**
- `backend/src/services/search_service.py` (SerpAPI)
- `backend/src/services/firecrawl_service.py` (Firecrawl)

**Features Added:**
- **Specific Error Detection**:
  - Quota/Billing errors → Clear message about checking billing
  - Rate limit errors → Clear message about trying later
  - Server errors → Clear message about temporary issue
  - Generic errors → Standard error message
- **User-Friendly Error Messages**: Instead of technical error codes, users see actionable messages
- **Graceful Degradation**: Tools fail gracefully but the system continues with available data

**Error Messages:**
- **Quota Exceeded**: "API quota exceeded. Please check your [Service] billing."
- **Rate Limited**: "API rate limit exceeded. Please try again later."
- **Server Error**: "[Service] server error. Please try again later."
- **Generic**: "Search/Scraping failed: [error]"

## Retry Strategy

### AI Agents
- **Max Retries**: 3 attempts
- **Base Delay**: 2^attempt seconds (1s, 2s, 4s)
- **Rate Limit Delay**: 2x base delay, capped at 30s
- **No Retry Cases**:
  - Invalid argument errors (user error)
  - Quota exceeded (billing issue)

### External Services
- No automatic retry (services handle internally)
- Better error classification and messaging
- System continues with partial data

## Error Scenarios Handled

1. ✅ **Gemini API Quota Exceeded**
   - No retry, immediate failure
   - Clear error message to check billing
   - User can upgrade plan

2. ✅ **Gemini API Rate Limited (429)**
   - Automatic retry with exponential backoff
   - Extended delay for rate limits
   - Success on retry if within limits

3. ✅ **Gemini Server Overload (500-504)**
   - Automatic retry with backoff
   - System tries again after delay
   - Fails gracefully after 3 attempts

4. ✅ **SerpAPI Quota Exceeded**
   - Clear error message
   - Research continues with cached data
   - User notified of limitation

5. ✅ **SerpAPI Rate Limited**
   - Retry with backoff
   - System tries alternative search queries
   - Continues with available data

6. ✅ **Firecrawl Quota Exceeded**
   - Clear error message
   - Uses web search results instead
   - Lower quality but functional

7. ✅ **Invalid Model Name**
   - No retry (user error)
   - Fixed in config to use correct format
   - System validates before running

## Best Practices Implemented

1. **Never Retry on User Errors**: Invalid arguments, bad requests
2. **Exponential Backoff**: Prevents overwhelming servers
3. **Different Strategies**: AI agents retry, external services don't
4. **Clear Error Messages**: Users know what to do
5. **Graceful Degradation**: System continues with partial data
6. **Comprehensive Logging**: All errors logged for debugging
7. **Version Compatibility**: Works with different library versions

## Testing Scenarios

To test the error handling:

1. **Quota Exceeded**: Use up SerpAPI/Firecrawl credits
2. **Rate Limit**: Make many rapid requests
3. **Server Error**: Monitor logs during 500-504 errors
4. **Invalid Config**: Test with wrong model names

## Monitoring

All errors are logged with:
- Error type and message
- Retry attempts
- Success/failure status
- Source (agent, service, API)

Check logs in:
- Backend console output
- Application logs
- Error tracking systems
