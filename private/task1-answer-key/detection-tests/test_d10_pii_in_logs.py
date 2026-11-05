"""D10: PII and health data (NIK, name, diagnosis) appear in log output.

Log messages should not contain identifiable patient information.
"""
import inspect
import re


def test_no_pii_in_logs():
    import app as app_module
    source = inspect.getsource(app_module)

    log_calls = re.findall(r'logger\.\w+\(.*?\)', source, re.DOTALL)

    pii_in_logs = False
    pii_fields = ["nik", "name", "diagnosis", "patient"]
    for call in log_calls:
        call_lower = call.lower()
        if any(field in call_lower for field in pii_fields):
            if "f\"" in call or "f'" in call or ".format(" in call or "%" in call:
                pii_in_logs = True
                break

    has_masking = any(
        keyword in source.lower()
        for keyword in ["mask", "redact", "hash", "anonymi", "***", "xxxx"]
    )

    assert not pii_in_logs or has_masking, (
        "Logger calls include patient PII (NIK, name, or diagnosis) "
        "in formatted strings without masking. This data ends up in "
        "log files accessible to operations staff."
    )
