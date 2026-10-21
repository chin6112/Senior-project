# Chapter 4: Results

All numbers below were produced by `python evaluate_dual.py` and `pytest tests` on the committed data.

## 4.1 Unit tests

13 of 13 tests pass (7 rule tests, 6 policy tests).

## 4.2 Standard labeled set (`data/labeled/orders_labeled.csv`, 200 rows)

| Rule | Expected | Detected | TP | FP | FN | Precision | Recall | F1 |
|------|---------:|---------:|---:|---:|---:|----------:|-------:|---:|
| missing_id | 4 | 4 | 4 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| duplicate_id | 4 | 4 | 4 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| invalid_date | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| invalid_amount | 3 | 3 | 3 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| **Macro** | | | | | | **1.000** | **1.000** | **1.000** |

**Caveat.** The labels were aligned with the rule definitions (see `design_rationale.md`: `duplicate_id` flags every row sharing an ID; amounts such as 999999.99 are not labeled invalid). An F1 of 1.0 therefore shows the code matches its specification, not that the specification is complete.

## 4.3 Hard set (`data/labeled/orders_hard.csv`, 45 rows)

| Rule | Expected | Detected | TP | FP | FN | Precision | Recall | F1 |
|------|---------:|---------:|---:|---:|---:|----------:|-------:|---:|
| missing_id | 1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| duplicate_id | 0 | 0 | 0 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| invalid_date | 0 | 1 | 0 | 1 | 0 | 0.000 | 1.000 | 0.000 |
| invalid_amount | 0 | 1 | 0 | 1 | 0 | 0.000 | 1.000 | 0.000 |
| **Macro** | | | | | | **0.500** | **1.000** | **0.500** |

### Discussion

The engine flags exactly one row, row 26, which is fully blank (`,,,`). The label for it is `missing_id` only, but a blank row also has an unparseable date and a non-numeric amount, so the two extra detections are consistent with the rule definitions. The false positives come from an under-specified label, not from a rule malfunction.

The boundary values in this file (0.00, 0.01, 999999.99, 1000000.00, dates in 2020 and 2030, IDs such as `ORD 2014` and `X`) are labeled `clean` and none is flagged. They are therefore not evidence about detection quality. They describe what the current rules deliberately do not check: outlier amounts, date ranges, and ID format. These are listed as future work in Chapter 5.

## 4.4 User testing

Not yet conducted. Record results here after the sessions.

Task for each participant: "How many rows in this file have problems, and what must be fixed?"

| Participant | Time without tool | Time with tool | Rows found without | Rows found with | Where they got stuck |
|-------------|------------------:|---------------:|-------------------:|----------------:|----------------------|
| P1 | | | | | |
| P2 | | | | | |
| P3 | | | | | |
