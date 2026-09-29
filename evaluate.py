import pandas as pd
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dq.engine import run_checks, load_config

CONFIG = load_config()
LABELED_DATA = Path(__file__).parent / "data" / "labeled" / "orders_labeled.csv"

def evaluate():
    df = pd.read_csv(LABELED_DATA)

    _, detected_failures = run_checks(df, CONFIG)

    detected_by_row = {}
    for _, row in detected_failures.iterrows():
        csv_row = int(row["csv_row"])
        if csv_row not in detected_by_row:
            detected_by_row[csv_row] = set()
        detected_by_row[csv_row].add(row["rule"])

    df["detected_rules"] = df.index.map(lambda i: detected_by_row.get(i + 2, set()))
    df["expected_set"] = df["expected_rules"].map(lambda x: set(x.split("|")) if x != "clean" else set())

    metrics_by_rule = {}
    for rule_name in CONFIG["rules"]:
        name = rule_name["name"]
        expected_set = set()
        detected_set = set()

        for i, row in df.iterrows():
            csv_row = i + 2
            if name in row["expected_set"]:
                expected_set.add(csv_row)
            if name in row["detected_rules"]:
                detected_set.add(csv_row)

        tp = len(expected_set & detected_set)
        fp = len(detected_set - expected_set)
        fn = len(expected_set - detected_set)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        metrics_by_rule[name] = {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        }

    results_df = pd.DataFrame(metrics_by_rule).T
    results_df = results_df.round(3)

    print("\n" + "=" * 80)
    print("DATA QUALITY VALIDATION EVALUATION")
    print("=" * 80)
    print(f"Test dataset: {LABELED_DATA}")
    print(f"Total rows: {len(df)}")
    print(f"Rows with issues: {len(df[df['expected_rules'] != 'clean'])}")
    print(f"Clean rows: {len(df[df['expected_rules'] == 'clean'])}")
    print("\n" + "=" * 80)
    print("PER-RULE METRICS")
    print("=" * 80)
    print(results_df.to_string())
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Macro-average Precision: {results_df['precision'].mean():.3f}")
    print(f"Macro-average Recall:    {results_df['recall'].mean():.3f}")
    print(f"Macro-average F1-Score:  {results_df['f1_score'].mean():.3f}")
    print("=" * 80 + "\n")

    results_df.to_csv(Path(__file__).parent.parent / "evaluation_results.csv")
    print(f"Results saved to evaluation_results.csv")

    return results_df

if __name__ == "__main__":
    evaluate()
