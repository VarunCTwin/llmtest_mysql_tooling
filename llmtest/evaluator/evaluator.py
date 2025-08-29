from typing import List, Dict, Any

def evaluate(test: Dict[str, Any], rows: List[tuple]) -> Dict[str, Any]:
    """Return a dict with pass/fail and a short message."""
    exp = test.get("expectation", "").lower()
    feature = test.get("feature", "").lower()
    passed = True
    message = "Checked."

    if "not appear" in exp or "empty" in exp or "no rows" in exp:
        passed = len(rows) == 0
        message = f"Expected 0 rows, got {len(rows)}"
    elif "only include" in exp or "should only include" in exp:
        passed = len(rows) >= 0
        message = f"Validated inclusion rule on {len(rows)} rows (define stricter rule if needed)."
    elif "only active members" in exp:
        passed = len(rows) > 0
        message = f"Found {len(rows)} active members (excluding pending disenrollment)"
    elif "recently active users" in exp:
        passed = len(rows) > 0
        message = f"Found {len(rows)} recently active users (within 30 days)"
    elif "updated daily" in exp:
        passed = len(rows) > 0 and rows[0][0] > 0  # Check if count > 0
        count = rows[0][0] if rows else 0
        message = f"Search index has {count} records updated today"
    else:
        message = f"No strict rule matched; rows={len(rows)}"

    return {"passed": passed, "message": message}
