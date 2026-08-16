import re
import streamlit as st
from data.database import register_user
from components.about_section import render_signup_about


def render_signup():
    col_left, col_right = st.columns([1.15, 1], gap="large")

    with col_left:
        st.markdown("""
        <div class="app-topbar">
          <span class="logo">🎓</span>
          <span class="name">Agentic AI Study Helper</span>
        </div>
        """, unsafe_allow_html=True)

        render_signup_about()

    with col_right:
        st.markdown(
            "<div class='section-title' style='margin-bottom:4px'>Create Account</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<div class='muted' style='margin-bottom:20px'>Fill in your details below</div>",
            unsafe_allow_html=True
        )

        with st.form("signup_form"):
            name = st.text_input(
                "Full Name",
                placeholder="Enter your full name"
            )

            student_id = st.text_input(
                "Student ID",
                placeholder="Enter student ID BC-00(B)U/22"
            )

            email = st.text_input(
                "Email Address",
                placeholder="Enter your email address"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a strong password"
            )

            # Password requirements
            st.markdown("""
            <div class="password-hint">
                <strong>Password requirements:</strong>
                <ul>
                    <li>At least 8 characters</li>
                    <li>At least one uppercase letter</li>
                    <li>At least one lowercase letter</li>
                    <li>At least one number</li>
                    <li>At least one special character</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            confirm = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password"
            )

            submitted = st.form_submit_button(
                "Create Account →",
                use_container_width=True,
                type="primary"
            )

        if submitted:

            # Empty field validation
            if not all([name, student_id, email, password, confirm]):
                st.error("Please fill in all fields.")

            # Password length
            elif len(password) < 8:
                st.error("Password must be at least 8 characters long.")

            # Uppercase
            elif not re.search(r"[A-Z]", password):
                st.error(
                    "Password must contain at least one uppercase letter (A-Z)."
                )

            # Lowercase
            elif not re.search(r"[a-z]", password):
                st.error(
                    "Password must contain at least one lowercase letter (a-z)."
                )

            # Number
            elif not re.search(r"\d", password):
                st.error(
                    "Password must contain at least one number (0-9)."
                )

            # Special character
            elif not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\[\]';`~]", password):
                st.error(
                    "Password must contain at least one special character "
                    "such as ! @ # $ % & *"
                )

            # Confirm password
            elif password != confirm:
                st.error("Passwords do not match.")

            else:
                success, message = register_user(
                    email,
                    password,
                    name,
                    student_id
                )

                if success:
                    st.success("🎉 Account created! Please sign in.")

                    st.session_state.just_registered = True

                    import time
                    time.sleep(1)

                    st.session_state.screen = "login"
                    st.rerun()

                else:
                    st.error(f"❌ {message}")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        if st.button(
            "Already have an account? Sign in →",
            use_container_width=True
        ):
            st.session_state.screen = "login"
            st.rerun()