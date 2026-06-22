import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# The fields we expect every result to contain
EXPECTED_FIELDS = ["job_title", "line_items", "grand_total", "notes"]


def estimate_from_text(job_text):
    """Takes raw job text, returns a parsed dictionary (or None if it fails)."""

    with open("perfect_output.json", "r") as f:
        schema_example = f.read()

    prompt = f"""You are an estimator for a painting contractor.
Read the job description below and return ONLY valid JSON, no other text.

The JSON must match this exact shape and field names:
{schema_example}

Rules:
- Each line_total must equal quantity * unit_price.
- grand_total must equal the sum of all line_total values.
- If a value is missing, use null and explain in "notes". Do not invent numbers.

Job description:
{job_text}
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text

    # Strip anything before the first { and after the last } (handles stray text / markdown fences)
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        print("ERROR: No JSON object found in the response.")
        return None
    cleaned = raw[start:end + 1]

    # Parse safely so a bad response flags a problem instead of crashing
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        print("ERROR: Could not parse the response as JSON.")
        return None

    # Check every expected field is present; flag any that are missing
    for field in EXPECTED_FIELDS:
        if field not in data:
            print(f"WARNING: missing expected field '{field}'")

    return data


# --- Run it ---
with open("data/sample_1_easy.txt", "r") as f:
    job_text = f.read()

result = estimate_from_text(job_text)

if result:
    # Prove the parse worked by printing one field on its own
    print("Line items:")
    print(result["line_items"])

    # Save the parsed result to the outputs folder
    with open("outputs/sample_1_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("Saved to outputs/sample_1_result.json")