import sqlite3
import pandas as pd

DB = "cash_posting.db"


def load_detail(file):

    conn = sqlite3.connect(DB)

    df = pd.read_excel(file)

    data = pd.DataFrame({
        'pas_system' : df['PAS System'],
        'deposit_date' : df['Date of Deposit'],
        'entry_type' : df['Type of Entry'],
        'amount' : df['Amount'],
        'batch_number' : df['Batch Number'],
        'note' : df['Note']
    })

    data.to_sql(
        'detail_table',
        conn,
        if_exists='append',
        index=False
    )

    conn.close()


def load_batch(file):

    conn = sqlite3.connect(DB)

    df = pd.read_excel(file)

    data = pd.DataFrame({
        'batch_name':df['Batch'],
        'net_payments':df['Net Payments'],
        'net_ups':df['Net UPs'],
        'totals':df['Totals']
    })

    data.to_sql(
        'batch_table',
        conn,
        if_exists='append',
        index=False
    )

    conn.close()


def reconcile():

    conn = sqlite3.connect(DB)

    detail_total = pd.read_sql(
        """
        SELECT SUM(amount)
        total
        FROM detail_table
        """,
        conn
    )

    batch_total = pd.read_sql(
        """
        SELECT SUM(totals)
        total
        FROM batch_table
        """,
        conn
    )

    detail_amount = detail_total.iloc[0,0]
    batch_amount = batch_total.iloc[0,0]

    variance = detail_amount - batch_amount

    conn.close()

    return {
        "detail_total":detail_amount,
        "batch_total":batch_amount,
        "variance":variance
    }