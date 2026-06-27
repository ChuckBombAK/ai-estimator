"""
estimator.py — Core pipeline for the AI Estimator (painting).
Takes a raw job description, calls the AI, and returns a structured estimate.
"""

import os
import json
import time
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-6"
REQUIRED_FIELDS = ["job_title", "line_items", "grand_total", "notes"]


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
    """Strips any stray text/markdown and parses the JSON into a dictionary.
    Returns the dictionary, or None if it can't be parsed."""
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(raw_text[start:end + 1])
    except json.JSONDecodeError:
        return None


def estimate_from_text(job_text):
    """The core function: raw job text in, structured estimate dictionary out.
    Returns None if the AI response could not be parsed."""
    prompt = build_prompt(job_text)

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text
    return extract_json(raw_text)


# --- Day 1: run the function across all the EASY samples ---

EASY_SAMPLES = [
    "sample_1_easy.txt",
    "sample_2_exterior.txt",
]


def run_easy_samples():
    """Runs every easy sample through the core function and logs a quick summary."""
    print(f"{'sample':<28}{'parsed?':<10}{'fields present?':<16}")
    print("-" * 54)

    for filename in EASY_SAMPLES:
        with open(f"data/{filename}", "r") as f:
            job_text = f.read()

        result = estimate_from_text(job_text)

        if result is None:
            print(f"{filename:<28}{'NO':<10}{'-':<16}")
            continue

        fields_ok = all(field in result for field in REQUIRED_FIELDS)
        print(f"{filename:<28}{'yes':<10}{('yes' if fields_ok else 'MISSING'):<16}")

        # Save each result so we can spot-check it by hand
        out_name = filename.replace(".txt", "_result.json")
        with open(f"outputs/{out_name}", "w") as f:
            json.dump(result, f, indent=2)


if __name__ == "__main__":
    run_easy_samples()