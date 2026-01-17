# utils/navigation.py

import streamlit as st
from utils.constants import ROLE_ADMIN, ROLE_MANAGER, ROLE_USER

def apply_role_based_navigation():
    user = st.session_state.get("user")
    if not user:
        return

    role = user["role"]

    # 👑 Admin → see everything
    if role == ROLE_ADMIN:
        return

    # 👔 Manager → dashboards only (HARD-CODED)
    if role == ROLE_MANAGER:
        st.markdown(
            """
            <style>
            [data-testid="stSidebarNav"] li {
                display: none;
            }

            [data-testid="stSidebarNav"] a[aria-label="Dashboard"] {
                display: block !important;
            }

            [data-testid="stSidebarNav"] a[aria-label="User Asset Assignments"] {
                display: block !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        return

    # 👤 User → My Assets only
    if role == ROLE_USER:
        st.markdown(
            """
            <style>
            [data-testid="stSidebarNav"] li {
                display: none;
            }

            [data-testid="stSidebarNav"] a[aria-label="My Assets"] {
                display: block !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
