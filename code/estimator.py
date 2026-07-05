"""
estimator.py — Core pipeline for the AI Estimator (painting).
Takes a raw job description, calls the AI, validates the result, and returns it.
Also scores all samples against the hand-written answer keys.
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


# --- Scoring: compare a tool result to the hand-written answer, field by field ---

def score_against_answer(tool_estimate, answer):
    """Counts correct fields vs total fields for one sample.
    Returns (correct, total)."""
    correct = 0
    total = 0

    # Top-level simple fields
    for field in ["job_title", "grand_total"]:
        total += 1
        if tool_estimate.get(field) == answer.get(field):
            correct += 1

    # notes: count as correct if both have a note when the answer does
    total += 1
    if bool(tool_estimate.get("notes")) == bool(answer.get("notes")):
        correct += 1

    # Line items, compared position by position
    tool_items = tool_estimate.get("line_items", [])
    answer_items = answer.get("line_items", [])
    for i in range(max(len(tool_items), len(answer_items))):
        t_item = tool_items[i] if i < len(tool_items) else {}
        a_item = answer_items[i] if i < len(answer_items) else {}
        for field in ["task", "category", "quantity", "unit", "unit_price", "line_total"]:
            total += 1
            if t_item.get(field) == a_item.get(field):
                correct += 1

    return correct, total


# --- Run all 10 samples, score them, print overall accuracy ---

SAMPLES = [
    "sample_1_easy", "sample_2_exterior", "sample_3_vague",
    "sample_4_missing_measurement", "sample_5_unusual_material",
    "sample_6_kitchen", "sample_7_deck", "sample_8_office",
    "sample_9_vague", "sample_10_specialty",
]


def run_all_samples():
    print(f"{'sample':<32}{'parsed?':<10}{'valid?':<10}{'score':<10}")
    print("-" * 62)

    total_correct = 0
    total_fields = 0

    for name in SAMPLES:
        with open(f"sample_data/{name}.txt", "r") as f:
            job_text = f.read()

        result = estimate_from_text(job_text)
        estimate = result["estimate"]
        problems = result["problems"]

        parsed = "yes" if estimate else "NO"
        valid = "yes" if (estimate and not problems) else "FLAGGED"

        score_str = "-"
        if estimate:
            # answer key is sample_N_answer.json; map by number
            num = name.split("_")[1]
            answer_path = f"answer_key/sample_{num}_answer.json"
            if os.path.exists(answer_path):
                with open(answer_path, "r") as f:
                    answer = json.load(f)
                correct, fields = score_against_answer(estimate, answer)
                total_correct += correct
                total_fields += fields
                score_str = f"{correct}/{fields}"

            # save the output
            with open(f"outputs/{name}_result.json", "w") as f:
                json.dump(estimate, f, indent=2)

        print(f"{name:<32}{parsed:<10}{valid:<10}{score_str:<10}")

    if total_fields:
        pct = round(100 * total_correct / total_fields, 1)
        print("-" * 62)
        print(f"OVERALL ACCURACY: {total_correct}/{total_fields} fields = {pct}%")


if __name__ == "__main__":
    run_all_samples()