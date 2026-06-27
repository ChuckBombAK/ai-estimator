# AI Estimator (Painting)

Takes a plain-language painting job description and returns a structured cost
estimate (line items with quantity, unit, unit price, line total, and a grand total).

## How to run
1. Activate the environment: `source venv/bin/activate`
2. Install requirements: `pip3 install anthropic python-dotenv openai`
3. Add your API key to a `.env` file (never committed).
4. Run the estimator: `python3 code/estimator.py`
5. Validate an output: `python3 code/validate.py`

## Input
A plain-text painting job description (see `data/` for samples).

## Output
A JSON estimate saved to `outputs/`, with line items and a grand total.

## Missing-data rule
Missing values are returned as null with an explanation in "notes" — never guessed.

## Accuracy
[To be filled in once the full sample set is run.]