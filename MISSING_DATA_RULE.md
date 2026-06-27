# Missing-data rule

When the job description doesn't provide a value the estimate needs:
- The field is set to null (never a guessed number).
- A short explanation is added to the "notes" field naming what was missing.
- For genuinely ambiguous jobs (even a human couldn't price them), the tool
  flags the estimate for human review in "notes" rather than committing to a number.

This rule is enforced in two places:
1. The prompt instructs the AI to follow it.
2. The validation code allows null for numeric fields (so a null is treated as
   "known missing", not an error), while still catching wrong types and bad math.