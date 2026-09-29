# Order CSV Quality Monitor

A production-grade data quality monitoring system that validates order CSV files for completeness, uniqueness, and data integrity. It tracks validation results over time and provides historical trend analysis.

## Features

- **Real-time validation**: Upload CSVs and get instant feedback on data quality
- **Configurable rules**: Rules defined in YAML, no code changes needed
- **History tracking**: All validation runs stored in SQLite with trend analysis
- **Comprehensive checks**: Missing values, duplicates, invalid dates, negative amounts
- **Severity levels**: Distinguish between critical and warning-level issues
- **Test coverage**: Full pytest suite for validation logic

## Project Structure

```
├── app.py                    # Streamlit UI (Validate & History tabs)
├── config/
│   └── rules.yaml            # Rule definitions (configurable)
├── dq/
│   ├── __init__.py
│   ├── engine.py             # Validation logic & rule dispatch
│   └── store.py              # SQLite history storage
├── tests/
│   ├── __init__.py
│   └── test_rules.py         # pytest validation tests
├── orders_with_issues.csv    # Test data with errors
├── orders_valid.csv          # Test data (clean)
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# or: source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

## Run

### Streamlit app
```bash
streamlit run app.py
```

Upload `orders_valid.csv` to see a clean run, or `orders_with_issues.csv` to see failures with detailed reports.

### Tests
```bash
pytest tests/test_rules.py -v
```

7 tests validate:
- Missing ID detection
- Duplicate ID detection  
- Invalid date detection
- Invalid amount detection
- Clean file passes all checks
- Missing required columns error handling
- All errors detected in sample file

## Rules (config/rules.yaml)

Rules are defined in `config/rules.yaml`. Each rule has:
- **name**: Internal identifier
- **column**: Target column to check
- **check**: Validation function (not_null, unique, parseable_date, numeric_min)
- **severity**: critical or warning
- **min**: (for numeric_min) Minimum allowed value

Example:
```yaml
rules:
  - name: missing_id
    column: order_id
    check: not_null
    severity: critical
  - name: duplicate_id
    column: order_id
    check: unique
    severity: critical
```

## Validation Checks

| Check | Description |
|-------|-------------|
| **not_null** | Column value is not empty or whitespace |
| **unique** | Value appears only once (ignores blanks) |
| **parseable_date** | Value parses as a valid date |
| **numeric_min** | Value is numeric and ≥ min (default 0) |

## Database Schema

Two tables track history:

**runs** - Summary of each validation run
```sql
run_id, run_at, file_name, rows_checked, rows_failed, pass_rate
```

**rule_results** - Detailed failures per rule per run
```sql
run_id, rule, severity, failed_count
```

## History Tab

The History tab shows:
- All past validation runs (pass rate, rows checked, failures)
- Pass rate trend chart over time
- Aggregate metrics (latest, average pass rates)

Enables detection of:
- Declining data quality trends
- Specific rules that are failing repeatedly
- File-level patterns (e.g., do orders from specific sources have more issues)

## CSV Row Numbers

CSV row numbers in reports count the header as row 1. Multi-line records (with embedded newlines) may shift physical line numbers—the number reported is the logical row in the DataFrame, which is canonical for programmatic fixes.

## Dependencies

- **pandas**: Data processing
- **streamlit**: Web UI
- **pyyaml**: Config file parsing
- **pytest**: Test runner (dev)

## Future Extensions

- Alert thresholds (Slack/Discord when critical count > N)
- Precision/recall metrics against known answer sets
- Custom validation functions via plugins
- Deployment to Streamlit Community Cloud

---

**CSV row numbers count the header as row 1.** Quoted multiline records may not match physical line numbers.
