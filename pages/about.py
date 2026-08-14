import streamlit as st

from components.about_section import render_about_platform
from components.sidebar import render_about_sidebar


def render_about():
    """Render the standalone About screen."""

    # Sidebar
    render_about_sidebar()

    # Main About page
    render_about_platform()

    # Back button
    st.html("""
    <div style="
        max-width:1120px;
        margin:0 auto;
        padding:0 25px;
        box-sizing:border-box;
    ">
    """)

    if st.button(
        "← Back",
        key="about_back_button"
    ):
        st.session_state.screen = st.session_state.get(
            "about_return_screen",
            "login"
        )
        st.rerun()

    st.html("""
    </div>
    """)