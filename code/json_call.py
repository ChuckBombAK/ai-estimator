import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Read one sample job description
with open("data/sample_1_easy.txt", "r") as f:
    job_text = f.read()

# Read your hand-written perfect output to show the AI the exact shape you want
with open("perfect_output.json", "r") as f:
    schema_example = f.read()

prompt = f"""You are an estimator for a painting contractor.
Read the job description below and return ONLY valid JSON, no other text.

The JSON must match this exact shape and field names:
{schema_example}

Rules:
- Each line_total must equal quantity * unit_price.
- grand_total must equal the sum of all line_total values.
- If a value is missing from the description, use null and explain in "notes". Do not invent numbers.

Job description:
{job_text}
"""

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1500,
    messages=[{"role": "user", "content": prompt}],
)

print(response.content[0].text)