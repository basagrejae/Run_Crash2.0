
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime
from pathlib import Path

DB = Path("cash_posting.db")

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS batches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_date TEXT NOT NULL,
        batch_number TEXT NOT NULL UNIQUE,
        payer TEXT,
        payment_method TEXT,
        deposit_amount REAL NOT NULL DEFAULT 0,
        posted_amount REAL NOT NULL DEFAULT 0,
        adjustment_amount REAL NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'Open',
        notes TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id INTEGER NOT NULL,
        check_number TEXT,
        patient_account TEXT,
        patient_name TEXT,
        claim_number TEXT,
        payer TEXT,
        payment_amount REAL NOT NULL DEFAULT 0,
        adjustment_amount REAL NOT NULL DEFAULT 0,
        posted_amount REAL NOT NULL DEFAULT 0,
        payment_date TEXT,
        notes TEXT,
        FOREIGN KEY(batch_id) REFERENCES batches(id)
    );
    """)
    conn.commit()
    conn.close()

def refresh_batch(batch_id):
    conn = db()
    row = conn.execute("""
        SELECT
            COALESCE(SUM(payment_amount),0) AS payment_total,
            COALESCE(SUM(adjustment_amount),0) AS adjustment_total,
            COALESCE(SUM(posted_amount),0) AS posted_total
        FROM payments WHERE batch_id=?
    """, (batch_id,)).fetchone()

    batch = conn.execute("SELECT deposit_amount FROM batches WHERE id=?", (batch_id,)).fetchone()
    variance = float(batch["deposit_amount"]) - float(row["payment_total"])
    status = "Balanced" if abs(variance) < 0.005 else "Open"

    conn.execute("""
        UPDATE batches
        SET posted_amount=?, adjustment_amount=?, status=?
        WHERE id=?
    """, (row["posted_total"], row["adjustment_total"], status, batch_id))
    conn.commit()
    conn.close()

def money(x):
    return f"${float(x or 0):,.2f}"

init_db()

st.set_page_config(page_title="Cash Posting & Balancing", page_icon="💵", layout="wide")
st.title("💵 Pogi ni Lord may Cash Posting & Balancing app")
st.caption("Simple cash posting, batch balancing, payment tracking, and reconciliation app")

menu = st.sidebar.radio("Navigation", [
    "Dashboard", "Create Batch", "Post Payments", "Balance Batch",
    "Batch History", "Export"
])

if menu == "Dashboard":
    conn = db()
    batches = pd.read_sql_query("SELECT * FROM batches ORDER BY id DESC", conn)
    payments = pd.read_sql_query("SELECT * FROM payments ORDER BY id DESC", conn)
    conn.close()

    total_deposits = batches["deposit_amount"].sum() if not batches.empty else 0
    total_posted = batches["posted_amount"].sum() if not batches.empty else 0
    total_adjustments = batches["adjustment_amount"].sum() if not batches.empty else 0
    open_batches = int((batches["status"] == "Open").sum()) if not batches.empty else 0
    balanced_batches = int((batches["status"] == "Balanced").sum()) if not batches.empty else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Deposits", money(total_deposits))
    c2.metric("Total Posted", money(total_posted))
    c3.metric("Adjustments", money(total_adjustments))
    c4.metric("Open Batches", open_batches)

    st.subheader("Recent Batches")
    if batches.empty:
        st.info("No batches created yet.")
    else:
        show = batches[[
            "batch_date","batch_number","payer","payment_method",
            "deposit_amount","posted_amount","adjustment_amount","status"
        ]].copy()
        for col in ["deposit_amount","posted_amount","adjustment_amount"]:
            show[col] = show[col].map(money)
        st.dataframe(show, use_container_width=True, hide_index=True)

elif menu == "Create Batch":
    st.header("Create Payment Batch")
    with st.form("create_batch"):
        c1,c2 = st.columns(2)
        batch_date = c1.date_input("Batch Date", date.today())
        batch_number = c2.text_input("Batch Number", placeholder="e.g. BATCH-2026-001")
        c3,c4 = st.columns(2)
        payer = c3.text_input("Payer")
        method = c4.selectbox("Payment Method", ["EFT/ERA", "Check", "Cash", "Credit Card", "Other"])
        deposit = st.number_input("Deposit Amount", min_value=0.0, step=0.01, format="%.2f")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Create Batch", type="primary")

    if submitted:
        if not batch_number.strip():
            st.error("Batch number is required.")
        else:
            try:
                conn = db()
                conn.execute("""
                    INSERT INTO batches
                    (batch_date,batch_number,payer,payment_method,deposit_amount,notes,created_at)
                    VALUES (?,?,?,?,?,?,?)
                """, (str(batch_date), batch_number.strip(), payer, method, deposit, notes,
                      datetime.now().isoformat(timespec="seconds")))
                conn.commit()
                conn.close()
                st.success(f"Batch {batch_number} created.")
            except sqlite3.IntegrityError:
                st.error("That batch number already exists.")

elif menu == "Post Payments":
    st.header("Post Payments")
    conn = db()
    batches = pd.read_sql_query(
        "SELECT id,batch_number,batch_date,payer,deposit_amount,status FROM batches ORDER BY id DESC",
        conn
    )
    conn.close()

    if batches.empty:
        st.warning("Create a batch first.")
    else:
        labels = {
            int(r.id): f"{r.batch_number} | {r.payer or 'Unknown payer'} | Deposit {money(r.deposit_amount)} | {r.status}"
            for r in batches.itertuples()
        }
        batch_id = st.selectbox("Select Batch", list(labels.keys()), format_func=lambda x: labels[x])

        st.subheader("Add Payment")
        with st.form("payment_form"):
            c1,c2,c3 = st.columns(3)
            check = c1.text_input("Check / EFT Number")
            acct = c2.text_input("Patient Account #")
            claim = c3.text_input("Claim Number")
            c4,c5,c6 = st.columns(3)
            patient = c4.text_input("Patient Name")
            payer = c5.text_input("Payer")
            payment = c6.number_input("Payment Amount", min_value=0.0, step=0.01, format="%.2f")
            c7,c8 = st.columns(2)
            adjustment = c7.number_input("Adjustment Amount", min_value=0.0, step=0.01, format="%.2f")
            posted = c8.number_input("Posted Amount", min_value=0.0, step=0.01, format="%.2f")
            pdate = st.date_input("Payment Date", date.today())
            notes = st.text_area("Payment Notes")
            add = st.form_submit_button("Post Payment", type="primary")

        if add:
            conn = db()
            conn.execute("""
                INSERT INTO payments
                (batch_id,check_number,patient_account,patient_name,claim_number,payer,
                 payment_amount,adjustment_amount,posted_amount,payment_date,notes)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (batch_id,check,acct,patient,claim,payer,payment,adjustment,posted,str(pdate),notes))
            conn.commit()
            conn.close()
            refresh_batch(batch_id)
            st.success("Payment posted.")

        conn = db()
        payments = pd.read_sql_query(
            "SELECT * FROM payments WHERE batch_id=? ORDER BY id DESC", conn, params=(batch_id,)
        )
        conn.close()

        st.subheader("Payments in Batch")
        if payments.empty:
            st.info("No payments posted in this batch.")
        else:
            display = payments[[
                "id","check_number","patient_account","patient_name","claim_number",
                "payment_amount","adjustment_amount","posted_amount","payment_date"
            ]].copy()
            for col in ["payment_amount","adjustment_amount","posted_amount"]:
                display[col] = display[col].map(money)
            st.dataframe(display, use_container_width=True, hide_index=True)

