import pandas as pd
import streamlit as st
from dq.service import ValidationService
from dq.store import connect, history


RULE_LABELS = {
    "missing_id": "Missing order_id",
    "duplicate_id": "Duplicate order_id",
    "invalid_date": "Invalid order_date",
    "invalid_amount": "Missing, invalid, or negative amount",
}

STATUS_COLORS = {
    "PASS": "🟢",
    "WARN": "🟡",
    "FAIL": "🔴",
}


st.set_page_config(
    page_title="Order CSV Quality Monitor",
    page_icon=":bar_chart:",
    layout="wide"
)
st.title("Order CSV Quality Monitor")

tab1, tab2, tab3 = st.tabs(["Validate", "History", "Evaluation"])

with tab1:
    st.write("Upload an orders CSV to find missing, duplicate, or invalid values.")

    uploaded_file = st.file_uploader("Upload orders.csv", type="csv")
    if uploaded_file is None:
        st.info("Choose a CSV with order_id, order_date, and amount columns to begin.")
    else:
        service = ValidationService()
        result = service.process_file(uploaded_file.getvalue(), uploaded_file.name)
        service.close()

        if not result["success"]:
            st.error(result["error"])
        else:
            data = result["data"]
            status = data["status"]
            failures = data["failures"]

            st.subheader(f"{STATUS_COLORS.get(status, '❓')} Status: {status}")

            first, second, third = st.columns(3)
            first.metric("Rows checked", data["rows_checked"])
            second.metric("Rows with issues", data["rows_failed"])
            third.metric("Critical failures", data["critical_count"])

            if failures.empty:
                st.success("All rows passed the checks.")
            else:
                if status == "FAIL":
                    st.error("❌ File contains critical issues. Review and fix before processing.")
                elif status == "WARN":
                    st.warning("⚠️ File has issues. Review the details below.")

                st.subheader("Failures by rule")
                rule_counts = failures.groupby("rule").size().sort_values(ascending=False)
                st.bar_chart(rule_counts)

                st.subheader("Rows to review")
                display_failures = failures.copy()
                display_failures["rule"] = display_failures["rule"].map(RULE_LABELS)
                st.dataframe(
                    display_failures.sort_values(["csv_row", "rule"]),
                    hide_index=True,
                    use_container_width=True
                )

                st.download_button(
                    "Download failure report",
                    data=failures.to_csv(index=False).encode("utf-8"),
                    file_name="order_quality_failures.csv",
                    mime="text/csv",
                )

            st.caption("CSV row numbers count the header as row 1; quoted multiline records may shift physical line numbers.")

with tab2:
    st.subheader("Monitoring History")
    db = connect()
    hist = history(db)
    db.close()

    if hist.empty:
        st.info("No validation runs yet. Upload a CSV in the Validate tab to start tracking history.")
    else:
        st.write(f"Total runs: {len(hist)}")

        col1, col2 = st.columns(2)
        with col1:
            latest = hist.iloc[0]
            st.metric(
                "Latest pass rate",
                f"{latest['pass_rate']:.1%}",
                f"{int(latest['rows_failed'])} rows with issues"
            )
        with col2:
            avg_pass_rate = hist["pass_rate"].mean()
            st.metric("Average pass rate", f"{avg_pass_rate:.1%}")

        hist_display = hist.copy()
        hist_display["run_at"] = pd.to_datetime(hist_display["run_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        hist_display["pass_rate"] = hist_display["pass_rate"].apply(lambda x: f"{x:.1%}")
        st.subheader("Run history")
        st.dataframe(hist_display, hide_index=True, use_container_width=True)

        st.subheader("Pass rate trend")
        hist_trend = hist.copy()
        hist_trend["run_at"] = pd.to_datetime(hist_trend["run_at"])
        hist_trend = hist_trend.sort_values("run_at")
        st.line_chart(
            hist_trend.set_index("run_at")[["pass_rate"]],
            use_container_width=True,
            height=400
        )

with tab3:
    st.subheader("Rule Evaluation Metrics")
    st.write("""
    These metrics measure how accurately our validation rules detect data quality issues
    against a labeled test dataset with 200 known orders.
    """)

    try:
        from evaluate import get_evaluation_summary
        summary = get_evaluation_summary()

        if summary:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Macro Precision",
                    f"{summary['macro_precision']:.1%}",
                    help="Average % of detected issues that are actually issues"
                )
            with col2:
                st.metric(
                    "Macro Recall",
                    f"{summary['macro_recall']:.1%}",
                    help="Average % of real issues that we successfully detect"
                )
            with col3:
                st.metric(
                    "Macro F1-Score",
                    f"{summary['macro_f1']:.1%}",
                    help="Harmonic mean of precision and recall"
                )

            st.subheader("Per-Rule Breakdown")
            results_df = summary["results"][["expected", "detected", "tp", "fp", "fn", "precision", "recall", "f1"]]
            st.dataframe(results_df.round(3), use_container_width=True)

            st.subheader("Interpretation")
            if summary["macro_f1"] > 0.8:
                st.success("✅ Validation rules are highly accurate")
            elif summary["macro_f1"] > 0.6:
                st.warning("⚠️ Validation rules are reasonably accurate but have room for improvement")
            else:
                st.error("❌ Validation rules need refinement")

            st.write("""
            **Precision**: Of all issues we flag, how many are real?
            - High precision = few false alarms
            - Low precision = we're catching noise

            **Recall**: Of all real issues, how many do we catch?
            - High recall = we find most problems
            - Low recall = we miss some problems

            **F1-Score**: Balance between precision and recall
            """)
        else:
            st.info("Run evaluate.py to generate metrics:")
            st.code("python evaluate.py")

    except ImportError:
        st.error("Evaluation module not available. Please ensure evaluate.py is in the project root.")
