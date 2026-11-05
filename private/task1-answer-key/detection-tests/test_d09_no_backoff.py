"""D9: No exponential backoff and 429 responses are not handled.

The retry logic should use exponential backoff and respect Retry-After
headers from 429 responses.
"""
import inspect

from app import submit_claim_to_api


def test_retry_has_backoff_and_429_handling():
    source = inspect.getsource(submit_claim_to_api)

    has_429_handling = "429" in source or "Retry-After" in source or "retry_after" in source
    has_backoff = "**" in source or "pow" in source or "2 *" in source or "backoff" in source

    assert has_429_handling, (
        "submit_claim_to_api() does not handle HTTP 429 responses. "
        "Fixed-delay retries during rate limiting make the problem worse."
    )
    assert has_backoff, (
        "submit_claim_to_api() uses fixed sleep(1) with no backoff. "
        "Retries should use exponential backoff."
    )
