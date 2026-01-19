import streamlit as st
from datetime import datetime

from utils.permissions import admin_only
from utils.gsheets import read_sheet, append_row
from utils.auth import logout

admin_only()
logout()

st.title("💻 Software Master")

SHEET_NAME = "software_master"

df = read_sheet(SHEET_NAME)
if not df.empty:
    df.columns = df.columns.str.strip().str.lower()

# ─────────────────────────────────────────────
# Generate soft_id
# ─────────────────────────────────────────────
def next_soft_id(df):
    if df.empty:
        return "SOFT-001"
    nums = (
        df["soft_id"]
        .astype(str)
        .str.replace("SOFT-", "", regex=False)
        .astype(int)
    )
    return f"SOFT-{str(nums.max()+1).zfill(3)}"

# ─────────────────────────────────────────────
# Entry Form
# ─────────────────────────────────────────────
with st.form("software_form"):
    soft_name = st.text_input("Software Name *")
    status = st.selectbox("Status *", ["Active", "Paused"])

    col1, col2 = st.columns(2)
    with col1:
        monthly_price = st.text_input("Monthly Price")
        registered_id = st.text_input("Registered ID")
        login_id = st.text_input("Login ID")

    with col2:
        yearly_price = st.text_input("Yearly Price")
        registered_pass = st.text_input("Registered Password")
        login_pass = st.text_input("Login Password")

    links = st.text_input("Links")

    submit = st.form_submit_button("➕ Add Software")

if submit:
    if not soft_name:
        st.error("Software name is required")
        st.stop()

    now = datetime.now().isoformat()

    append_row(
        SHEET_NAME,
        {
            "soft_id": next_soft_id(df),
            "soft_name": soft_name,
            "status": status,
            "monthly_price": monthly_price,
            "yearly_price": yearly_price,
            "registered_id": registered_id,
            "registered_pass": registered_pass,
            "login_id": login_id,
            "login_pass": login_pass,
            "links": links,
            "created_at": now,
            "updated_at": now,
        }
    )

    st.success("Software added successfully")
    st.rerun()

# ─────────────────────────────────────────────
# Table
# ─────────────────────────────────────────────
st.divider()
st.dataframe(df, use_container_width=True)
