"""
Persistent Authentication Cookie Helper.
Manages setting, reading, and clearing secure session cookies across Streamlit reruns
and browser restarts.
"""
import streamlit as st
import streamlit.components.v1 as components

COOKIE_NAME = "study_helper_session"
DEFAULT_MAX_AGE_DAYS = 30


def get_session_token() -> str | None:
    """
    Read the session token cookie from the incoming HTTP request.
    Streamlit 1.58+ provides native access via `st.context.cookies`.
    """
    try:
        if hasattr(st, "context") and hasattr(st.context, "cookies"):
            cookies = st.context.cookies
            if cookies and COOKIE_NAME in cookies:
                token = cookies.get(COOKIE_NAME)
                if token and isinstance(token, str) and len(token.strip()) > 10:
                    return token.strip()
    except Exception:
        pass
    return None


def set_session_cookie(token: str, days_valid: int = DEFAULT_MAX_AGE_DAYS):
    """
    Inject lightweight JavaScript to set the persistent authentication cookie
    in the user's browser.
    """
    if not token:
        return

    max_age_seconds = days_valid * 86400
    js_code = f"""
    <script>
    (function() {{
        var cookieName = "{COOKIE_NAME}";
        var token = "{token}";
        var maxAge = {max_age_seconds};
        var isSecure = window.location.protocol === "https:";
        var cookieStr = cookieName + "=" + encodeURIComponent(token) +
                        "; path=/; max-age=" + maxAge +
                        "; SameSite=Lax" + (isSecure ? "; Secure" : "");

        try {{
            document.cookie = cookieStr;
        }} catch(e) {{}}

        try {{
            if (window.parent && window.parent.document) {{
                window.parent.document.cookie = cookieStr;
            }}
        }} catch(e) {{}}
    }})();
    </script>
    """
    components.html(js_code, height=0, width=0)


def delete_session_cookie():
    """
    Inject JavaScript to delete the session cookie on user logout.
    """
    js_code = f"""
    <script>
    (function() {{
        var cookieName = "{COOKIE_NAME}";
        var expireStr = cookieName + "=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax";

        try {{
            document.cookie = expireStr;
        }} catch(e) {{}}

        try {{
            if (window.parent && window.parent.document) {{
                window.parent.document.cookie = expireStr;
            }}
        }} catch(e) {{}}
    }})();
    </script>
    """
    components.html(js_code, height=0, width=0)
