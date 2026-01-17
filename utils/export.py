# utils/export.py

import streamlit as st
import pandas as pd

def export_csv(df: pd.DataFrame, filename: str):
    if df.empty:
        st.warning("No data to export")
        return

    csv = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )
