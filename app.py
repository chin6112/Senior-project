import pandas as pd
import streamlit as st
import io
import hashlib
from pathlib import Path
from dq.engine import run_checks, load_config
from dq.store import connect, save_run, history


RULE_LABELS = {
    "missing_id": "Missing order_id",
    "duplicate_id": "Duplicate order_id",
    "invalid_date": "Invalid order_date",
    "invalid_amount": "Missing, invalid, or negative amount",
}


st.set_page_config(
    page_title="Order CSV Quality Monitor",
    page_icon=":bar_chart:",
    layout="wide"
)
st.title("Order CSV Quality Monitor")

tab1, tab2 = st.tabs(["Validate", "History"])

with tab1:
    st.write("Upload an orders CSV to find missing, duplicate, or invalid values.")

    uploaded_file = st.file_uploader("Upload orders.csv", type="csv")
    if uploaded_file is None:
        st.info("Choose a CSV with order_id, order_date, and amount columns to begin.")
    else:
        try:
            raw_data = uploaded_file.getvalue()
            file_hash = hashlib.sha256(raw_data).hexdigest()
            orders = pd.read_csv(io.BytesIO(raw_data))
        except Exception as exc:
            st.error(f"Cannot read CSV: {exc}")
            orders = None

        if orders is not None:
            config = load_config()
            missing_columns, failures = run_checks(orders, config)

            if missing_columns:
                st.error(f"Missing required columns: {', '.join(sorted(missing_columns))}")
            else:
                rows_with_issues = int(failures["csv_row"].nunique())
                total_issues = len(failures)
                critical_issues = len(failures[failures["severity"] == "critical"])

                first, second, third = st.columns(3)
                first.metric("Rows checked", len(orders))
                second.metric("Rows with issues", rows_with_issues)
                third.metric("Critical failures", critical_issues)

                if "last_saved" not in st.session_state:
                    st.session_state["last_saved"] = None

                if st.session_state.get("last_saved") != file_hash:
                    db = connect()
                    save_run(db, uploaded_file.name, len(orders), failures)
                    db.close()
                    st.session_state["last_saved"] = file_hash

                if failures.empty:
                    st.success("All rows passed the checks.")
                else:
                    if critical_issues > 0:
                        st.warning(f"⚠️ {critical_issues} critical issue(s) found. Review before proceeding.")

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
            st.metric(
                "Latest pass rate",
                f"{hist.iloc[0]['pass_rate']:.1%}",
                f"{hist.iloc[0]['rows_failed']} rows with issues"
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