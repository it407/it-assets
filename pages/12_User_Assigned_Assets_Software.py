import streamlit as st
import duckdb
import pandas as pd

from utils.permissions import admin_or_manager_only
from utils.gsheets import read_sheet
from utils.ui import apply_global_ui
from utils.auth import logout

# ─────────────────────────────────────────────
# Security & UI
# ─────────────────────────────────────────────
apply_global_ui()
admin_or_manager_only()
logout()

st.title("👤 User Assigned Assets & Software")

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
asset_assign_df = read_sheet("asset_assignments")
asset_master_df = read_sheet("assets_master")
software_assign_df = read_sheet("software_assignments")
software_master_df = read_sheet("software_master")
employee_df = read_sheet("employee_master")

dfs = [
    asset_assign_df,
    asset_master_df,
    software_assign_df,
    software_master_df,
    employee_df,
]

for df in dfs:
    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()

# ─────────────────────────────────────────────
# DuckDB
# ─────────────────────────────────────────────
con = duckdb.connect(database=":memory:")

con.register("asset_assign", asset_assign_df)
con.register("asset_master", asset_master_df)
con.register("software_assign", software_assign_df)
con.register("software_master", software_master_df)
con.register("employee", employee_df)

# ─────────────────────────────────────────────
# ASSETS QUERY
# ─────────────────────────────────────────────
asset_query = """
SELECT
    e.employee_id,
    e.employee_name,
    am.asset_id,
    am.asset_name,
    am.category,
    am.location,
    e.department,
    a.assigned_on
FROM asset_assign a
JOIN asset_master am ON a.asset_id = am.asset_id
JOIN employee e ON a.employee_id = e.employee_id
WHERE a.assignment_status = 'Assigned'
"""

asset_df = con.execute(asset_query).df()

# ─────────────────────────────────────────────
# SOFTWARE QUERY
# ─────────────────────────────────────────────
software_query = """
SELECT
    e.employee_id,
    e.employee_name,
    sm.soft_id,
    sm.soft_name,
    sm.links,
    e.location,
    e.department,
    s.assigned_on
FROM software_assign s
JOIN software_master sm ON s.soft_id = sm.soft_id
JOIN employee e ON s.employee_id = e.employee_id
WHERE s.assignment_status = 'Assigned'
"""

software_df = con.execute(software_query).df()

# ─────────────────────────────────────────────
# Filters
# ─────────────────────────────────────────────
st.subheader("🔍 Filters")

col1, col2, col3 = st.columns(3)

with col1:
    search = st.text_input("Search Employee (ID / Name)")

with col2:
    dept = st.selectbox(
        "Department",
        ["All"] + sorted(
            set(
                pd.concat(
                    [
                        asset_df["department"],
                        software_df["department"],
                    ],
                    ignore_index=True,
                ).dropna()
            )
        ),
    )

with col3:
    location = st.selectbox(
        "Location",
        ["All"] + sorted(
            set(
                pd.concat(
                    [
                        asset_df["location"],
                        software_df["location"],
                    ],
                    ignore_index=True,
                ).dropna()
            )
        ),
    )

# Apply filters
def apply_filters(df):
    if search:
        df = df[
            df["employee_id"].str.contains(search, case=False, na=False)
            | df["employee_name"].str.contains(search, case=False, na=False)
        ]

    if dept != "All":
        df = df[df["department"] == dept]

    if location != "All":
        df = df[df["location"] == location]

    return df


asset_df = apply_filters(asset_df)
software_df = apply_filters(software_df)

# ─────────────────────────────────────────────
# ASSETS SECTION
# ─────────────────────────────────────────────
st.divider()
st.subheader("🖥️ Assigned Assets")

if asset_df.empty:
    st.info("No assigned assets found.")
else:
    st.dataframe(
        asset_df[
            [
                "employee_id",
                "employee_name",
                "asset_id",
                "asset_name",
                "category",
                "location",
                "department",
                "assigned_on",
            ]
        ].sort_values("assigned_on", ascending=False),
        use_container_width=True,
    )

# ─────────────────────────────────────────────
# SOFTWARE SECTION (WITH OPEN + COPY)
# ─────────────────────────────────────────────
st.divider()
st.subheader("💻 Assigned Software")

if software_df.empty:
    st.info("No assigned software found.")
else:
    for i, row in software_df.sort_values(
        "assigned_on", ascending=False
    ).iterrows():

        with st.container():
            col1, col2, col3 = st.columns([6, 1, 1])

            with col1:
                st.markdown(
                    f"""
                    **{row['soft_name']}**  
                    `{row['soft_id']}`  
                    👤 {row['employee_name']} ({row['employee_id']})  
                    📍 {row['location']} | 🏢 {row['department']}
                    """
                )

            with col2:
                if row["links"]:
                    st.link_button("🌐 Open", row["links"])

            with col3:
                if row["links"]:
                    if st.button("📋 Copy", key=f"copy_{i}"):
                        st.code(row["links"])
                        st.toast("Link ready to copy")
