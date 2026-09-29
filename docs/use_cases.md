# Use Cases and System Scope

## System Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| **Data Analyst** | Primary user | Uploads CSV files, reviews results, downloads reports |
| **Data Owner** | Data provider | Receives error reports, fixes data, re-uploads |
| **Data Steward** | Policy maker | Defines what constitutes "bad" data via rules.yaml |
| **Developer** | Evaluator | Runs evaluate.py, measures rule accuracy |
| **System (Time)** | Scheduler | ⊘ Triggers periodic checks (out of scope for MVP) |

## System Scope

The system covers **validation, history tracking, and reporting only**. Out of scope:
- Automatic data source ingestion
- Direct source system fixes
- Scheduled/triggered validation

```
     Upload CSV          Review Results      Download Report
         │                    │                     │
         ▼                    ▼                     ▼
    ┌─────────────────────────────────────────────────────┐
    │  Order CSV Quality Monitor                          │
    │                                                     │
    │  ├─ Validate Tab (UC-01, UC-02, UC-03)             │
    │  ├─ History Tab (UC-04)                            │
    │  └─ Evaluation Tab (UC-06)                         │
    │                                                     │
    │  Store: SQLite (runs + rule_results tables)         │
    └─────────────────────────────────────────────────────┘
```

---

## Use Case Descriptions

### UC-01: Validate Order File (Primary)

| Field | Content |
|-------|---------|
| **ID** | UC-01 |
| **Name** | Validate Order File |
| **Actor** | Data Analyst |
| **Goal** | Determine if the file is ready for sales analysis |
| **Precondition** | App is running; CSV file available locally |
| **Postcondition** | Validation result stored in runs + rule_results tables |

**Main Flow:**
1. Analyst opens Validate tab
2. System prompts file upload; displays required columns (order_id, order_date, amount)
3. Analyst selects orders.csv
4. System reads CSV into DataFrame
5. System verifies all required columns present
6. System runs 4 validation rules from config/rules.yaml
7. System evaluates status: PASS / WARN / FAIL (based on thresholds)
8. System saves run to database with timestamp and filename
9. System displays 3 metrics: rows checked, rows with issues, critical failures
10. Analyst reviews results and decides: proceed or return for corrections

**Alternate Flows:**
- **A1 — Parse Error:** Step 4 fails → system shows error message → does NOT save run
- **A2 — Missing Columns:** Step 5 detects missing columns → lists them and stops
- **A3 — All Rows Pass:** Step 10 shows "All rows passed the checks"
- **A4 — Duplicate Upload:** (Not yet implemented) Check file hash; if identical to last run, display cached result

**Special Notes:** Row numbers count header as row 1. Files with embedded newlines may not align with text editor line numbers.

---

### UC-02: View Error Details

**Extends:** UC-01 (when errors found)

When UC-01 detects errors:
1. System displays bar chart: rules triggered vs. failure count
2. System shows table: csv_row, human-readable rule name, column, severity (sorted by row number)
3. Analyst identifies which rows to fix and what column caused it

**Why this matters:** Without per-row attribution, the analyst would have to manually re-read the file.

---

### UC-03: Download Failure Report

**Extends:** UC-01 (when errors found)

1. Analyst clicks "Download failure report"
2. System exports failures table as CSV
3. Analyst sends file to Data Owner

**Alternate:** If no errors, download button is hidden (empty report would be confusing)

---

### UC-04: View Quality Trends

| Field | Content |
|-------|---------|
| **ID** | UC-04 |
| **Name** | Monitor Data Quality Over Time |
| **Actors** | Data Analyst, Data Steward |
| **Goal** | Answer: Is data quality improving or declining? |
| **Precondition** | At least 1 prior validation run exists |
| **Postcondition** | N/A (read-only) |

**Main Flow:**
1. User opens History tab
2. System queries last 50 runs from runs table
3. System shows: latest pass_rate, average pass_rate
4. System displays table: run timestamp, filename, rows checked, rows failed, pass_rate
5. System plots pass_rate trend over time (line chart)
6. System displays dropdown to select a rule
7. When rule selected, system plots failure count trend for that rule
8. User identifies which data quality issues are trending worse

**Alternate:** If no history exists, show message inviting upload at Validate tab

**Known Limitation:** This use case is partially broken by Phase 1 bug (st.stop() prevents History access without upload). Will be fixed when st.stop() removed.

---

### UC-05: Edit Rules and Thresholds ⊘ (Partial)

| Field | Content |
|-------|---------|
| **ID** | UC-05 |
| **Name** | Configure Validation Rules |
| **Actor** | Data Steward |
| **Goal** | Adjust rules without touching Python code |
| **Status** | Partial — rules implemented, thresholds not yet integrated |

**Workflow:**
1. Steward edits config/rules.yaml:
   - Add new rule
   - Change severity (critical → warning)
   - Adjust min_pass_rate threshold
2. Steward saves file
3. System reloads config on next validation run
4. New thresholds take effect

**Why this matters:** Answers "who defines what 'bad' data is?" Currently rules are in YAML, thresholds still hard-coded in policy.py.

**Not Yet Implemented:** dq/policy.py loads thresholds from config, so UC-05 incomplete.

---

### UC-06: Evaluate Rule Accuracy ⊘

