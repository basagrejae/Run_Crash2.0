import streamlit as st
import pandas as pd

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