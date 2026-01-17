# pages/5_My_Assets.py

import streamlit as st
import pandas as pd
from utils.navigation import apply_role_based_navigation
from utils.permissions import login_required
from utils.gsheets import read_sheet
from utils.export import export_csv
from utils.constants import ASSET_ASSIGNMENTS_SHEET, ASSETS_MASTER_SHEET, ROLE_ADMIN
from utils.ui import apply_global_ui
apply_global_ui()

from utils.auth import logout

# ─────────────────────────────────────────────
# Page protection
# ─────────────────────────────────────────────
login_required()
apply_role_based_navigation()
logout()

user = st.session_state["user"]
employee_id = user["employee_id"]
is_admin = user["role"] == ROLE_ADMIN

st.title("My Assets")

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
assignments_df = read_sheet(ASSET_ASSIGNMENTS_SHEET)
assets_df = read_sheet(ASSETS_MASTER_SHEET)

if assignments_df.empty:
    st.info("No asset assignments found.")
    st.stop()

for df in [assignments_df, assets_df]:
    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()

# ─────────────────────────────────────────────
# STRICT permission filter
# ─────────────────────────────────────────────
if not is_admin:
    assignments_df = assignments_df[
        assignments_df["employee_id"] == employee_id
    ]

# ─────────────────────────────────────────────
# Attach asset name & category (READ-ONLY JOIN)
# ─────────────────────────────────────────────
assignments_df = assignments_df.merge(
    assets_df[
        ["asset_id", "asset_name", "category", "location"]
    ],
    on="asset_id",
    how="left"
)

# ─────────────────────────────────────────────
# Split current & history
# ─────────────────────────────────────────────
current_assets = assignments_df[
    assignments_df["assignment_status"] == "Assigned"
]

past_assets = assignments_df[
    assignments_df["assignment_status"] == "Returned"
]

# ─────────────────────────────────────────────
# Current assets
# ─────────────────────────────────────────────
st.subheader("📌 Currently Assigned Assets")

if current_assets.empty:
    st.info("No active assets.")
else:
    st.dataframe(
        current_assets[
            [
                "assignment_id",
                "asset_id",
                "asset_name",
                "category",
                "location",
                "assigned_on",
                "remarks",
            ]
        ].sort_values("assigned_on", ascending=False),
        use_container_width=True,
    )

    export_csv(current_assets, "my_current_assets.csv")

# ─────────────────────────────────────────────
# Past assets
# ─────────────────────────────────────────────
st.divider()
st.subheader("📜 Assignment History")

if past_assets.empty:
    st.info("No past assets.")
else:
    st.dataframe(
        past_assets[
            [
                "assignment_id",
                "asset_id",
                "asset_name",
                "category",
                "location",
                "assigned_on",
                "returned_on",
                "return_reason",
            ]
        ].sort_values("returned_on", ascending=False),
        use_container_width=True,
    )

    export_csv(past_assets, "my_asset_history.csv")