| Field | Content |
|-------|---------|
| **ID** | UC-06 |
| **Name** | Measure Validation Accuracy |
| **Actor** | Developer / QA Engineer |
| **Goal** | Verify rules detect what they claim to detect |
| **Precondition** | Labeled test dataset (200 rows with expected_rules column) |
| **Postcondition** | evaluation_results.csv with per-rule metrics |

**Workflow:**
1. Developer runs `python evaluate.py`
2. System loads data/labeled/orders_labeled.csv
3. System runs validation rules on it
4. System compares detected_rules vs. expected_rules per row
5. System calculates TP, FP, FN per rule
6. System reports: Precision, Recall, F1-score
7. Developer reviews metrics and identifies rules needing refinement

**Current Results (Phase 3):**
```
Rule              Precision  Recall  F1-Score
───────────────────────────────────────────
missing_id        1.000      1.000   1.000 ✅
invalid_date      1.000      1.000   1.000 ✅
invalid_amount    1.000      0.750   0.857 ✅
duplicate_id      0.500      1.000   0.667 ⚠️

Macro-average:    0.875      0.938   0.881
```

**Why this matters:** Transforms project from "tool" to "research" — answers "how do you know the rules work?"

---

## Use Case Implementation Status

| UC | Name | Status | Phase | Blocker |
|----|----|--------|-------|---------|
| UC-01 | Validate File | ✅ 95% done | P0 | Missing A4 (hash dedup) |
| UC-02 | View Errors | ✅ Done | P1 | None |
| UC-03 | Download Report | ✅ Done | P1 | None |
| UC-04 | Quality Trends | ⚠️ 80% done | P2 | st.stop() blocks access; rule_trend() unused |
| UC-05 | Configure Rules | 🔲 50% done | P3 | Thresholds not in policy.py |
| UC-06 | Evaluate Accuracy | ✅ 100% done | P3 | None |

**Critical Path:** UC-01, UC-02, UC-03 are the "usable" system.
**Differentiator:** UC-06 is what makes this "research-grade" rather than "tool-grade."
UC-04 is what makes it "monitoring" rather than "batch validation."

---

## Design Decisions

### Why Separate Validation from Policy?

**Without separation:** `app.py` would do everything—read, validate, decide PASS/FAIL, display.
- Hard to test (requires Streamlit mock)
- Hard to reuse logic (other tools can't call it)
- Hard to reason about (business logic tangled with UI)

**With separation:**
- `dq/engine.py`: Pure function, testable
- `dq/policy.py`: Pure function, testable
- `dq/service.py`: Orchestrates both, handles failures
- `app.py`: Only UI concerns

### Why Labeled Evaluation Dataset?

**Without evaluation:** How do you know `duplicate_id` rule works?
- "I tested it manually" — not reproducible
- "It found duplicates" — that's not precision/recall

**With evaluation:** You run `evaluate.py`, get metrics table, can prove:
- Rule detects 93.8% of real issues (recall)
- When it flags something, 87.5% of the time it's actually wrong (precision)

This is the difference between "I built a tool" and "I built and validated a system."

### Why SQLite History?

**Single-run validator** answers: "Is this file good?"
**Multi-run monitor** answers: "Are my data quality practices improving?"

History enables detection of:
- Systemic issues (same rule failing on 80% of uploads → need to fix source)
- Improving trends (pass_rate climbing → data team is getting better)
- Seasonal patterns (maybe every Friday's batch is worse → investigate Friday process)

---

## Scope Not Included (Future Work)

These would extend the system but are out of scope for this project:

1. **Scheduled Validation** — Auto-check every morning (requires job scheduler)
2. **Alerting** — Slack/Discord when critical count spikes (requires webhook integration)
3. **Multi-dataset** — Currently hardcoded to "orders"; could generalize
4. **PostgreSQL Persistence** — SQLite is ephemeral on Streamlit Cloud
5. **Programmatic API** — FastAPI wrapper for non-Streamlit consumers
6. **Anomaly Detection** — ML model to flag unusual data patterns

---

## Validation with Labeled Data

### Why Ground Truth Matters

When you test with `data/labeled/orders_labeled.csv`:
- **Expected column:** Human-annotated `expected_rules` (e.g., "invalid_date|duplicate_id")
- **Detected column:** What the system found
- **Comparison:** Did system find what was expected?

Example row analysis:
```
Row 50:
  order_id:       ""
  order_date:     2026-02-20
  amount:         120.50
  expected_rules: "missing_id"
  detected:       "missing_id" ✅ TP

Row 75:
  order_id:       ORD-1075
  order_date:     2026-03-01
  amount:         -5.00
  expected_rules: "invalid_amount"
  detected:       "invalid_amount" ✅ TP
  
Row 120:
  order_id:       ORD-1120
  order_date:     invalid-date
  amount:         250.00
  expected_rules: "invalid_date"
  detected:       ""  ❌ FN (we missed it)
```

Per-rule metrics answer: "How often do we miss issues?" and "How often do we cry wolf?"

---

## Conclusion: The Difference This Makes

**Without UC-06:** "We built a CSV validator that checks 4 rules."
- ✓ Works
- ✓ Shows results
- ✗ Can't prove it works correctly
- ✗ Hard to defend to reviewers

**With UC-06:** "We built and validated a CSV quality monitor. On a 200-row labeled test set with ground truth, our rules achieve 88.1% F1-score (87.5% precision, 93.8% recall). Errors are per-row attributed for actionable correction."
- ✓ Works
- ✓ Shows results
- ✓ Measurable accuracy
- ✓ Credible to reviewers
- ✓ Replicable methodology
