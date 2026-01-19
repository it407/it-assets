import streamlit as st
from datetime import datetime

from utils.permissions import admin_only
from utils.gsheets import read_sheet, write_sheet
from utils.auth import logout

admin_only()
logout()

st.title("↩️ Return Software")

df = read_sheet("software_assignments")
if df.empty:
    st.info("No assignments found")
    st.stop()

df.columns = df.columns.str.strip().str.lower()

active_df = df[df["assignment_status"] == "Assigned"]

if active_df.empty:
    st.info("No active software assignments")
    st.stop()

options = active_df.apply(
    lambda x: f"{x['assignment_id']} | {x['soft_name']} | {x['employee_name']}",
    axis=1
)

choice = st.selectbox("Select Assignment", options)
return_reason = st.text_input("Return Reason")

if st.button("Return Software"):
    aid = choice.split(" | ")[0]
    idx = df[df["assignment_id"] == aid].index

    df.loc[idx, "assignment_status"] = "Returned"
    df.loc[idx, "returned_on"] = datetime.now().isoformat()
    df.loc[idx, "remarks"] = return_reason

    write_sheet("software_assignments", df)

    st.success("Software returned successfully")
    st.rerun()
