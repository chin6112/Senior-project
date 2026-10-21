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


def _blank(s):
    v = s.astype("string").str.strip()
    return v.isna() | v.eq("")


def _optional_date(s):
    # Blanks are reported by not_null, so only flag non-blank unparseable values.
    parsed = pd.to_datetime(s, errors="coerce", format="mixed", utc=True)
    return parsed.isna() & ~_blank(s)


def _optional_numeric(s):
    return pd.to_numeric(s, errors="coerce").isna() & ~_blank(s)


CHECKS = {
    "not_null": _not_null,
    "unique": _unique,
    "parseable_date": _parseable_date,
    "numeric_min": _numeric_min,
    "optional_date": _optional_date,
    "optional_numeric": _optional_numeric,
}

MAX_MISSING_RATE_AS_ERROR = 0.05
MIN_UNIQUE_RATE_FOR_KEY = 0.95
SAMPLE_SIZE = 1000


def _infer_kind(s, non_blank):
    if non_blank.empty:
        return "empty"
    if len(non_blank) < 5:
        return "text"
    if pd.api.types.is_numeric_dtype(s):
        return "numeric"
    sample = non_blank.head(SAMPLE_SIZE)
    if pd.to_numeric(sample, errors="coerce").notna().mean() >= 0.95:
        return "numeric"
    parsed = pd.to_datetime(sample, errors="coerce", format="mixed", utc=True)
    if parsed.notna().mean() >= 0.95:
        return "date"
    return "text"


def infer_config(df: pd.DataFrame, thresholds=None) -> tuple[dict, pd.DataFrame]:
    """Build rules for an arbitrary CSV from its own content; returns (config, column profile)."""
    rows = len(df)
    rules = []
    profile = []

    for col in df.columns:
        s = df[col]
        blank = _blank(s)
        non_blank = s[~blank]
        missing = int(blank.sum())
        kind = _infer_kind(s, non_blank)
        unique_count = int(non_blank.nunique())
        applied = []

        if rows and 0 < missing / rows <= MAX_MISSING_RATE_AS_ERROR:
            rules.append({"name": f"{col}: missing", "column": col, "check": "not_null", "severity": "warning"})
            applied.append("missing")

        name = str(col).lower()
        is_key_name = name == "id" or name.endswith("_id")
        if is_key_name and len(non_blank) and unique_count / len(non_blank) >= MIN_UNIQUE_RATE_FOR_KEY \
                and unique_count < len(non_blank):
            rules.append({"name": f"{col}: duplicate", "column": col, "check": "unique", "severity": "warning"})
            applied.append("duplicate")

        if kind == "numeric" and not pd.api.types.is_numeric_dtype(s):
            rules.append({"name": f"{col}: not numeric", "column": col, "check": "optional_numeric", "severity": "warning"})
            applied.append("not numeric")
        elif kind == "date":
            rules.append({"name": f"{col}: invalid date", "column": col, "check": "optional_date", "severity": "warning"})
            applied.append("invalid date")

        profile.append({
            "column": col,
            "inferred_type": kind,
            "missing": missing,
            "missing_pct": round(100 * missing / rows, 1) if rows else 0.0,
            "unique_values": unique_count,
            "rules_applied": ", ".join(applied),
        })

    rules.append({"name": "duplicate_row", "column": "*", "check": "duplicate_row", "severity": "warning"})

    config = {
        "dataset": "generic",
        "required_columns": [],
        "rules": rules,
        "thresholds": thresholds or {"max_critical_failures": 0, "max_warning_failures": 10},
    }
    return config, pd.DataFrame(profile)


DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config" / "rules.yaml"


def load_config(path=None):
    if path is None:
        config_path = DEFAULT_CONFIG
    else:
        config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_checks(df: pd.DataFrame, config: dict) -> tuple[set[str], pd.DataFrame]:
    missing = set(config["required_columns"]) - set(df.columns)
    if missing:
        return missing, pd.DataFrame(columns=["csv_row", "rule", "column", "severity"])

    records = []
    for rule in config["rules"]:
        if rule["check"] == "duplicate_row":
            failed = df.duplicated(keep=False)
        else:
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
