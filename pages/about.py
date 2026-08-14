import streamlit as st
from components.about_section import render_about_platform
from components.sidebar import render_about_sidebar


def render_about():
    """Standalone, independently navigable About screen.

    Reuses the existing 'About This Platform' content/design that used to
    live inline in the auth sidebar (components/about_section.render_about_platform),
    just presented as its own page now.
    """
    render_about_sidebar()

    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown("""
        <div class='auth-card'>
          <div class='auth-card-logo'>🎓</div>
          <div class='auth-card-title'>Agentic AI Study Helper</div>
          <div class='auth-card-sub'>About This Platform</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        render_about_platform()

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True):
            st.session_state.screen = st.session_state.get("about_return_screen", "login")
            st.rerun()
