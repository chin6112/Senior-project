import pandas as pd
from dq.engine import infer_config, run_checks
from dq.service import ValidationService


def _failures(df):
    config, _ = infer_config(df)
    _, failures = run_checks(df, config)
    return set(zip(failures["csv_row"], failures["rule"]))


def test_detects_duplicate_rows():
    df = pd.DataFrame({"a": ["x", "y", "x"], "b": ["1", "2", "1"]})
    found = _failures(df)
    assert (2, "duplicate_row") in found
    assert (4, "duplicate_row") in found


def test_detects_bad_numeric_values_in_numeric_column():
    df = pd.DataFrame({"score": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "n/a", "12", "13", "14", "15", "16", "17", "18", "19", "20"]})
    assert (12, "score: not numeric") in _failures(df)


def test_detects_bad_dates_in_date_column():
    dates = ["2026-01-%02d" % d for d in range(1, 21)]
    dates[4] = "not-a-date"
    df = pd.DataFrame({"when": dates})
    assert (6, "when: invalid date") in _failures(df)


def test_flags_rare_missing_values_but_not_mostly_empty_columns():
    df = pd.DataFrame({
        "mostly_filled": ["a"] * 98 + ["", "b"],
        "mostly_empty": [""] * 90 + ["z"] * 10,
    })
    found = _failures(df)
    assert (100, "mostly_filled: missing") in found
    assert not any(rule.startswith("mostly_empty") for _, rule in found)


def test_duplicate_key_flagged_only_for_id_like_columns():
    df = pd.DataFrame({
        "user_id": [str(i) for i in range(30)] + ["0"],
        "city": [str(i) for i in range(30)] + ["0"],
    })
    rules = {rule for _, rule in _failures(df)}
    assert "user_id: duplicate" in rules
    assert "city: duplicate" not in rules


def test_service_falls_back_to_generic_for_non_orders_file():
    service = ValidationService()
    try:
        result = service.process_file(b"id,name\n1,a\n1,a\n", "other.csv")
    finally:
        service.close()
    assert result["success"]
    assert result["data"]["dataset"] == "generic"
    assert not result["data"]["failures"].empty
