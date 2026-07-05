# Accuracy Scoring — AI Estimator

Our ground-truth answer keys are hand-written in `answer_key/`. Once the tool can
run, we score it **field by field** against these answers and compute an accuracy
percentage. Field-level scoring (not whole-document) is fairer and shows exactly
which field is weakest.

## How we score
For each sample, compare the tool's output to the hand-written answer, field by field:
- A field counts as **correct** if it matches the answer (for line items: task, category,
  quantity, unit, unit_price, line_total; plus job_title, grand_total, and the
  presence of a notes explanation).
- **Accuracy = correct fields / total fields**, across all 10 samples.
- For missing-data cases, "correct" means the tool returned `null` + a note where the
  answer key does, rather than inventing a number.

## Overall score

| Run | Date | Overall accuracy | Notes |
|---|---|---|---|
| Baseline | | | first run, before any fix |
| After fix | | | after improving the weakest field |

## Per-field breakdown (fill in after the baseline run)

| Field | Correct / Total | Accuracy | Most common problem |
|---|---|---|---|
| job_title | | | |
| task | | | |
| category | | | |
| quantity | | | |
| unit | | | |
| unit_price | | | |
| line_total | | | |
| grand_total | | | |
| notes (gap flagged) | | | |

## Per-sample results (fill in after the baseline run)

| Sample | Parsed? | Fields correct / total | Notes |
|---|---|---|---|
| sample_1_easy | | | |
| sample_2_exterior | | | |
| sample_3_vague | | | |
| sample_4_missing_measurement | | | |
| sample_5_unusual_material | | | |
| sample_6_kitchen | | | |
| sample_7_deck | | | |
| sample_8_office | | | |
| sample_9_vague | | | |
| sample_10_specialty | | | |

## Improvement log (Day 4)

- **Before accuracy:** [ ]
- **Worst field:** [ ]
- **Change made:** [ one thing only ]
- **After accuracy:** [ ]
- **Did any other field regress?:** [ ]
- **Improvement story (for Week 5):** [ was X%, changed this, now Y% ]