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
    for rule_config in CONFIG["rules"]:
        name = rule_config["name"]
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

        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0 if tp == 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0 if tp == 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        metrics_by_rule[name] = {
            "expected": len(expected_set),
            "detected": len(detected_set),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    results_df = pd.DataFrame(metrics_by_rule).T.round(3)

    print("\n" + "=" * 100)
    print("DATA QUALITY VALIDATION EVALUATION REPORT".center(100))
    print("=" * 100)
    print(f"Test Dataset: {LABELED_DATA.name}")
    print(f"Total Rows: {len(df)} | Rows with Issues: {len(df[df['expected_rules'] != 'clean'])} | Clean Rows: {len(df[df['expected_rules'] == 'clean'])}")
    print("\n" + "=" * 100)
    print("PER-RULE METRICS")
    print("=" * 100)

    display_cols = ["expected", "detected", "tp", "fp", "fn", "precision", "recall", "f1"]
    print(results_df[display_cols].to_string())

    print("\n" + "=" * 100)
    print("SUMMARY STATISTICS")
    print("=" * 100)
    print(f"Macro-average Precision:  {results_df['precision'].mean():.3f}")
    print(f"Macro-average Recall:     {results_df['recall'].mean():.3f}")
    print(f"Macro-average F1-Score:   {results_df['f1'].mean():.3f}")
    print("=" * 100)

    results_df.to_csv(Path(__file__).parent / "evaluation_results.csv")
    print(f"\nResults saved to: evaluation_results.csv\n")

    return results_df


def get_evaluation_summary():
    """Return dict for Streamlit display. Compute on-the-fly if results file doesn't exist."""
    results_path = Path(__file__).parent / "evaluation_results.csv"
    try:
        results = pd.read_csv(results_path, index_col=0)
    except FileNotFoundError:
        # Compute evaluation on-the-fly for Streamlit Cloud deployment
        results = evaluate()

    return {
        "macro_precision": results["precision"].mean(),
        "macro_recall": results["recall"].mean(),
        "macro_f1": results["f1"].mean(),
        "results": results,
    }


if __name__ == "__main__":
    evaluate()
