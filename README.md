# Order CSV Quality Monitor

A small Streamlit app for checking order CSV files before sales analysis. It checks required columns, blank and duplicate order IDs, invalid dates, and missing, non-numeric, or negative amounts.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Upload `orders_valid.csv` to see a clean run, or `orders_with_issues.csv` to see failures and download a report. CSV row numbers count the header as row 1; CSV records containing embedded newlines may not match physical line numbers.