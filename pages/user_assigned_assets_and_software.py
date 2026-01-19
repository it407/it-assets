import streamlit as st
import pandas as pd
import duckdb

from utils.permissions import admin_or_manager_only
from utils.gsheets import read_sheet
from utils.constants import (
    SOFTWARE_ASSIGNMENTS_SHEET,
    SOFTWARE_MASTER_SHEET,
    EMPLOYEE_MASTER_SHEET,
)
from utils.html_table import render_html_table
from utils.ui import apply_global_ui
from utils.auth import logout

# ─────────────────────────────────────────────
# Global UI + Security
# ─────────────────────────────────────────────
apply_global_ui()
admin_or_manager_only()
logout()

# ─────────────────────────────────────────────
# Back to Dashboard Hub
# ─────────────────────────────────────────────
if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")

st.title("💻 User Assigned Software")

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
assign_df = read_sheet(SOFTWARE_ASSIGNMENTS_SHEET)
software_df = read_sheet(SOFTWARE_MASTER_SHEET)
employees_df = read_sheet(EMPLOYEE_MASTER_SHEET)

if assign_df.empty:
    st.info("No software assignments found.")
    st.stop()

# Normalize columns
for df in [assign_df, software_df, employees_df]:
    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()

# Keep only ACTIVE assignments
assign_df = assign_df[assign_df["status"] == "Active"]

if assign_df.empty:
    st.info("No active software assignments.")
    st.stop()

# ─────────────────────────────────────────────
# DuckDB JOIN (SAFE & EXPLICIT)
# ─────────────────────────────────────────────
con = duckdb.connect(database=":memory:")

con.register("assign", assign_df)
con.register("soft", software_df)
con.register("emp", employees_df)

query = """
SELECT
    a.employee_id,
    e.employee_name,
    a.soft_id,
    s.soft_name,
    e.department,
    e.location,
    a.assigned_on,
    s.links
FROM assign a
LEFT JOIN soft s
    ON a.soft_id = s.soft_id
LEFT JOIN emp e
    ON a.employee_id = e.employee_id
ORDER BY a.assigned_on DESC
"""

result_df = con.execute(query).df()

if result_df.empty:
    st.info("No assigned software records.")
    st.stop()

# ─────────────────────────────────────────────
# Filters
# ─────────────────────────────────────────────
st.subheader("🔎 Filters")

col1, col2, col3, col4 = st.columns(4)

with col1:
    emp_search = st.text_input("Employee ID / Name")

with col2:
    dept_filter = st.multiselect(
        "Department",
        sorted(result_df["department"].dropna().unique()),
        default=sorted(result_df["department"].dropna().unique()),
    )

with col3:
    location_filter = st.multiselect(
        "Location",
        sorted(result_df["location"].dropna().unique()),
        default=sorted(result_df["location"].dropna().unique()),
    )

with col4:
    soft_filter = st.multiselect(
        "Software",
        sorted(result_df["soft_name"].dropna().unique()),
        default=sorted(result_df["soft_name"].dropna().unique()),
    )

filtered_df = result_df.copy()

if emp_search:
    filtered_df = filtered_df[
        filtered_df["employee_id"].astype(str).str.contains(emp_search, case=False, na=False)
        | filtered_df["employee_name"].astype(str).str.contains(emp_search, case=False, na=False)
    ]

filtered_df = filtered_df[
    filtered_df["department"].isin(dept_filter)
    & filtered_df["location"].isin(location_filter)
    & filtered_df["soft_name"].isin(soft_filter)
]

# ─────────────────────────────────────────────
# Software Table (HTML – Reusable)
# ─────────────────────────────────────────────
render_html_table(
    df=filtered_df,
    columns=[
        "employee_id",
        "employee_name",
        "soft_id",
        "soft_name",
        "department",
        "location",
        "assigned_on",
    ],
    link_column="links",
)
