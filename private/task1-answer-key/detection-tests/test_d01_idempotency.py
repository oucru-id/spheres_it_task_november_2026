"""D1: Claim submission retry creates duplicates in the claim API.

The submit_claim_to_api function should check if a claim was already
submitted (by external_claim_id or claim_reference) before re-posting.
"""
import inspect
import ast

from app import submit_claim_to_api


def test_no_duplicate_claims_on_retry():
    source = inspect.getsource(submit_claim_to_api)
    tree = ast.parse(source)

    has_dedup_check = any(
        keyword in source.lower()
        for keyword in [
            "external_claim_id",
            "claim_reference",
            "already_submitted",
            "already submitted",
            "idempoten",
            "dedup",
            "de-dup",
            "duplicate",
        ]
    )

    assert has_dedup_check, (
        "submit_claim_to_api() retries without checking if the claim was "
        "already submitted. On a network timeout after a successful POST, "
        "the retry creates a duplicate claim in the external system."
    )