elif menu == "Balance Batch":
    st.header("Batch Reconciliation")
    conn = db()
    batches = pd.read_sql_query("SELECT * FROM batches ORDER BY id DESC", conn)
    conn.close()

    if batches.empty:
        st.info("No batches available.")
    else:
        batch_id = st.selectbox(
            "Select Batch",
            batches["id"].tolist(),
            format_func=lambda x: batches.loc[batches.id == x, "batch_number"].iloc[0]
        )
        refresh_batch(int(batch_id))
        conn = db()
        b = conn.execute("SELECT * FROM batches WHERE id=?", (int(batch_id),)).fetchone()
        sums = conn.execute("""
            SELECT
              COALESCE(SUM(payment_amount),0) payment_total,
              COALESCE(SUM(adjustment_amount),0) adjustment_total,
              COALESCE(SUM(posted_amount),0) posted_total,
              COUNT(*) payment_count
            FROM payments WHERE batch_id=?
        """, (int(batch_id),)).fetchone()
        conn.close()

        variance = float(b["deposit_amount"]) - float(sums["payment_total"])
        posted_variance = float(b["deposit_amount"]) - float(sums["posted_total"])

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Deposit", money(b["deposit_amount"]))
        c2.metric("Payment Total", money(sums["payment_total"]))
        c3.metric("Posted Total", money(sums["posted_total"]))
        c4.metric("Variance", money(variance))

        if abs(variance) < 0.005:
            st.success("✅ BATCH BALANCED — deposit matches payment total.")
        else:
            st.error(f"⚠️ BATCH NOT BALANCED — variance: {money(variance)}")

        st.write(f"Payment count: **{sums['payment_count']}**")
        st.write(f"Adjustment total: **{money(sums['adjustment_total'])}**")
        st.write(f"Deposit vs posted variance: **{money(posted_variance)}**")

        if st.button("Mark Batch Closed"):
            if abs(variance) < 0.005:
                conn = db()
                conn.execute("UPDATE batches SET status='Closed' WHERE id=?", (int(batch_id),))
                conn.commit()
                conn.close()
                st.success("Batch closed.")
                st.rerun()
            else:
                st.warning("Balance the batch before closing it.")

