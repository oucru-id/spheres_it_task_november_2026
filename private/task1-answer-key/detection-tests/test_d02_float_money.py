"""D2: Money stored as float causes rounding errors.

Financial amounts should use integer cents (or Decimal), not float/REAL.
"""
import inspect

from database import SCHEMA
from models import BillRecord


def test_money_not_stored_as_float():
    uses_real = "REAL" in SCHEMA and "amount" in SCHEMA.lower()

    bill_source = inspect.getsource(BillRecord)
    uses_float_model = "float" in bill_source.lower() and "amount" in bill_source.lower()

    assert not (uses_real or uses_float_model), (
        "Financial amounts use float/REAL storage. "
        "33333.33 + 33333.33 + 33333.34 should equal 100000.00 exactly, "
        "but float arithmetic can produce 99999.99999999999. "
        "Use INTEGER (cents) or Decimal instead."
    )
