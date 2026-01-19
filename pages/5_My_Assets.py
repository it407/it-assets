# pages/5_My_Assets.py

import streamlit as st
import pandas as pd
import duckdb

from utils.navigation import apply_role_based_navigation
from utils.permissions import login_required
from utils.gsheets import read_sheet
from utils.export import export_csv
from utils.constants import (
    ASSET_ASSIGNMENTS_SHEET,
    ASSETS_MASTER_SHEET,
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
# MY SOFTWARE (ADDED SECTION ONLY)
# ─────────────────────────────────────────────
st.divider()
st.title("My Software")

software_assign_df = read_sheet("software_assignments")
software_master_df = read_sheet("software_master")
employee_df = read_sheet("employee_master")

for df in [software_assign_df, software_master_df, employee_df]:
    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()

if software_assign_df.empty:
    st.info("No software assignments found.")
else:
    # STRICT user filter (same as assets)
    if not is_admin:
        software_assign_df = software_assign_df[
            software_assign_df["employee_id"] == employee_id
        ]

    con = duckdb.connect(database=":memory:")
    con.register("software_assign", software_assign_df)
    con.register("software_master", software_master_df)
    con.register("employee", employee_df)

    software_df = con.execute("""
    SELECT
        e.employee_id,
        e.employee_name,
        sm.soft_id,
        sm.soft_name,
        sm.links AS link,
        e.department,
        e.location,
        s.assigned_on
    FROM software_assign s
    JOIN software_master sm ON s.soft_id = sm.soft_id
    JOIN employee e ON s.employee_id = e.employee_id
    WHERE s.assignment_status = 'Assigned'
    """).df()

    if software_df.empty:
        st.info("No software assigned.")
    else:
        st.dataframe(
            software_df[
                [
                    "employee_id",
                    "employee_name",
                    "soft_id",
                    "soft_name",
                    "department",
                    "location",
                    "assigned_on",
                    "link",
                ]
            ].sort_values("assigned_on", ascending=False),
            use_container_width=True,
            column_config={
                "link": st.column_config.LinkColumn(
                    "Software Link",
                    display_text="Open"
                )
            }
        )

        export_csv(software_df, "my_assigned_software.csv")