elif menu == "Batch History":
    st.header("Batch History")
    conn = db()
    batches = pd.read_sql_query("SELECT * FROM batches ORDER BY id DESC", conn)
    conn.close()

    if batches.empty:
        st.info("No history available.")
    else:
        status = st.multiselect("Filter Status", ["Open","Balanced","Closed"], default=["Open","Balanced","Closed"])
        view = batches[batches["status"].isin(status)].copy()
        for col in ["deposit_amount","posted_amount","adjustment_amount"]:
            view[col] = view[col].map(money)
        st.dataframe(view, use_container_width=True, hide_index=True)

elif menu == "Export":
    st.header("Export Data")
    conn = db()
    batches = pd.read_sql_query("SELECT * FROM batches ORDER BY id", conn)
    payments = pd.read_sql_query("SELECT * FROM payments ORDER BY id", conn)
    conn.close()

    st.download_button(
        "Download Batches CSV",
        batches.to_csv(index=False).encode("utf-8"),
        "batches.csv",
        "text/csv"
    )
    st.download_button(
        "Download Payments CSV",
        payments.to_csv(index=False).encode("utf-8"),
        "payments.csv",
        "text/csv"
    )

    st.subheader("Import Payments CSV")
    st.caption("CSV columns: batch_number, check_number, patient_account, patient_name, claim_number, payer, payment_amount, adjustment_amount, posted_amount, payment_date, notes")
    upload = st.file_uploader("Choose CSV", type=["csv"])
    if upload:
        df = pd.read_csv(upload)
        st.dataframe(df.head(20), use_container_width=True)
        if st.button("Import Payments"):
            required = ["batch_number","payment_amount"]
            missing = [x for x in required if x not in df.columns]
            if missing:
                st.error("Missing required columns: " + ", ".join(missing))
            else:
                conn = db()
                imported = 0
                skipped = 0
                for _, r in df.iterrows():
                    batch = conn.execute(
                        "SELECT id FROM batches WHERE batch_number=?",
                        (str(r["batch_number"]),)
                    ).fetchone()
                    if not batch:
                        skipped += 1
                        continue
                    conn.execute("""
                        INSERT INTO payments
                        (batch_id,check_number,patient_account,patient_name,claim_number,payer,
                         payment_amount,adjustment_amount,posted_amount,payment_date,notes)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        batch["id"], str(r.get("check_number","")),
                        str(r.get("patient_account","")), str(r.get("patient_name","")),
                        str(r.get("claim_number","")), str(r.get("payer","")),
                        float(r.get("payment_amount",0) or 0),
                        float(r.get("adjustment_amount",0) or 0),
                        float(r.get("posted_amount",0) or 0),
                        str(r.get("payment_date","")), str(r.get("notes",""))
                    ))
                    imported += 1
                conn.commit()
                conn.close()
                for bid in batches["id"].tolist():
                    refresh_batch(int(bid))
                st.success(f"Imported {imported} payments. Skipped {skipped} rows with unknown batch numbers.")
