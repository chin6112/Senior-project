"""Generate challenging test cases that reveal rule boundaries.

These cases are VALID according to rule definitions but represent
business/domain edge cases that more sophisticated validation might catch.
"""

import pandas as pd
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dq.engine import load_config

CONFIG = load_config()

def generate_hard_cases():
    """Generate 30 edge cases: technically valid but business-questionable"""
    rows = []

    cases = [
        # === Amount edge cases (rule: amount >= 0, but business logic might object) ===
        ("ORD-2001", "2026-01-01", "0.00", ""),           # Zero order (technically valid, unusual)
        ("ORD-2002", "2026-01-01", "0.01", ""),           # Penny order (valid, but suspiciously small)
        ("ORD-2003", "2026-01-01", "999999.99", ""),      # Huge outlier (valid numeric)
        ("ORD-2004", "2026-01-01", "1000000.00", ""),     # Million order (valid but extreme)
        ("ORD-2005", "2026-01-01", "1.5", ""),            # Odd decimal (valid, rule doesn't enforce .00)
        ("ORD-2006", "2026-01-01", "0.001", ""),          # Sub-cent (valid numeric)

        # === Date edge cases (rule: ISO 8601 format, but business context matters) ===
        ("ORD-2007", "2020-01-01", "100.00", ""),         # Old order from 2020 (past, valid format)
        ("ORD-2008", "2030-12-31", "100.00", ""),         # Future order (far future, valid format)
        ("ORD-2009", "2026-01-01", "100.00", ""),         # Date from very beginning of dataset (valid)
        ("ORD-2010", "2026-12-31", "100.00", ""),         # End of year date (valid)
        ("ORD-2011", "2026-02-28", "100.00", ""),         # End of February (valid, not leap year)
        ("ORD-2012", "2026-06-15", "100.00", ""),         # Mid-year (valid)

        # === Order ID edge cases (rule: not empty, checked for exact duplicates) ===
        ("ORD-0001", "2026-01-01", "100.00", ""),         # Leading zeros (valid, unique ID)
        ("ORD-99999", "2026-01-01", "100.00", ""),        # High number (valid, unique)
        ("X", "2026-01-01", "100.00", ""),                # Single character (valid, unique)
        ("ORD-2013-A", "2026-01-01", "100.00", ""),       # With letter (valid, unique)
        ("ORD 2014", "2026-01-01", "100.00", ""),         # Space instead of dash (valid format differs)
        ("ORD_2015", "2026-01-01", "100.00", ""),         # Underscore (valid, different format)

        # === Combined edge cases ===
        ("ORD-2016", "2026-01-01", "1.111", ""),          # Valid but many decimals
        ("ORD-2017", "2026-01-01", "100.10", ""),         # Unusual decimal (not round)
        ("ORD-2018", "2026-01-01", "50", ""),             # No decimal places (valid numeric)
        ("ORD-2019", "2026-01-01", "49.99", ""),          # Almost 50 (specific amount)
        ("ORD-2020", "2026-01-01", "100.00", ""),         # Standard clean case

        # === Cases that look wrong but pass our rules ===
        ("ORD-2021", "2026-01-01", "100.00", ""),         # Exact duplicate ID test (won't catch self)
        ("", "", "", "missing_id"),                       # All empty (catches missing_id)
        ("ORD-2022", "2026-01-01", "100.00", ""),         # Good data
        ("ORD-2023", "2026-01-01", "100.00", ""),         # Good data
        ("ORD-2024", "2026-01-01", "100.00", ""),         # Good data
        ("ORD-2025", "2026-01-01", "100.00", ""),         # Good data
    ]

    for order_id, order_date, amount, expected in cases:
        rows.append({
            "order_id": order_id,
            "order_date": order_date,
            "amount": amount,
            "expected_rules": expected if expected else "clean",
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_hard_cases()
    output_path = project_root / "data" / "labeled" / "orders_hard.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} hard test cases")
    print(f"Saved to {output_path}")
    print(f"\nIssue distribution:")
    print(df["expected_rules"].value_counts())
    print(f"\nDesign principles for these hard cases:")
    print("- All cases are VALID by current rule definitions")
    print("- But represent business edge cases or boundaries")
    print("- Examples of what more sophisticated validation could catch:")
    print("  * Zero or penny amounts (business: cost threshold)")
    print("  * Huge outliers like 999999.99 (business: anomaly detection)")
    print("  * Very old or very future dates (business: realistic time window)")
    print("  * Unusual formats like ORD 2014 vs ORD-2014 (business: consistency)")
    print("\nThese show what future enhancements could add.")

