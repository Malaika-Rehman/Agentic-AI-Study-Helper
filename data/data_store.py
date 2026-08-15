import streamlit as st
from data.database import init_db


def init_state():
    # Init DB tables on first run
    init_db()

    defaults = {
        # Auth
        "screen":           "login",
        "user_name":        "",
        "student_id":       "",
        "user_email":       "",

        # Course
        "selected_course":  "CS301 – Cloud Computing",

        # Current document
        "doc_text":         "",
        "doc_name":         "",
        "doc_id":           None,
        "doc_processed":    False,

        # AI generated outputs
        "ai_summary":       "",
        "ai_flashcards":    [],
        "ai_quiz":          [],
        "ai_study_plan":    [],

        # Flashcard state
        "fc_index":         0,
        "fc_flipped":       False,

        # Quiz state
        "quiz_index":       0,
        "quiz_answered":    None,

        # Chat
        "chat_messages":    [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def clear_current_document():
    """Reset the session back to the empty-dashboard state. The document
    itself stays saved in the database — this only clears what's loaded
    in the current session, so the user can start fresh or upload
    something new without losing anything in Previous Documents."""
    st.session_state.doc_id         = None
    st.session_state.doc_name       = ""
    st.session_state.doc_text       = ""
    st.session_state.doc_processed  = False
    st.session_state.ai_summary     = ""
    st.session_state.ai_flashcards  = []
    st.session_state.ai_quiz        = []
    st.session_state.ai_study_plan  = []
    st.session_state.fc_index       = 0
    st.session_state.fc_flipped     = False
    st.session_state.quiz_index     = 0
    st.session_state.quiz_answered  = None
    st.session_state.chat_messages  = []


def load_document_into_session(doc_id: int, user_email: str):
    """Load a previously saved document + its results into session state."""
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