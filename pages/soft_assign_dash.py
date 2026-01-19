import streamlit as st
import pandas as pd
import duckdb

from utils.permissions import admin_or_manager_only
from utils.gsheets import read_sheet
from utils.ui import apply_global_ui
from utils.auth import logout

# ─────────────────────────────────────────────
# Auth & UI
# ─────────────────────────────────────────────
apply_global_ui()
admin_or_manager_only()
logout()

st.title("💻 User-wise Assigned Software")

# ─────────────────────────────────────────────
# Load Data
# ─────────────────────────────────────────────
software_assign_df = read_sheet("software_assignments")
software_master_df = read_sheet("software_master")
employees_df = read_sheet("employee_master")

# Normalize column names
for df in [software_assign_df, software_master_df, employees_df]:
    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()

# Guard
if software_assign_df.empty:
    st.info("No software assignments found.")
    st.stop()

# ─────────────────────────────────────────────
# DuckDB Join
# ─────────────────────────────────────────────
con = duckdb.connect(database=":memory:")

con.register("software_assign", software_assign_df)
con.register("software_master", software_master_df)
con.register("employees", employees_df)

query = """
SELECT
    s.soft_id,
    sm.soft_name,
    e.employee_id   AS user_id,
    e.employee_name AS user_name,
    e.location,
    e.department,
    s.assigned_on,
    sm.links        AS link
FROM software_assign s
JOIN employees e
    ON s.employee_id = e.employee_id
JOIN software_master sm
    ON s.soft_id = sm.soft_id
WHERE s.assignment_status = 'Assigned'
"""

result_df = con.execute(query).df()

if result_df.empty:
    st.info("No active software assignments found.")
    st.stop()

# ─────────────────────────────────────────────
# Filters
# ─────────────────────────────────────────────
st.subheader("🔍 Filters")

col1, col2, col3 = st.columns(3)

with col1:
    search = st.text_input("Search User (ID / Name)")

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

filtered_df = result_df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df["user_id"].str.contains(search, case=False, na=False)
        | filtered_df["user_name"].str.contains(search, case=False, na=False)
    ]

if dept_filter != "All":
    filtered_df = filtered_df[filtered_df["department"] == dept_filter]

if loc_filter != "All":
    filtered_df = filtered_df[filtered_df["location"] == loc_filter]

# ─────────────────────────────────────────────
# Display
# ─────────────────────────────────────────────
st.subheader("📋 Assigned Software")

display_cols = [
    "soft_id",
    "soft_name",
    "user_id",
    "user_name",
    "location",
    "department",
    "assigned_on",
    "link",
]

st.dataframe(
    filtered_df[display_cols]
        .sort_values("assigned_on", ascending=False),
    use_container_width=True
)

# ─────────────────────────────────────────────
# Export
# ─────────────────────────────────────────────
st.download_button(
    "⬇ Download CSV",
    data=filtered_df[display_cols].to_csv(index=False),
    file_name="user_assigned_software.csv",
    mime="text/csv",
)
