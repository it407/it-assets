# pages/3_Assign_Asset.py

import streamlit as st
import pandas as pd
from datetime import datetime

from utils.permissions import login_required, admin_only
from utils.gsheets import read_sheet, append_row
from utils.constants import ASSETS_MASTER_SHEET, ASSET_ASSIGNMENTS_SHEET
from utils.ui import apply_global_ui
apply_global_ui()

from utils.permissions import admin_only
admin_only()

from utils.navigation import apply_role_based_navigation
apply_role_based_navigation()

from utils.auth import logout
logout()



st.title("Assign Asset")

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
assets_df = read_sheet(ASSETS_MASTER_SHEET)
assignments_df = read_sheet(ASSET_ASSIGNMENTS_SHEET)
employees_df = read_sheet("employee_master")

for df in [assets_df, assignments_df, employees_df]:
    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()

if assets_df.empty or employees_df.empty:
    st.error("Assets or Employees data missing.")
    st.stop()

# ─────────────────────────────────────────────
# Currently assigned assets
# ─────────────────────────────────────────────
assigned_asset_ids = []
if not assignments_df.empty:
    assigned_asset_ids = assignments_df[
        assignments_df["assignment_status"] == "Assigned"
    ]["asset_id"].astype(str).tolist()

# ─────────────────────────────────────────────
# Available assets
# ─────────────────────────────────────────────
available_assets = assets_df[
    (assets_df["is_active"].astype(str).str.lower() == "true")
    & (~assets_df["asset_id"].isin(assigned_asset_ids))
]

if available_assets.empty:
    st.warning("No available assets for assignment.")
    st.stop()

active_employees = employees_df[
    employees_df["employment_status"] == "Active"
]

# ─────────────────────────────────────────────
# SAFE assignment_id generator
# ─────────────────────────────────────────────
def get_next_assignment_id(df: pd.DataFrame) -> str:
    if df.empty or "assignment_id" not in df.columns:
        return "ASN-0001"

    nums = df["assignment_id"].astype(str).str.extract(r"(\d+)")
    nums = nums.dropna()

    if nums.empty:
        return "ASN-0001"

    return f"ASN-{str(nums[0].astype(int).max() + 1).zfill(4)}"

# ─────────────────────────────────────────────
# Assignment form
# ─────────────────────────────────────────────
with st.form("assign_asset_form"):
    asset_option = st.selectbox(
        "Select Asset",
        available_assets.apply(
            lambda x: f"{x['asset_id']} | {x['asset_name']} | {x['location']}",
            axis=1
        )
    )

    employee_option = st.selectbox(
        "Select Employee",
        active_employees.apply(
            lambda x: f"{x['employee_id']} | {x['employee_name']}",
            axis=1
        )
    )

    assigned_on = st.date_input("Assigned On", value=datetime.today())
    remarks = st.text_input("Remarks (optional)")

    submit = st.form_submit_button("✅ Assign Asset")

# ─────────────────────────────────────────────
# Assignment logic
# ─────────────────────────────────────────────
if submit:
    asset_id = asset_option.split(" | ")[0]
    employee_id, employee_name = employee_option.split(" | ", 1)

    if asset_id in assigned_asset_ids:
        st.error("Asset already assigned.")
        st.stop()

    assignment_id = get_next_assignment_id(assignments_df)

    append_row(
        ASSET_ASSIGNMENTS_SHEET,
        {
            "assignment_id": assignment_id,
            "asset_id": asset_id,
            "employee_id": employee_id,
            "employee_name": employee_name,
            "assigned_on": assigned_on.isoformat(),
            "returned_on": "",
            "assignment_status": "Assigned",
            "remarks": remarks,
            "return_reason": "",
            "created_at": datetime.now().isoformat(),
        }
    )

    st.success(f"Asset {asset_id} assigned to {employee_name}")
    st.rerun()

# ─────────────────────────────────────────────
# Active assignments view
# ─────────────────────────────────────────────
st.divider()
st.subheader("📌 Active Asset Assignments")

if not assignments_df.empty:
    st.dataframe(
        assignments_df[
            assignments_df["assignment_status"] == "Assigned"
        ].sort_values("assigned_on", ascending=False),
        use_container_width=True
    )
