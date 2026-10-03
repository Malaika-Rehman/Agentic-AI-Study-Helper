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

from components.auth_cookies import set_session_cookie, delete_session_cookie
from components.notification_manager import render_push_notification_client

st.write("TEST VERSION: OCTOBER 3 2026")

# ── Init ──
init_state()

# ── Handle any pending cookie synchronization ──
if st.session_state.get("cookie_action"):
    action, act_token = st.session_state.cookie_action
    if action == "set" and act_token:
        set_session_cookie(act_token)
    elif action == "delete":
        delete_session_cookie()
    st.session_state.cookie_action = None

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

# ── Background Push Notification Client (Authenticated Screens) ──
if screen not in ("onboarding", "login", "signup", "about") and st.session_state.get("user_email"):
    render_push_notification_client(st.session_state.user_email)

# ── First-login notification permission overlay ──
if (screen not in ("onboarding", "login", "signup", "about")
        and st.session_state.get("is_first_login")
        and st.session_state.get("user_email")):
    from components.notification_manager import render_first_login_notification_prompt
    render_first_login_notification_prompt(
        st.session_state.user_email,
        st.session_state.user_name,
    )

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