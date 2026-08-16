import streamlit as st
from data.database import login_user, get_user_documents, record_login
from data.data_store import load_document_into_session
from components.about_section import render_login_about


def render_auth():
    col_left, col_right = st.columns([1.15, 1], gap="large")

    with col_left:
        st.markdown("""
        <div class="app-topbar">
          <span class="logo">🎓</span><span class="name">Agentic AI Study Helper</span>
        </div>
        """, unsafe_allow_html=True)
        render_login_about()

    with col_right:
        st.markdown("<div class='section-title' style='margin-bottom:4px'>Welcome</div>",
                    unsafe_allow_html=True)
        st.markdown("<div class='muted' style='margin-bottom:20px'>Enter your credentials to continue</div>",
                    unsafe_allow_html=True)

        with st.form("login_form"):
            email    = st.text_input("Email Address", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

        if submitted:
            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                success, result = login_user(email, password)
                if success:
                    st.session_state.user_name  = result["name"]
                    st.session_state.student_id = result["student_id"]
                    st.session_state.user_email = result["email"]
                    st.session_state.screen     = "home"
                    st.session_state.pop("just_registered", None)

                    # Server-side truth about whether this is this user's
                    # very first login ever — not guessable from the
                    # login page itself, since the app doesn't know who's
                    # logging in until after this point.
                    st.session_state.is_first_login = record_login(result["email"])

                    # If this user already has study material from a
                    # previous session, load the most recent one so the
                    # dashboard shows their content instead of the
                    # empty-state upload card.
                    existing_docs = get_user_documents(result["email"])
                    if existing_docs:
                        loaded = load_document_into_session(existing_docs[0]["id"], result["email"])
                        if loaded:
                            st.session_state.doc_name = existing_docs[0]["filename"]

                    st.rerun()
                else:
                    st.error(f"❌ {result}")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("New here? Create an account →", use_container_width=True):
            st.session_state.screen = "signup"
            st.rerun()