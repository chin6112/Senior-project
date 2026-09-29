import pandas as pd
import pytest
from dq.engine import run_checks, load_config


CONFIG = load_config()


def test_detects_missing_id():
    df = pd.DataFrame({
        "order_id": ["ORD-1", "", "ORD-3"],
        "order_date": ["2026-09-27", "2026-09-28", "2026-09-29"],
        "amount": [10.0, 20.0, 30.0],
    })
    _, failures = run_checks(df, CONFIG)
    assert (3, "missing_id") in set(zip(failures["csv_row"], failures["rule"]))


def test_detects_duplicate_id():
    df = pd.DataFrame({
        "order_id": ["ORD-1", "ORD-2", "ORD-1"],
        "order_date": ["2026-09-27", "2026-09-28", "2026-09-29"],
        "amount": [10.0, 20.0, 30.0],
    })
    _, failures = run_checks(df, CONFIG)
    found = set(zip(failures["csv_row"], failures["rule"]))
    assert (2, "duplicate_id") in found
    assert (4, "duplicate_id") in found


def test_detects_invalid_date():
    df = pd.DataFrame({
        "order_id": ["ORD-1", "ORD-2", "ORD-3"],
        "order_date": ["2026-09-27", "not-a-date", "2026-09-29"],
        "amount": [10.0, 20.0, 30.0],
    })
    _, failures = run_checks(df, CONFIG)
    assert (3, "invalid_date") in set(zip(failures["csv_row"], failures["rule"]))


def test_detects_invalid_amount():
    df = pd.DataFrame({
        "order_id": ["ORD-1", "ORD-2", "ORD-3"],
        "order_date": ["2026-09-27", "2026-09-28", "2026-09-29"],
        "amount": [10.0, -5.0, "not-a-number"],
    })
    _, failures = run_checks(df, CONFIG)
    found = set(zip(failures["csv_row"], failures["rule"]))
    assert (3, "invalid_amount") in found
    assert (4, "invalid_amount") in found


def test_clean_file_has_no_failures():
    df = pd.DataFrame({
        "order_id": ["ORD-1", "ORD-2", "ORD-3"],
        "order_date": ["2026-09-27", "2026-09-28", "2026-09-29"],
        "amount": [10.0, 20.0, 30.0],
    })
    _, failures = run_checks(df, CONFIG)
    assert failures.empty


def test_missing_required_columns():
    df = pd.DataFrame({"order_id": ["ORD-1"]})
    missing, _ = run_checks(df, CONFIG)
    assert missing == {"order_date", "amount"}


def test_detects_all_issues_in_sample_file():
    df = pd.read_csv("orders_with_issues.csv")
    _, failures = run_checks(df, CONFIG)
    found = set(zip(failures["csv_row"], failures["rule"]))

    expected = {
        (3, "invalid_date"),
        (4, "invalid_amount"),
        (4, "duplicate_id"),
        (5, "duplicate_id"),
        (6, "missing_id"),
        (6, "invalid_amount"),
        (7, "invalid_amount"),
    }
    assert expected <= found, f"Missing: {expected - found}"
