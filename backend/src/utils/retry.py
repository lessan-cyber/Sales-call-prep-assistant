"""Utility module for retry logic with exponential backoff."""

import asyncio
from typing import Any, Callable
from pydantic_ai import Agent
from ..utils.logger import error


async def run_agent_with_retry(
    agent: Agent,
    prompt: str,
    max_retries: int = 3
) -> Any:
    """
    Run an agent with retry logic for handling API errors.

    Args:
        agent: The pydantic_ai agent to run
        prompt: The prompt to send to the agent
        max_retries: Maximum number of retry attempts

    Returns:
        The agent result

    Raises:
        Exception: If all retries are exhausted
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            result = await agent.run(prompt)
            return result
        except Exception as e:
            last_error = e
            error_msg = str(e).lower()

            # Check if this is a retryable error
            is_rate_limit = "429" in error_msg or "rate limit" in error_msg
            is_quota_exceeded = "quota" in error_msg or "billing" in error_msg
            is_invalid = "invalid" in error_msg and "argument" in error_msg

            # Non-retryable errors
            if is_invalid:
                error(f"Non-retryable error: {e}")
                raise

            if attempt < max_retries - 1:
                # Calculate backoff delay (exponential: 1s, 2s, 4s)
                delay = 2 ** attempt
                error(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")

                # Additional delay for specific error types
                if is_rate_limit:
                    delay = min(delay * 2, 30)  # Longer delay for rate limits
                elif is_quota_exceeded:
                    error(f"Quota exceeded: {e}. Not retrying.")
                    raise

                await asyncio.sleep(delay)
            else:
                error(f"All {max_retries} attempts failed. Last error: {e}")

    # If we get here, all retries failed
    raise last_error
