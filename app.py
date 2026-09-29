import pandas as pd
import streamlit as st


REQUIRED_COLUMNS = {"order_id", "order_date", "amount"}
RULE_LABELS = {
    "missing_id": "Missing order_id",
    "duplicate_id": "Duplicate order_id",
    "invalid_date": "Invalid order_date",
    "invalid_amount": "Missing, invalid, or negative amount",
}


def validate_orders(df: pd.DataFrame) -> tuple[set[str], pd.DataFrame]:
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        return missing_columns, pd.DataFrame()

    order_ids = df["order_id"].astype("string").str.strip()
    dates = pd.to_datetime(df["order_date"], errors="coerce")
    amounts = pd.to_numeric(df["amount"], errors="coerce")
    checks = pd.DataFrame(
        {
            "missing_id": order_ids.isna() | order_ids.eq(""),
            "duplicate_id": order_ids.duplicated(keep=False)
            & order_ids.notna()
            & order_ids.ne(""),
            "invalid_date": dates.isna(),
            "invalid_amount": amounts.isna() | amounts.lt(0),
        },
        index=df.index,
    ).fillna(False)

    failures = checks.copy()
    failures.insert(0, "csv_row", df.index + 2)
    failures = failures.melt(
        id_vars="csv_row", var_name="rule", value_name="failed"
    )
    failures = failures.loc[failures["failed"]].drop(columns="failed")
    failures["rule"] = failures["rule"].map(RULE_LABELS)
    return set(), failures


st.set_page_config(page_title="Order CSV Quality Monitor", page_icon=":bar_chart:", layout="wide")
st.title("Order CSV Quality Monitor")
st.write("Upload an orders CSV to find missing, duplicate, or invalid values.")

uploaded_file = st.file_uploader("Upload orders.csv", type="csv")
if uploaded_file is None:
    st.info("Choose a CSV with order_id, order_date, and amount columns to begin.")
    st.stop()

try:
    orders = pd.read_csv(uploaded_file)
except Exception as exc:
    st.error(f"Cannot read CSV: {exc}")
    st.stop()

missing_columns, failures = validate_orders(orders)
if missing_columns:
    st.error(f"Missing required columns: {', '.join(sorted(missing_columns))}")
    st.stop()

rows_with_issues = int(failures["csv_row"].nunique())
total_issues = len(failures)
first, second, third = st.columns(3)
first.metric("Rows checked", len(orders))
second.metric("Rows with issues", rows_with_issues)
third.metric("Total rule failures", total_issues)

if failures.empty:
    st.success("All rows passed the checks.")
else:
    st.subheader("Failures by rule")
    st.bar_chart(failures["rule"].value_counts())
    st.subheader("Rows to review")
    st.dataframe(failures.sort_values(["csv_row", "rule"]), hide_index=True)
    st.download_button(
        "Download failure report",
        data=failures.to_csv(index=False).encode("utf-8"),
        file_name="order_quality_failures.csv",
        mime="text/csv",
    )

st.caption("CSV row numbers count the header as row 1; quoted multiline records may shift physical line numbers.")