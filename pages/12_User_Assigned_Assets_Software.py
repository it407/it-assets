import streamlit as st
import pandas as pd
import duckdb

from utils.permissions import admin_or_manager_only
from utils.gsheets import read_sheet
from utils.ui import apply_global_ui
from utils.auth import logout

apply_global_ui()
admin_or_manager_only()
logout()

st.title("👤 User-wise Assigned Assets & Software")

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
assets_assign_df = read_sheet("asset_assignments")
assets_master_df = read_sheet("assets_master")
software_assign_df = read_sheet("software_assignments")
employees_df = read_sheet("employee_master")

dfs = [assets_assign_df, assets_master_df, software_assign_df, employees_df]
for df in dfs:
    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()

# Guard
if assets_assign_df.empty and software_assign_df.empty:
    st.info("No asset or software assignments found.")
    st.stop()

# ─────────────────────────────────────────────
# DuckDB joins
# ─────────────────────────────────────────────
con = duckdb.connect(database=":memory:")

con.register("asset_assign", assets_assign_df)
con.register("asset_master", assets_master_df)
con.register("software_assign", software_assign_df)
con.register("employees", employees_df)

query = """
-- ASSETS
SELECT
    e.employee_id,
    e.employee_name,
    'Asset' AS assignment_type,
    a.asset_id,
    am.asset_name,
    NULL AS soft_id,
    NULL AS soft_name,
    am.location,
    e.department,
    a.assigned_on
FROM asset_assign a
JOIN employees e ON a.employee_id = e.employee_id
JOIN asset_master am ON a.asset_id = am.asset_id
WHERE a.assignment_status = 'Assigned'

UNION ALL

-- SOFTWARE
SELECT
    e.employee_id,
    e.employee_name,
    'Software' AS assignment_type,
    NULL AS asset_id,
    NULL AS asset_name,
    s.soft_id,
    s.soft_name,
    e.location,
    e.department,
    s.assigned_on
FROM software_assign s
JOIN employees e ON s.employee_id = e.employee_id
WHERE s.assignment_status = 'Assigned'
"""

result_df = con.execute(query).df()

if result_df.empty:
    st.info("No active assignments found.")
    st.stop()

# ─────────────────────────────────────────────
# Filters
# ─────────────────────────────────────────────
st.subheader("🔍 Filters")

col1, col2, col3 = st.columns(3)

with col1:
    search = st.text_input("Search Employee (ID / Name)")

with col2:
    dept_filter = st.selectbox(
        "Department",
        ["All"] + sorted(result_df["department"].dropna().unique().tolist())
    )

with col3:
    loc_filter = st.selectbox(
        "Location",
        ["All"] + sorted(result_df["location"].dropna().unique().tolist())
    )

# Apply filters
filtered_df = result_df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df["employee_id"].str.contains(search, case=False, na=False)
        | filtered_df["employee_name"].str.contains(search, case=False, na=False)
    ]

if dept_filter != "All":
    filtered_df = filtered_df[filtered_df["department"] == dept_filter]

if loc_filter != "All":
    filtered_df = filtered_df[filtered_df["location"] == loc_filter]

# ─────────────────────────────────────────────
# Display
# ─────────────────────────────────────────────
st.subheader("📋 Assigned Assets & Software")

display_cols = [
    "employee_id",
    "employee_name",
    "assignment_type",
    "asset_id",
    "asset_name",
    "soft_id",
    "soft_name",
    "location",
    "department",
    "assigned_on",
]

st.dataframe(
    filtered_df[display_cols]
    .sort_values("assigned_on", ascending=False),
    use_container_width=True,
)

# ─────────────────────────────────────────────
# Export
# ─────────────────────────────────────────────
st.download_button(
    "⬇ Download CSV",
    data=filtered_df[display_cols].to_csv(index=False),
    file_name="user_assigned_assets_software.csv",
    mime="text/csv",
)
