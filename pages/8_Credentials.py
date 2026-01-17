# pages/8_Credentials.py

import streamlit as st
import pandas as pd
from datetime import datetime

from utils.permissions import login_required, admin_only
from utils.gsheets import read_sheet, append_row
from utils.ui import apply_global_ui
apply_global_ui()

from utils.permissions import admin_only
admin_only()

from utils.navigation import apply_role_based_navigation
apply_role_based_navigation()

from utils.auth import logout
logout()


st.title("Credentials")

SHEET_NAME = "credentials_master"

# ─────────────────────────────────────────────
# Load existing credentials
# ─────────────────────────────────────────────
cred_df = read_sheet(SHEET_NAME)
if not cred_df.empty:
    cred_df.columns = cred_df.columns.str.strip().str.lower()

# ─────────────────────────────────────────────
# Safe credential_id generator
# Format: CRED-001
# ─────────────────────────────────────────────
def get_next_credential_id(df: pd.DataFrame):
    if df.empty or "credential_id" not in df.columns:
        return "CRED-001"

    nums = df["credential_id"].astype(str).str.extract(r"(\d+)")
    nums = nums.dropna()

    if nums.empty:
        return "CRED-001"

    next_num = nums[0].astype(int).max() + 1
    return f"CRED-{str(next_num).zfill(3)}"

# ─────────────────────────────────────────────
# Submission form
# ─────────────────────────────────────────────
with st.form("credential_form"):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Name *")
        category = st.text_input("Category *")
        login_id = st.text_input("Login ID / Username *")

    with col2:
        password = st.text_input("Password *")
        link_url = st.text_input("Link / URL")
        remark = st.text_area("Remark")

    submit = st.form_submit_button("➕ Save Credential")

# ─────────────────────────────────────────────
# Submit logic
# ─────────────────────────────────────────────
if submit:
    if not name or not category or not login_id or not password:
        st.error("Name, Category, Login ID, and Password are required.")
        st.stop()

    credential_id = get_next_credential_id(cred_df)

    append_row(
        SHEET_NAME,
        {
            "credential_id": credential_id,
            "name": name,
            "category": category,
            "login_id": login_id,
            "password": password,
            "link_url": link_url,
            "remark": remark,
            "created_at": datetime.now().isoformat(),
        }
    )

    st.success("Credential saved successfully")
    st.rerun()

# ─────────────────────────────────────────────
# Credentials table view
# ─────────────────────────────────────────────
st.divider()
st.subheader("📋 Stored Credentials")

if cred_df.empty:
    st.info("No credentials found.")
else:
    st.dataframe(
        cred_df.sort_values("created_at", ascending=False),
        use_container_width=True
    )
