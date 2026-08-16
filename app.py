import streamlit as st
from dotenv import load_dotenv
load_dotenv()  # Load GROQ_API_KEY from .env

from data.data_store import init_state
from styles.style_loader import load_styles
from pages.login import render_auth
from pages.signup import render_signup
from pages.dashboard import render_home
from pages.chat import render_chat
from pages.about import render_about
from components.sidebar import render_auth_sidebar

# ── Init Session State ──
init_state()
screen = st.session_state.screen

# ── Page Config ──
st.set_page_config(
    page_title="Agentic AI Study Helper",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Hide Streamlit's auto multi-page nav sidebar ──
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Load Global Styles ──
load_styles()

# ── Sidebar Show/Hide (custom toggle, mirrors Claude's own UI) ──
# One persistent button, always fixed to the same corner — right where
# the sidebar's top-right edge sits when open. It just flips between
# « (collapse) and » (expand) and slides to the left edge when the
# sidebar is hidden, rather than being two separate buttons in two
# different places.
if st.session_state.sidebar_collapsed:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        min-width: 0px !important;
        max-width: 0px !important;
        width: 0px !important;
        overflow: hidden !important;
        border-right: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
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
if screen == "login":
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