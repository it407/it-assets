# pages/5_My_Assets.py

import streamlit as st
import pandas as pd

from utils.navigation import apply_role_based_navigation
from utils.permissions import login_required
from utils.gsheets import read_sheet
from utils.export import export_csv
from utils.constants import (
    ASSET_ASSIGNMENTS_SHEET,
    ASSETS_MASTER_SHEET,
    SOFTWARE_ASSIGNMENTS_SHEET,
    SOFTWARE_MASTER_SHEET,
    ROLE_ADMIN,
)
from utils.ui import apply_global_ui
from utils.auth import logout

# ─────────────────────────────────────────────
# Global UI & Page protection
# ─────────────────────────────────────────────
apply_global_ui()
login_required()
apply_role_based_navigation()
logout()

user = st.session_state["user"]
employee_id = user["employee_id"]
is_admin = user["role"] == ROLE_ADMIN

st.title("My Assets")

# ─────────────────────────────────────────────
# Load ASSET data (UNCHANGED)
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
# STRICT asset permission filter (UNCHANGED)
# ─────────────────────────────────────────────
if not is_admin:
    assignments_df = assignments_df[
        assignments_df["employee_id"] == employee_id
    ]

# ─────────────────────────────────────────────
# Attach asset name & category (UNCHANGED)
# ─────────────────────────────────────────────
assignments_df = assignments_df.merge(
    assets_df[
        ["asset_id", "asset_name", "category", "location"]
    ],
    on="asset_id",
    how="left"
)

# ─────────────────────────────────────────────
# Split current & history (UNCHANGED)
# ─────────────────────────────────────────────
current_assets = assignments_df[
    assignments_df["assignment_status"] == "Assigned"
]

past_assets = assignments_df[
    assignments_df["assignment_status"] == "Returned"
]

# ─────────────────────────────────────────────
# Current assets table (UNCHANGED)
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
# Asset history table (UNCHANGED)
# ─────────────────────────────────────────────
st.divider()
st.subheader("📜 Asset Assignment History")

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

# ─────────────────────────────────────────────
# LOAD SOFTWARE DATA (NEW)
# ─────────────────────────────────────────────
software_assign_df = read_sheet(SOFTWARE_ASSIGNMENTS_SHEET)
software_master_df = read_sheet(SOFTWARE_MASTER_SHEET)

for df in [software_assign_df, software_master_df]:
    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()

# ─────────────────────────────────────────────
# STRICT software permission filter (NEW)
# ─────────────────────────────────────────────
if not is_admin and not software_assign_df.empty:
    software_assign_df = software_assign_df[
        software_assign_df["employee_id"] == employee_id
    ]

# ─────────────────────────────────────────────
# Attach software name & link (READ-ONLY JOIN)
# ─────────────────────────────────────────────
if not software_assign_df.empty:
    software_assign_df = software_assign_df.merge(
        software_master_df[["soft_id", "soft_name", "links"]],
        on="soft_id",
        how="left"
    )

# ─────────────────────────────────────────────
# Split current & history (NEW)
# ─────────────────────────────────────────────
current_software = software_assign_df[
    software_assign_df["assignment_status"] == "Assigned"
]

past_software = software_assign_df[
    software_assign_df["assignment_status"] == "Returned"
]

# ─────────────────────────────────────────────
# SOFTWARE TABLES (ADDED ONLY)
# ─────────────────────────────────────────────
st.divider()
st.title("My Software")

# ───── Current Software ─────
st.subheader("💻 Currently Assigned Software")

if current_software.empty:
    st.info("No software assigned.")
else:
    st.dataframe(
        current_software[
            [
                "soft_id",
                "soft_name",
                "assigned_on",
                "links",
            ]
        ].sort_values("assigned_on", ascending=False),
        use_container_width=True,
        column_config={
            "links": st.column_config.LinkColumn(
                "Software Link",
                display_text="Open"
            )
        }
    )
    export_csv(current_software, "my_current_software.csv")

# ───── Software History ─────
st.subheader("🕘 Software Assignment History")

if past_software.empty:
    st.info("No software history.")
else:
    st.dataframe(
        past_software[
            [
                "soft_id",
                "soft_name",
                "assigned_on",
                "returned_on",
                "return_reason",
            ]
        ].sort_values("returned_on", ascending=False),
        use_container_width=True,
    )
    export_csv(past_software, "my_software_history.csv")
