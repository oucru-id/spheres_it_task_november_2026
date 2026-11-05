"""D8: Pending claims query has no LIMIT.

The sync function should batch pending claims rather than loading all
into memory at once.
"""
import ast
import inspect

from app import sync_pending_claims


def test_sync_uses_limit():
    source = inspect.getsource(sync_pending_claims)

    has_limit = "LIMIT" in source or "limit" in source
    assert has_limit, (
        "sync_pending_claims() fetches all unsynced claims with no LIMIT. "
        "With thousands of pending claims, this loads everything into memory at once."
    )
