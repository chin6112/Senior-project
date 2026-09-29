class PolicyEvaluator:
    """Decide PASS / WARN / FAIL based on thresholds"""

    def __init__(self, config: dict):
        self.thresholds = config.get("thresholds", {
            "min_pass_rate": 0.95,
            "max_critical_failures": 0,
            "max_warning_failures": 10,
        })

    def evaluate(self, failures) -> str:
        """
        Returns:
            'PASS': All thresholds met
            'WARN': Some issues but within tolerance
            'FAIL': Critical issues exceed threshold
        """
        if failures.empty:
            return "PASS"

        critical_count = len(failures[failures["severity"] == "critical"])
        warning_count = len(failures[failures["severity"] == "warning"])

        if critical_count > self.thresholds.get("max_critical_failures", 0):
            return "FAIL"

        if warning_count > self.thresholds.get("max_warning_failures", 10):
            return "WARN"

        return "PASS"

    def get_reason(self, failures) -> str:
        """Human-readable explanation of status"""
        if failures.empty:
            return "All rows passed validation checks"

        critical = len(failures[failures["severity"] == "critical"])
        warning = len(failures[failures["severity"] == "warning"])

        reasons = []
        if critical > 0:
            reasons.append(f"{critical} critical failure(s)")
        if warning > 0:
            reasons.append(f"{warning} warning(s)")

        return " + ".join(reasons)
