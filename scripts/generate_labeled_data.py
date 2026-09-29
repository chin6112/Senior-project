import pandas as pd
import random
from datetime import datetime, timedelta
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dq.engine import load_config

random.seed(42)
CONFIG = load_config()

def generate_order_id(idx, issues=None):
    if issues and "missing_id" in issues:
        return ""
    if issues and "duplicate_id" in issues:
        return "ORD-DUP-001"
    return f"ORD-{1000 + idx}"

def generate_date(idx, issues=None):
    if issues and "invalid_date" in issues:
        return "invalid-date"
    base = datetime(2026, 1, 1)
    return (base + timedelta(days=idx)).strftime("%Y-%m-%d")

def generate_amount(idx, issues=None):
    if issues and "invalid_amount" in issues:
        return "-10.50" if idx % 2 == 0 else ""
    return str(10.0 + idx * 0.5)

rows = []

for i in range(1, 201):
    issues = set()

    if i % 50 == 0:
        issues.add("missing_id")
    if i % 60 == 0:
        issues.add("duplicate_id")
    if i % 55 == 0:
        issues.add("invalid_date")
    if i % 45 == 0:
        issues.add("invalid_amount")

    rows.append({
        "order_id": generate_order_id(i, issues),
        "order_date": generate_date(i, issues),
        "amount": generate_amount(i, issues),
        "expected_rules": "|".join(sorted(issues)) if issues else "clean",
    })

df = pd.DataFrame(rows)
output_path = project_root / "data" / "labeled" / "orders_labeled.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False)

print(f"Generated {len(df)} labeled orders")
print(f"Saved to {output_path}")
print(f"\nIssue distribution:")
print(df["expected_rules"].value_counts().head(10))
