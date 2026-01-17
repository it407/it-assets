# utils/ui.py
import streamlit as st

def apply_global_ui():
    st.markdown(
        """
        <style>

        /* Remove extra top spacing */
        .block-container {
            padding-top: 1rem;
        }

        /* Hide top-right toolbar (GitHub, Fork, Deploy) */
        header [data-testid="stToolbar"] {
            display: none;
        }

        /* Hide bottom-right Share floating button */
        a[href*="share.streamlit"] {
            display: none !important;
        }
        [data-testid="stShareButton"] {
            display: none !important;
        }

        /* Hide footer */
        footer {
            visibility: hidden;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
