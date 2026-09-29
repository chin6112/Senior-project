import pandas as pd
import yaml
from pathlib import Path


def _not_null(s):
    v = s.astype("string").str.strip()
    return v.isna() | v.eq("")


def _unique(s):
    v = s.astype("string").str.strip()
    # Only flag as duplicate if it's non-empty AND appears more than once
    is_blank = v.isna() | v.eq("")
    duplicated_mask = v.duplicated(keep=False)
    return duplicated_mask & ~is_blank


def _parseable_date(s):
    return pd.to_datetime(s, errors="coerce").isna()


def _numeric_min(s, min_value=0):
    n = pd.to_numeric(s, errors="coerce")
    return n.isna() | n.lt(min_value)


CHECKS = {
    "not_null": _not_null,
    "unique": _unique,
    "parseable_date": _parseable_date,
    "numeric_min": _numeric_min,
}


DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config" / "rules.yaml"


def load_config(path=None):
    config_path = Path(path or DEFAULT_CONFIG)
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_checks(df: pd.DataFrame, config: dict) -> tuple[set[str], pd.DataFrame]:
    missing = set(config["required_columns"]) - set(df.columns)
    if missing:
        return missing, pd.DataFrame(columns=["csv_row", "rule", "column", "severity"])

    records = []
    for rule in config["rules"]:
        fn = CHECKS[rule["check"]]
        kwargs = {"min_value": rule.get("min")} if rule["check"] == "numeric_min" else {}
        failed = fn(df[rule["column"]], **kwargs).fillna(False)
        for idx in df.index[failed]:
            records.append({
                "csv_row": int(idx) + 2,
                "rule": rule["name"],
                "column": rule["column"],
                "severity": rule["severity"],
            })

    return set(), pd.DataFrame(records, columns=["csv_row", "rule", "column", "severity"])
