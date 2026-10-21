# Abstract

This project develops the Order CSV Quality Monitor, a system that checks order CSV files for completeness, uniqueness and value validity using rules configured in YAML. Files that are not order data are profiled and checked with rules inferred from their content. The system decides PASS / WARN / FAIL, stores each run in SQLite and shows pass-rate trends in a Streamlit web interface.

All 19 unit tests pass. The standard labeled set (200 rows) scores F1 = 1.000 and the hard set (45 rows) scores F1 = 0.500; the latter results from an under-specified label for a blank row rather than a rule malfunction.

**Keywords:** data quality, CSV validation, Streamlit, rule-based validation
