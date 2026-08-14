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
