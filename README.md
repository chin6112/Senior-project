# Order CSV Quality Monitor

[![tests](https://github.com/your-username/your-repo/actions/workflows/tests.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/tests.yml)

A production-grade data quality monitoring system that validates order CSV files for completeness, uniqueness, and data integrity. It tracks validation results over time and provides historical trend analysis.

**Live Demo:** [Streamlit Cloud](#deployment) (see below for setup)

## Features

- **Real-time validation**: Upload CSVs and get instant feedback on data quality
- **Configurable rules**: Rules defined in YAML, no code changes needed
- **History tracking**: All validation runs stored in SQLite with trend analysis
- **Comprehensive checks**: Missing values, duplicates, invalid dates, negative amounts
- **Severity levels**: Distinguish between critical and warning-level issues
- **Test coverage**: Full pytest suite for validation logic

## Project Structure

```
├── app.py                           # Streamlit UI entry point
├── streamlit_app.py                 # Streamlit Cloud entry point
├── dq/
│   ├── engine.py                    # Validation logic & rule dispatch
│   ├── service.py                   # Orchestration layer
│   ├── policy.py                    # PASS/WARN/FAIL decision logic
│   └── store.py                     # SQLite history storage
├── config/
│   └── rules.yaml                   # Rule definitions + thresholds (configurable)
├── data/
│   ├── samples/                     # Sample CSV files
│   └── labeled/                     # Labeled test set with ground truth
├── tests/
│   ├── test_rules.py                # Validation rule tests
│   ├── test_policy.py               # Policy evaluation tests
│   └── test_store.py                # Database tests
├── scripts/
│   └── generate_labeled_data.py     # Generate test dataset
├── evaluate.py                      # Precision/recall metrics
├── .github/workflows/
│   └── tests.yml                    # GitHub Actions CI/CD
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
pytest tests/ -v
```

13 tests validate:
- **Rule logic** (7 tests): Each validation check (missing_id, duplicate_id, invalid_date, invalid_amount)
- **Policy logic** (6 tests): PASS/WARN/FAIL decision boundaries and thresholds

### Evaluation
```bash
python evaluate.py
```

Measures accuracy against 200-row labeled test dataset with ground truth:
- **Precision: 87.5%** — When we flag an issue, it's correct 87.5% of the time
- **Recall: 93.8%** — We catch 93.8% of real issues
- **F1-Score: 88.1%** — Balanced performance metric

Per-rule metrics saved to `evaluation_results.csv`

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

## Deployment

### GitHub Actions CI/CD

Every push runs automated tests and evaluation:
- `pytest` validates 13 tests
- `evaluate.py` runs accuracy metrics
- Results uploaded as artifact

Badge shows current status:
```markdown
[![tests](https://github.com/your-username/your-repo/actions/workflows/tests.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/tests.yml)
```

### Streamlit Community Cloud

Deploy the app to Streamlit Cloud for free:

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Connect GitHub repo
5. Set main file to `streamlit_app.py`
6. Deploy

**Note:** SQLite database (`dq_history.db`) is ephemeral on Streamlit Cloud (resets on app restart). For persistent history, upgrade to a PostgreSQL backend with Supabase or Heroku Postgres.

### Local Deployment (Docker)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "streamlit_app.py"]
```

Build and run:
```bash
docker build -t order-monitor .
docker run -p 8501:8501 order-monitor
```

## Future Extensions

- Alert thresholds (Slack/Discord notifications when critical count > N)
- PostgreSQL backend for persistent history across deployments
- Custom validation functions via plugin system
- Web API endpoint (FastAPI) for programmatic access
- Data profiling reports (distributions, outliers)
- ML-based anomaly detection for data quality trends

---

**CSV row numbers count the header as row 1.** Quoted multiline records may not match physical line numbers.
