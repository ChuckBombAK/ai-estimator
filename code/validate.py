"""
validate.py — Checks an estimate dictionary before we trust it.
Runs with no AI/API key: it only inspects JSON that's already been produced.
"""

REQUIRED_TOP_FIELDS = ["job_title", "line_items", "grand_total", "notes"]
REQUIRED_LINE_FIELDS = ["task", "category", "quantity", "unit", "unit_price", "line_total"]


def validate_estimate(estimate):
    """Checks one estimate dictionary. Returns a list of problem strings.
    An empty list means the estimate passed every check."""
    problems = []

    for field in REQUIRED_TOP_FIELDS:
        if field not in estimate:
            problems.append(f"missing top-level field: {field}")

    line_items = estimate.get("line_items")
    if not isinstance(line_items, list):
        problems.append("line_items is missing or not a list")
        return problems

    for i, item in enumerate(line_items):
        label = f"line_items[{i}]"

        for field in REQUIRED_LINE_FIELDS:
            if field not in item:
                problems.append(f"{label} missing field: {field}")

        qty = item.get("quantity")
        price = item.get("unit_price")
        line_total = item.get("line_total")

        for name, value in [("quantity", qty), ("unit_price", price), ("line_total", line_total)]:
            if value is not None and not isinstance(value, (int, float)):
                problems.append(f"{label} {name} should be a number, got {type(value).__name__}")

        if all(isinstance(v, (int, float)) for v in [qty, price, line_total]):
            expected = round(qty * price, 2)
            if round(line_total, 2) != expected:
                problems.append(f"{label} line_total {line_total} != quantity*unit_price ({expected})")

    grand_total = estimate.get("grand_total")
    line_totals = [item.get("line_total") for item in line_items]
    if isinstance(grand_total, (int, float)) and all(isinstance(t, (int, float)) for t in line_totals):
        expected_total = round(sum(line_totals), 2)
        if round(grand_total, 2) != expected_total:
            problems.append(f"grand_total {grand_total} != sum of line totals ({expected_total})")

    return problems


def is_valid(estimate):
    """Convenience: True if the estimate passes every check."""
    return len(validate_estimate(estimate)) == 0


if __name__ == "__main__":
    import json
    with open("perfect_output.json", "r") as f:
        perfect = json.load(f)
    problems = validate_estimate(perfect)
    if not problems:
        print("PASS — perfect_output.json passed every validation check.")
    else:
        print("FAIL — problems found:")
        for p in problems:
            print(f"  - {p}")