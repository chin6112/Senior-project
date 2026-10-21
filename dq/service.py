import pandas as pd
from pathlib import Path
from dq.engine import run_checks, load_config, infer_config
from dq.store import connect, save_run


class ValidationService:
    """Orchestrates validation: read → check → decide → persist"""

    def __init__(self, config_path=None):
        self.config = load_config(config_path)
        self.db = connect()

    def process_file(self, file_bytes: bytes, file_name: str) -> dict:
        """Single entry point for file validation"""
        import hashlib
        import io

        file_hash = hashlib.sha256(file_bytes).hexdigest()

        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except Exception as exc:
            return {
                "success": False,
                "error": f"Cannot read CSV: {exc}",
                "data": None,
            }

        config, dataset, profile = self.config, "orders", None
        if set(config["required_columns"]) - set(df.columns):
            config, profile = infer_config(df, self.config.get("thresholds"))
            dataset = "generic"

        missing_cols, failures = run_checks(df, config)
        if missing_cols:
            return {
                "success": False,
                "error": f"Missing required columns: {', '.join(sorted(missing_cols))}",
                "data": None,
            }

        from dq.policy import PolicyEvaluator

        policy = PolicyEvaluator(config)
        status = policy.evaluate(failures)

        run_id = save_run(self.db, file_name, len(df), failures, file_hash, status, dataset)

        return {
            "success": True,
            "error": None,
            "data": {
                "run_id": run_id,
                "rows_checked": len(df),
                "rows_failed": failures["csv_row"].nunique() if not failures.empty else 0,
                "critical_count": len(failures[failures["severity"] == "critical"]),
                "status": status,
                "dataset": dataset,
                "profile": profile,
                "failures": failures,
                "file_hash": file_hash,
            },
        }

    def close(self):
        self.db.close()
