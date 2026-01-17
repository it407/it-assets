# utils/gsheets.py

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def _get_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    return gspread.authorize(creds)

def read_sheet(sheet_name: str) -> pd.DataFrame:
    client = _get_client()
    sh = client.open_by_key(st.secrets["gcp_service_account"]["spreadsheet_id"])
    ws = sh.worksheet(sheet_name)

    records = ws.get_all_records()
    df = pd.DataFrame(records)

    if df.empty:
        return df

    df.columns = df.columns.str.strip().str.lower()
    return df

def write_sheet(sheet_name: str, df: pd.DataFrame):
    client = _get_client()
    sh = client.open_by_key(st.secrets["gcp_service_account"]["spreadsheet_id"])
    ws = sh.worksheet(sheet_name)

    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()

    ws.clear()
    ws.update([df.columns.tolist()] + df.astype(str).values.tolist())

def append_row(sheet_name: str, row: dict):
    client = _get_client()
    sh = client.open_by_key(st.secrets["gcp_service_account"]["spreadsheet_id"])
    ws = sh.worksheet(sheet_name)

    ordered_row = [str(row.get(col, "")) for col in ws.row_values(1)]
    ws.append_row(ordered_row)
