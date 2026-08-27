import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from data.data_store import init_state
from styles.style_loader import load_styles
from pages.login import render_auth
from pages.signup import render_signup
from pages.dashboard import render_home
from pages.chat import render_chat
from pages.about import render_about
from pages.onboarding import render_onboarding
from components.sidebar import render_auth_sidebar

# ── Init ──
init_state()

# ── Page config ──
st.set_page_config(
    page_title="Agentic AI Study Helper",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Hide Streamlit's auto multi-page nav ──
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Global styles ──
load_styles()

screen = st.session_state.screen

# ── Sidebar collapse toggle (only on authenticated screens) ──
if screen not in ("onboarding", "login", "signup", "about"):
    if st.session_state.sidebar_collapsed:
        st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            min-width:0!important;max-width:0!important;
            width:0!important;overflow:hidden!important;border-right:none!important;
        }
        </style>""", unsafe_allow_html=True)
        with st.container(key="sidebar_toggle_collapsed"):
            if st.button("»", key="expand_btn", help="Show sidebar"):
                st.session_state.sidebar_collapsed = False
                st.rerun()
    else:
        with st.container(key="sidebar_toggle_expanded"):
            if st.button("«", key="collapse_btn", help="Hide sidebar"):
                st.session_state.sidebar_collapsed = True
                st.rerun()

# ── Router ──
if screen == "onboarding":
    render_onboarding()

elif screen == "login":
    render_auth_sidebar()
    render_auth()

elif screen == "signup":
    render_auth_sidebar()
    render_signup()

elif screen == "home":
    render_home()

elif screen == "chat":
    render_chat()

elif screen == "about":
    render_about()