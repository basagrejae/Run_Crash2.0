# Cash Posting & Balancing App

A local Python/Streamlit application for healthcare cash posting and payment batch reconciliation.

## Features
- Create payment batches
- Track deposit amount
- Post checks/EFT/ERA payments
- Track patient account and claim numbers
- Record adjustments and posted amounts
- Automatic batch balancing and variance calculation
- Open/Balanced/Closed batch statuses
- Batch history
- CSV import/export
- SQLite local database

## Run on Windows

1. Install Python 3.10+.
2. Open Command Prompt in this folder.
3. Run:
   `pip install -r requirements.txt`
4. Start:
   `streamlit run app.py`
5. Open the local address shown by Streamlit, normally:
   `http://localhost:8501`

The database file `cash_posting.db` is created automatically in the app folder.

## Important
This is a starter/local application. For production healthcare use, add authentication, role-based access, audit logging, encryption, secure hosting, backups, and HIPAA/security controls before entering real PHI.
