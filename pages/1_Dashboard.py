# pages/1_Dashboard.py

import streamlit as st
import pandas as pd
import duckdb

from utils.permissions import login_required, admin_only
from utils.gsheets import read_sheet
from utils.export import export_csv
from utils.constants import ASSETS_MASTER_SHEET, ASSET_ASSIGNMENTS_SHEET

from utils.permissions import admin_or_manager_only
from utils.navigation import apply_role_based_navigation
from utils.auth import logout

from utils.ui import apply_global_ui
apply_global_ui()

admin_or_manager_only()
apply_role_based_navigation()
logout()

# ─────────────────────────────────────────────
# Back to Dashboard Hub
# ─────────────────────────────────────────────
if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")

st.title("Dashboard")

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
assets_df = read_sheet(ASSETS_MASTER_SHEET)
assignments_df = read_sheet(ASSET_ASSIGNMENTS_SHEET)

if assets_df.empty:
    st.info("No assets found.")
    st.stop()

assets_df.columns = assets_df.columns.str.strip().str.lower()

if not assignments_df.empty:
    assignments_df.columns = assignments_df.columns.str.strip().str.lower()
else:
    assignments_df = pd.DataFrame(columns=["asset_id", "assignment_status"])

# ─────────────────────────────────────────────
# Filters
# ─────────────────────────────────────────────
st.subheader("🔎 Filters")

col1, col2 = st.columns(2)

with col1:
    category_filter = st.multiselect(
        "Category",
        sorted(assets_df["category"].dropna().unique().tolist()),
        default=sorted(assets_df["category"].dropna().unique().tolist())
    )

with col2:
    location_filter = st.multiselect(
        "Location",
        sorted(assets_df["location"].dropna().unique().tolist()),
        default=sorted(assets_df["location"].dropna().unique().tolist())
    )

filtered_assets_df = assets_df[
    assets_df["category"].isin(category_filter)
    & assets_df["location"].isin(location_filter)
]

if filtered_assets_df.empty:
    st.warning("No data for selected filters.")
    st.stop()

# ─────────────────────────────────────────────
# DuckDB aggregation
# ─────────────────────────────────────────────
con = duckdb.connect(database=":memory:")

con.register("assets_master", filtered_assets_df)

assigned_df = (
    assignments_df[assignments_df["assignment_status"] == "Assigned"]
    if not assignments_df.empty
    else assignments_df
)

con.register("asset_assignments", assigned_df[["asset_id"]])

query = """
SELECT
    am.category,
    COUNT(*) AS total_qty,

    /* Inactive / Damaged assets */
    SUM(
        CASE 
            WHEN LOWER(CAST(am.is_active AS VARCHAR)) IN ('false', '0', 'no')
            THEN 1 
            ELSE 0 
        END
    ) AS out_of_service_qty,

    /* Currently assigned assets */
    COUNT(a.asset_id) AS total_assigned,

    /* Available assets */
    COUNT(*) 
        - SUM(
            CASE 
                WHEN LOWER(CAST(am.is_active AS VARCHAR)) IN ('false', '0', 'no')
                THEN 1 
                ELSE 0 
            END
        )
        - COUNT(a.asset_id)
        AS available_qty,

    am.location
FROM assets_master am
LEFT JOIN asset_assignments a
    ON am.asset_id = a.asset_id
GROUP BY am.category, am.location
ORDER BY am.category, am.location
"""

summary_df = con.execute(query).df()

# ─────────────────────────────────────────────
# Dashboard table
# ─────────────────────────────────────────────
st.subheader("🧾 Asset Summary")

st.dataframe(
    summary_df,
    use_container_width=True
)

# ─────────────────────────────────────────────
# CSV Export
# ─────────────────────────────────────────────
export_csv(summary_df, "asset_dashboard_summary.csv")
