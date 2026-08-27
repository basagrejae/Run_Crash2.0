import streamlit as st
import pandas as pd
import sqlite3

DB = "cash_posting.db"

conn = sqlite3.connect(DB)

# Create tables
conn.execute("""
CREATE TABLE IF NOT EXISTS detail_table(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pas_system TEXT,
    deposit_date TEXT,
    entry_type TEXT,
    amount REAL,
    batch_number TEXT,
    note TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS batch_table(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_name TEXT,
    net_payments REAL,
    net_ups REAL,
    totals REAL
)
""")

conn.commit()


def import_detail(file):
    df = pd.read_excel(file)

    data = df[[
        'PAS System',
        'Date of Deposit',
        'Type of Entry',
        'Amount',
        'Batch Number',
        'Note'
    ]]

    data.columns = [
        'pas_system',
        'deposit_date',
        'entry_type',
        'amount',
        'batch_number',
        'note'
    ]

    data.to_sql(
        'detail_table',
        conn,
        if_exists='append',
        index=False
    )

    print("Detail records imported")


def import_batch(file):
    df = pd.read_excel(file)

    data = pd.DataFrame({
        'batch_name': df['Batch'],
        'net_payments': df['Net Payments'],
        'net_ups': df['Net UPs'],
        'totals': df['Totals']
    })

    data.to_sql(
        'batch_table',
        conn,
        if_exists='append',
        index=False
    )

    print("Batch records imported")


def balance():
    detail_total = pd.read_sql("""
        SELECT SUM(amount) AS total
        FROM detail_table
    """, conn)

    batch_total = pd.read_sql("""
        SELECT SUM(totals) AS total
        FROM batch_table
    """, conn)

    detail_sum = float(detail_total.iloc[0,0] or 0)
    batch_sum = float(batch_total.iloc[0,0] or 0)

    variance = detail_sum - batch_sum

    print("=" * 50)
    print(f"Detail Amount Total : ${detail_sum:,.2f}")
    print(f"Batch Total         : ${batch_sum:,.2f}")
    print(f"Variance            : ${variance:,.2f}")

    if variance == 0:
        print("STATUS : BALANCED")
    elif variance > 0:
        print("STATUS : OVER POSTED")
    else:
        print("STATUS : UNDER POSTED")

    return variance


if __name__ == "__main__":
    import_detail("detail_table.xlsx")
    import_batch("batch_table.xlsx")
    balance()

st.title("Cash Posting & Balancing")

detail_file = st.file_uploader(
    "Upload Detail Table",
    type=["xlsx"]
)

batch_file = st.file_uploader(
    "Upload Batch Table",
    type=["xlsx"]
)

if detail_file and batch_file:

    detail_df = pd.read_excel(detail_file)
    batch_df = pd.read_excel(batch_file)

    detail_total = detail_df["Amount"].sum()
    batch_total = batch_df["Totals"].sum()

    variance = detail_total - batch_total

    st.metric("Detail Total", f"${detail_total:,.2f}")
    st.metric("Batch Total", f"${batch_total:,.2f}")
    st.metric("Variance", f"${variance:,.2f}")

    if variance == 0:
        st.success("BALANCED")
    else:
        st.error("OUT OF BALANCE")

    report = pd.DataFrame({
        "Detail Total":[detail_total],
        "Batch Total":[batch_total],
        "Variance":[variance]
    })

    st.dataframe(report)