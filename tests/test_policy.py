import pandas as pd
import pytest
from dq.policy import PolicyEvaluator
from dq.engine import load_config


CONFIG = load_config()


def test_pass_no_failures():
    evaluator = PolicyEvaluator(CONFIG)
    failures = pd.DataFrame(columns=["rule", "severity", "csv_row"])
    assert evaluator.evaluate(failures) == "PASS"


def test_pass_within_thresholds():
    evaluator = PolicyEvaluator(CONFIG)
    failures = pd.DataFrame({
        "rule": ["invalid_date", "invalid_date"],
        "severity": ["warning", "warning"],
        "csv_row": [3, 5],
    })
    assert evaluator.evaluate(failures) == "PASS"


def test_fail_critical_over_threshold():
    evaluator = PolicyEvaluator(CONFIG)
    failures = pd.DataFrame({
        "rule": ["missing_id"],
        "severity": ["critical"],
        "csv_row": [3],
    })
    assert evaluator.evaluate(failures) == "FAIL"


def test_warn_warnings_over_threshold():
    evaluator = PolicyEvaluator(CONFIG)
    warnings = [{"rule": f"invalid_date", "severity": "warning", "csv_row": i} for i in range(15)]
    failures = pd.DataFrame(warnings)
    assert evaluator.evaluate(failures) == "WARN"


def test_reason_no_failures():
    evaluator = PolicyEvaluator(CONFIG)
    failures = pd.DataFrame(columns=["rule", "severity", "csv_row"])
    assert "passed" in evaluator.get_reason(failures).lower()


def test_reason_with_failures():
    evaluator = PolicyEvaluator(CONFIG)
    failures = pd.DataFrame({
        "rule": ["missing_id", "invalid_date"],
        "severity": ["critical", "warning"],
        "csv_row": [3, 5],
    })
    reason = evaluator.get_reason(failures)
    assert "critical" in reason.lower() and "warning" in reason.lower()
