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

def generate_realistic_dataset(n_rows=200):
    """Generate realistic labeled test data with diverse error patterns"""
    rows = []

    base_date = datetime(2026, 1, 1)

    for i in range(1, n_rows + 1):
        issues = set()

        # Pattern 1: Every 50th row missing ID (data entry skip)
        if i % 50 == 0:
            issues.add("missing_id")

        # Pattern 2: Exact duplicates (data loading glitch)
        if i % 60 == 0 and i > 60:
            issues.add("duplicate_id")

        # Pattern 3: Invalid dates (user typos, format mismatch)
        if i % 55 == 0:
            bad_dates = ["2026-13-01", "invalid", "2026/01/01", "01-01-2026", ""]
            order_date = bad_dates[random.randint(0, 4)]
            issues.add("invalid_date")
        else:
            order_date = (base_date + timedelta(days=i % 30)).strftime("%Y-%m-%d")

        # Pattern 4: Invalid amounts (negative, typos, missing)
        if i % 45 == 0:
            bad_amounts = ["-50.00", "-1.5", "", "abc", "999999.99"]
            amount = bad_amounts[random.randint(0, 4)]
            if amount not in ["", "abc"]:
                issues.add("invalid_amount")
            else:
                issues.add("invalid_amount")
        else:
            amount = f"{random.uniform(5, 500):.2f}"

        # Pattern 5: Realistic data with spaces/typos in ID
        if i % 70 == 0:
            order_id = f"  ORD-{1000+i}  "
            issues.add("missing_id")
        elif i % 75 == 0:
            order_id = f"ORD-{1000 + (i-1)}"
            issues.add("duplicate_id")
        else:
            order_id = f"ORD-{1000 + i}" if not issues else order_date

        rows.append({
            "order_id": order_id,
            "order_date": order_date,
            "amount": amount,
            "expected_rules": "|".join(sorted(issues)) if issues else "clean",
        })

    return pd.DataFrame(rows)

df = generate_realistic_dataset(200)
output_path = project_root / "data" / "labeled" / "orders_labeled.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False)

print(f"Generated {len(df)} realistic labeled orders")
print(f"Saved to {output_path}")
print(f"\nIssue distribution:")
print(df["expected_rules"].value_counts().head(12))
print(f"\nTotal rows with issues: {len(df[df['expected_rules'] != 'clean'])}")
print(f"Clean rows: {len(df[df['expected_rules'] == 'clean'])}")
