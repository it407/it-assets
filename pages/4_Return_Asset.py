# pages/4_Return_Asset.py

import streamlit as st
from datetime import datetime

from utils.permissions import admin_only
from utils.gsheets import read_sheet, write_sheet
from utils.constants import ASSET_ASSIGNMENTS_SHEET, ASSETS_MASTER_SHEET
from utils.ui import apply_global_ui
from utils.auth import logout

# ─────────────────────────────────────────────
# Global UI + Security
# ─────────────────────────────────────────────
apply_global_ui()
admin_only()
logout()

st.title("↩️ Return Asset")

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
assignments_df = read_sheet(ASSET_ASSIGNMENTS_SHEET)
assets_df = read_sheet(ASSETS_MASTER_SHEET)

if assignments_df.empty or assets_df.empty:
    st.info("No asset data available.")
    st.stop()

# Normalize columns
for df in [assignments_df, assets_df]:
    df.columns = df.columns.str.strip().str.lower()

# Active assignments only
active_assignments = assignments_df[
    assignments_df["assignment_status"] == "Assigned"
].copy()

if active_assignments.empty:
    st.info("No active asset assignments.")
    st.stop()

# Join asset_name
active_assignments = active_assignments.merge(
    assets_df[["asset_id", "asset_name"]],
    on="asset_id",
    how="left"
)

# ─────────────────────────────────────────────
# Employee selection (OUTSIDE FORM → dynamic)
# ─────────────────────────────────────────────
active_assignments["employee_label"] = (
    active_assignments["employee_id"] + " | " +
    active_assignments["employee_name"]
)

employee_options = sorted(
    active_assignments["employee_label"].unique().tolist()
)

selected_employee = st.selectbox(
    "Select Employee (search by ID or Name) *",
    employee_options
)

employee_id = selected_employee.split(" | ")[0]

# Filter assets for selected employee
emp_assets = active_assignments[
    active_assignments["employee_id"] == employee_id
].copy()

if emp_assets.empty:
    st.warning("No assets assigned to this employee.")
    st.stop()

emp_assets["asset_label"] = (
    emp_assets["asset_id"] + " | " +
    emp_assets["asset_name"]
)

asset_options = sorted(emp_assets["asset_label"].tolist())

# ─────────────────────────────────────────────
# Return Form (ASSET + SUBMIT)
# ─────────────────────────────────────────────
with st.form("return_asset_form"):

    selected_asset = st.selectbox(
        "Select Asset *",
        asset_options
    )

    asset_id = selected_asset.split(" | ")[0]

    assignment_row = emp_assets[
        emp_assets["asset_id"] == asset_id
    ].iloc[0]

    assignment_id = assignment_row["assignment_id"]

    return_reason = st.selectbox(
        "Return Reason *",
        [
            "Reassignment",
            "Employee Exit",
            "Asset Inactive / Damaged",
            "Other",
        ]
    )

    returned_on = st.date_input(
        "Return Date",
        value=datetime.today()
    )

    submit = st.form_submit_button("↩️ Return Asset")

# ─────────────────────────────────────────────
# Return Logic
# ─────────────────────────────────────────────
if submit:

    assignments_df.loc[
        assignments_df["assignment_id"] == assignment_id,
        ["assignment_status", "returned_on", "return_reason"]
    ] = [
        "Returned",
        returned_on.isoformat(),
        return_reason,
    ]

    if return_reason == "Asset Inactive / Damaged":
        assets_df.loc[
            assets_df["asset_id"] == asset_id,
            "is_active"
        ] = False

        assets_df.loc[
            assets_df["asset_id"] == asset_id,
            "updated_at"
        ] = datetime.now().isoformat()

    write_sheet(ASSET_ASSIGNMENTS_SHEET, assignments_df)
    write_sheet(ASSETS_MASTER_SHEET, assets_df)

    st.success("Asset returned successfully")
    st.rerun()

# ─────────────────────────────────────────────
# Active Assignments View
# ─────────────────────────────────────────────
st.divider()
st.subheader("📌 Currently Assigned Assets")

st.dataframe(
    active_assignments.sort_values("assigned_on", ascending=False),
    use_container_width=True
)
