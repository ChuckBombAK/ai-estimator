"""
estimator.py — Core pipeline for the AI Estimator (painting).
Takes a raw job description, calls the AI, validates the result, and returns it.
"""

import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

from validate import validate_estimate

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-6"


def build_prompt(job_text):
    """Builds the full prompt: instruction + schema example + the job description."""
    with open("perfect_output.json", "r") as f:
        schema_example = f.read()

    return f"""You are an estimator for a painting contractor.
Read the job description below and return ONLY valid JSON, no other text.

The JSON must match this exact shape and field names:
{schema_example}

Rules:
- Each line_total must equal quantity * unit_price.
- grand_total must equal the sum of all line_total values.
- If a value is missing from the description, use null and explain in "notes".
  Do not invent numbers.

Job description:
{job_text}
"""


def extract_json(raw_text):
    """Strips stray text/markdown and parses JSON. Returns a dict, or None."""
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(raw_text[start:end + 1])
    except json.JSONDecodeError:
        return None


def estimate_from_text(job_text):
    """Core function: raw job text in, validated estimate out.
    Returns a dict: {"estimate": <dict or None>, "problems": [<strings>]}."""
    prompt = build_prompt(job_text)

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    estimate = extract_json(response.content[0].text)

    if estimate is None:
        return {"estimate": None, "problems": ["could not parse JSON from AI response"]}

    problems = validate_estimate(estimate)
    return {"estimate": estimate, "problems": problems}


# --- Run across the easy samples and log a quick summary ---

EASY_SAMPLES = ["sample_1_easy.txt", "sample_2_exterior.txt"]


def run_easy_samples():
    print(f"{'sample':<28}{'parsed?':<10}{'valid?':<10}")
    print("-" * 48)

    for filename in EASY_SAMPLES:
        with open(f"data/{filename}", "r") as f:
            job_text = f.read()

        result = estimate_from_text(job_text)
        estimate = result["estimate"]
        problems = result["problems"]

        parsed = "yes" if estimate else "NO"
        valid = "yes" if (estimate and not problems) else "FLAGGED"
        print(f"{filename:<28}{parsed:<10}{valid:<10}")

        if estimate:
            out_name = filename.replace(".txt", "_result.json")
            with open(f"outputs/{out_name}", "w") as f:
                json.dump(estimate, f, indent=2)
            for p in problems:
                print(f"    flag: {p}")