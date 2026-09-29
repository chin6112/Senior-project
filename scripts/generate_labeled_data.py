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
            order_id = ""
        else:
            order_id = f"ORD-{1000 + i}"

        # Pattern 2: Exact duplicates (data loading glitch)
        # Mark with duplicate ID but DON'T add to issues yet
        duplicate_marker = None
        if i % 60 == 0 and i > 60:
            duplicate_marker = f"ORD-{1000 + (i-1)}"
            order_id = duplicate_marker

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
            if amount in ["-50.00", "-1.5", ""]:
                issues.add("invalid_amount")
            else:
                issues.add("invalid_amount")
        else:
            amount = f"{random.uniform(5, 500):.2f}"

        rows.append({
            "order_id": order_id,
            "order_date": order_date,
            "amount": amount,
            "_duplicate_marker": duplicate_marker,
            "expected_rules": "|".join(sorted(issues)) if issues else "clean",
        })

    df = pd.DataFrame(rows)

    # Second pass: Mark ALL rows with duplicate order_ids as duplicate_id
    # (excluding empty/missing IDs)
    seen_ids = {}
    duplicate_ids = set()
    for idx, row in df.iterrows():
        order_id = row["order_id"]
        if order_id and order_id != "":  # Skip empty IDs
            if order_id in seen_ids:
                duplicate_ids.add(order_id)
            else:
                seen_ids[order_id] = idx

    # Mark ALL rows with duplicate IDs as having the duplicate_id issue
    for idx, row in df.iterrows():
        if row["order_id"] in duplicate_ids:
            issues = set(row["expected_rules"].split("|")) if row["expected_rules"] != "clean" else set()
            issues.add("duplicate_id")
            df.at[idx, "expected_rules"] = "|".join(sorted(issues))

    # Remove helper column
    df = df.drop("_duplicate_marker", axis=1)

    return df

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
