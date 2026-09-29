import sqlite3
from datetime import datetime, timezone
import pandas as pd


DDL = """
CREATE TABLE IF NOT EXISTS runs (
    run_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at       TEXT NOT NULL,
    file_name    TEXT NOT NULL,
    file_hash    TEXT,
    dataset      TEXT NOT NULL DEFAULT 'orders',
    rows_checked INTEGER NOT NULL,
    rows_failed  INTEGER NOT NULL,
    pass_rate    REAL NOT NULL,
    status       TEXT NOT NULL DEFAULT 'UNKNOWN'
);
CREATE TABLE IF NOT EXISTS rule_results (
    run_id       INTEGER NOT NULL,
    rule         TEXT NOT NULL,
    severity     TEXT NOT NULL,
    failed_count INTEGER NOT NULL,
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);
"""


def connect(path="dq_history.db"):
    conn = sqlite3.connect(path)
    conn.executescript(DDL)
    return conn


def save_run(conn, file_name, rows_checked, failures, file_hash=None, status="UNKNOWN"):
    rows_failed = failures["csv_row"].nunique() if not failures.empty else 0
    pass_rate = 1 - (rows_failed / rows_checked) if rows_checked else 1.0

    cur = conn.execute(
        "INSERT INTO runs (run_at, file_name, file_hash, dataset, rows_checked, rows_failed, pass_rate, status)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), file_name, file_hash, "orders",
         rows_checked, rows_failed, pass_rate, status),
    )
    run_id = cur.lastrowid

    if not failures.empty:
        counts = failures.groupby(["rule", "severity"]).size()
        conn.executemany(
            "INSERT INTO rule_results VALUES (?, ?, ?, ?)",
            [(run_id, r, s, int(c)) for (r, s), c in counts.items()],
        )
    conn.commit()
    return run_id


def history(conn, limit=50):
    return pd.read_sql_query(
        "SELECT run_at, file_name, dataset, rows_checked, rows_failed, pass_rate, status"
        " FROM runs ORDER BY run_id DESC LIMIT ?",
        conn,
        params=(limit,)
    )


def rule_trend(conn, rule_name, limit=50):
    return pd.read_sql_query(
        "SELECT r.run_at, rr.failed_count FROM runs r"
        " JOIN rule_results rr ON r.run_id = rr.run_id"
        " WHERE rr.rule = ? ORDER BY r.run_id DESC LIMIT ?",
        conn,
        params=(rule_name, limit)
    )
