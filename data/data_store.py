import streamlit as st
from data.database import (
    init_db,
    is_onboarding_completed,
    validate_session_token,
    get_user_documents,
    update_user_activity,
)
from components.auth_cookies import get_session_token


def init_state():
    # Init DB tables on first run
    init_db()

    initial_screen = "onboarding"

    defaults = {
        # Auth
        "screen":            initial_screen,
        "ob_step":           0,
        "user_name":         "",
        "student_id":        "",
        "user_email":        "",
        "session_token":     "",
        "is_first_login":    False,
        "sidebar_collapsed": False,
        "cookie_action":     None,  # ("set", token) or ("delete", None)

        # Course — starts empty; gets set when user uploads a document
        "selected_course":   "",

        # Current document
        "doc_text":          "",
        "doc_name":          "",
        "doc_id":            None,
        "doc_processed":     False,

        # AI generated outputs
        "ai_summary":        "",
        "ai_flashcards":     [],
        "ai_quiz":           [],
        "ai_study_plan":     [],

        # Flashcard state
        "fc_index":          0,
        "fc_flipped":        False,

        # Quiz state
        "quiz_index":        0,
        "quiz_answered":     None,

        # Chat
        "chat_messages":     [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Check for Persistent Cookie Authentication ──
    if not st.session_state.user_email:
        token = get_session_token()
        if token:
            user = validate_session_token(token)
            if user:
                st.session_state.user_name     = user["name"]
                st.session_state.student_id    = user["student_id"]
                st.session_state.user_email    = user["email"]
                st.session_state.session_token = token
                if st.session_state.screen in ("login", "signup", "onboarding"):
                    st.session_state.screen = "home"

                # Automatically load latest document if available
                if not st.session_state.doc_processed:
                    existing_docs = get_user_documents(user["email"])
                    if existing_docs:
                        loaded = load_document_into_session(existing_docs[0]["id"], user["email"])
                        if loaded:
                            st.session_state.doc_name = existing_docs[0]["filename"]

                update_user_activity(user["email"])
    elif st.session_state.user_email:
        # Periodic activity refresh
        update_user_activity(st.session_state.user_email)


def clear_current_document():
    """Reset the session back to the empty-dashboard state.
    The document stays saved in the database — this only clears
    what is loaded in the current session."""
    st.session_state.doc_id         = None
    st.session_state.doc_name       = ""
    st.session_state.doc_text       = ""
    st.session_state.doc_processed  = False
    st.session_state.selected_course = ""
    st.session_state.ai_summary     = ""
    st.session_state.ai_flashcards  = []
    st.session_state.ai_quiz        = []
    st.session_state.ai_study_plan  = []
    st.session_state.fc_index       = 0
    st.session_state.fc_flipped     = False
    st.session_state.quiz_index     = 0
    st.session_state.quiz_answered  = None
    st.session_state.chat_messages  = []


def load_document_into_session(doc_id: int, user_email: str) -> bool:
    """Load a previously saved document and its results into session state."""
    from data.database import get_document_text, get_results, get_chat_history

    text    = get_document_text(doc_id)
    results = get_results(doc_id)
    history = get_chat_history(user_email, doc_id)

    if not results:
        return False

    st.session_state.doc_id          = doc_id
    st.session_state.doc_text        = text
    st.session_state.selected_course = results["course"]
    st.session_state.ai_summary      = results["summary"]
    st.session_state.ai_flashcards   = [tuple(f) for f in results["flashcards"]]
    st.session_state.ai_quiz         = [tuple(q) for q in results["quiz"]]
    st.session_state.ai_study_plan   = [tuple(p) for p in results["study_plan"]]
    st.session_state.chat_messages   = history
    st.session_state.fc_index        = 0
    st.session_state.fc_flipped      = False
    st.session_state.quiz_index      = 0
    st.session_state.quiz_answered   = None
    st.session_state.doc_processed   = True

    return True