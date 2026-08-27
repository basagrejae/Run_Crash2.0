import pandas as pd
import sqlite3

DETAIL_FILE="detail_table.xlsx"
BATCH_FILE="batch_table.xlsx"
DB_FILE="variance.db"

def load_data():
    return pd.read_excel(DETAIL_FILE, engine="openpyxl"), pd.read_excel(BATCH_FILE, engine="openpyxl")

def save_to_sql(detail_df, batch_df):
    conn=sqlite3.connect(DB_FILE)
    detail_df.to_sql("pas_detail", conn, if_exists="replace", index=False)
    batch_df.to_sql("batch_summary", conn, if_exists="replace", index=False)
    conn.close()

def create_variance_table(detail_df,batch_df):
    amount_total=pd.to_numeric(detail_df["Amount"],errors="coerce").fillna(0).sum()
    variance_df=batch_df.copy()
    variance_df["Totals"]=pd.to_numeric(variance_df["Totals"],errors="coerce").fillna(0)
    variance_df["Detail_Amount_Total"]=amount_total
    variance_df["Variance"]=variance_df["Totals"]-amount_total
    return variance_df

def save_variance_sql(variance_df):
    conn=sqlite3.connect(DB_FILE)
    variance_df.to_sql("variance_table",conn,if_exists="replace",index=False)
    result=pd.read_sql_query("SELECT Batch, Totals, Detail_Amount_Total, (Totals-Detail_Amount_Total) AS Variance FROM variance_table",conn)
    conn.close()
    return result

if __name__=="__main__":
    detail_df,batch_df=load_data()
    save_to_sql(detail_df,batch_df)
    variance_df=create_variance_table(detail_df,batch_df)
    result=save_variance_sql(variance_df)
    print(result)
    variance_df.to_excel("variance_output.xlsx",index=False)
