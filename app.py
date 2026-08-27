import streamlit as st

from auth import login
from reconciliation import *

st.set_page_config(
    page_title="Cash Posting System",
    layout="wide"
)

st.title("Cash Posting & Balancing")

if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role is None:

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        role = login(username,password)

        if role:

            st.session_state.role = role
            st.success("Login Successful")

        else:
            st.error("Invalid Login")

else:

    st.sidebar.write(
        f"Role: {st.session_state.role}"
    )

    detail_file = st.file_uploader(
        "Detail Table",
        type="xlsx"
    )

    batch_file = st.file_uploader(
        "Batch Table",
        type="xlsx"
    )

    if st.button("Import Files"):

        if detail_file:
            load_detail(detail_file)

        if batch_file:
            load_batch(batch_file)

        st.success(
            "Files Imported"
        )

# Clear imported records
        if st.button("🗑️ Clear Detail & Batch Data"):

            clear_tables()

            st.success(
                "detail_table and batch_table have been cleared."
            )

            st.rerun()
    if st.button("Balance Batch"):

        result = reconcile()


        st.metric(
            "Detail Total",
            f"${result['detail_total']:,.2f}"
        )

        st.metric(
            "Batch Total",
            f"${result['batch_total']:,.2f}"
        )

        st.metric(
            "Variance",
            f"${result['variance']:,.2f}"
        )

        if result['variance'] == 0:
            st.success("BALANCED")
        else:
            st.error("OUT OF BALANCE")