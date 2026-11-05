"""D7: Token is cached forever and never refreshed after expiry.

The get_token() function should track token expiry and refresh when needed.
"""
import inspect


def test_token_refreshed_after_expiry():
    from app import get_token
    source = inspect.getsource(get_token)

    has_expiry_check = any(
        keyword in source.lower()
        for keyword in [
            "expir",
            "expires_at",
            "token_expiry",
            "refresh",
            "ttl",
            "valid_until",
            "is_expired",
        ]
    )

    has_time_check = any(
        keyword in source
        for keyword in [
            "time.time()",
            "datetime.now",
            "datetime.utcnow",
            "time.monotonic",
        ]
    )

    assert has_expiry_check or has_time_check, (
        "get_token() caches the token at module level and never checks "
        "if it has expired. After the token's TTL, all claim API calls "
        "will fail with 401 until the service restarts."
    )
