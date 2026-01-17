# pages/2_Assets.py

import streamlit as st
import pandas as pd
from datetime import datetime

from utils.permissions import admin_only
from utils.gsheets import read_sheet, append_row
from utils.constants import ASSETS_MASTER_SHEET
from utils.ui import apply_global_ui
from utils.auth import logout

# ─────────────────────────────────────────────
# Global UI + Security
# ─────────────────────────────────────────────
apply_global_ui()
admin_only()
logout()

st.title("🖨️ Assets")

# ─────────────────────────────────────────────
# Load assets
# ─────────────────────────────────────────────
assets_df = read_sheet(ASSETS_MASTER_SHEET)

if not assets_df.empty:
    assets_df.columns = assets_df.columns.str.strip().str.lower()

# ─────────────────────────────────────────────
# Prepare dropdown options
# ─────────────────────────────────────────────
category_options = (
    sorted(assets_df["category"].dropna().unique().tolist())
    if not assets_df.empty and "category" in assets_df.columns
    else []
)

location_options = (
    sorted(assets_df["location"].dropna().unique().tolist())
    if not assets_df.empty and "location" in assets_df.columns
    else []
)

category_options = ["Select"] + category_options + ["Other"]
location_options = ["Select"] + location_options + ["Other"]

# ─────────────────────────────────────────────
# SAFE asset_id generator
# ─────────────────────────────────────────────
def get_next_asset_ids(existing_df: pd.DataFrame, qty: int):
    if existing_df.empty or "asset_id" not in existing_df.columns:
        start = 1
    else:
        valid_ids = existing_df[
            existing_df["asset_id"].astype(str).str.startswith("AST-")
        ].copy()

        if valid_ids.empty:
            start = 1
        else:
            valid_ids["num"] = (
                valid_ids["asset_id"]
                .astype(str)
                .str.replace("AST-", "", regex=False)
                .astype(int)
            )
            start = valid_ids["num"].max() + 1

    return [f"AST-{str(i).zfill(3)}" for i in range(start, start + qty)]

# ─────────────────────────────────────────────
# Asset submission form
# ─────────────────────────────────────────────
with st.form("asset_submission_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        asset_name = st.text_input("Asset Name *")

        category = st.selectbox("Category *", category_options)
        new_category = ""
        if category == "Other":
            new_category = st.text_input("New Category *")

        brand = st.text_input("Brand")

    with col2:
        model = st.text_input("Model")

        location = st.selectbox("Location *", location_options)
        new_location = ""
        if location == "Other":
            new_location = st.text_input("New Location *")

        qty = st.number_input("Quantity *", min_value=1, step=1)

    with col3:
        purchase_date = st.date_input("Purchase Date *")
        warranty_end = st.date_input("Warranty End Date *")
        is_active = st.selectbox("Is Active", [True, False])

    submit = st.form_submit_button("➕ Create Assets")

# ─────────────────────────────────────────────
# Submit handling
# ─────────────────────────────────────────────
if submit:
    final_category = new_category.strip() if category == "Other" else category
    final_location = new_location.strip() if location == "Other" else location

    if not asset_name or not final_category or not final_location:
        st.error("Asset Name, Category, and Location are required")
        st.stop()

    now = datetime.now().isoformat()
    asset_ids = get_next_asset_ids(assets_df, qty)

    for asset_id in asset_ids:
        append_row(
            ASSETS_MASTER_SHEET,
            {
                "asset_id": asset_id,
                "asset_name": asset_name,
                "category": final_category,
                "brand": brand,
                "model": model,
                "purchase_date": purchase_date.isoformat(),
                "warranty_end": warranty_end.isoformat(),
                "location": final_location,
                "is_active": is_active,
                "created_at": now,
                "updated_at": now,
            },
        )

    st.success(f"{qty} asset units created successfully")
    st.rerun()

# ─────────────────────────────────────────────
# Asset inventory view
# ─────────────────────────────────────────────
st.divider()
st.subheader("📋 Asset Inventory (Unit Level)")

if assets_df.empty:
    st.info("No assets found")
else:
    st.dataframe(
        assets_df.sort_values("asset_id"),
        use_container_width=True
    )
