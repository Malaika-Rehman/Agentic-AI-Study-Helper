import streamlit as st
from data.document_processor import extract_text
from data.ai_agents import detect_subject, generate_summary, generate_flashcards, generate_quiz, generate_study_plan
from data.database import save_document, save_results, get_user_documents, delete_document as delete_document_db
from data.vector_store import store_document, delete_document as delete_document_vectors
from data.data_store import load_document_into_session
from components.about_section import render_sidebar_footer


def _section_label(text: str):
    """Small uppercase section heading used throughout the sidebar
    instead of plain st.divider() rules, for a cleaner, app-like feel."""
    st.markdown(f"<div class='sidebar-section-label'>{text}</div>", unsafe_allow_html=True)


def _nav_button(label: str, target_screen: str, current_screen: str):
    """A nav row that visually highlights when it's the active screen."""
    return st.button(
        label, use_container_width=True,
        type="primary" if current_screen == target_screen else "secondary",
    )


@st.dialog("Delete Study Material")
def _confirm_delete_dialog(doc_id: int, filename: str):
    """A real modal popup (like a Flutter AlertDialog) — clicking the
    trash icon opens this instead of deleting immediately. Nothing is
    removed unless the user explicitly confirms here."""
    st.markdown(f"""
    <div style='font-size:14px; color:#4A3A40; line-height:1.6;'>
      Are you sure you want to delete <b>{filename}</b>?
    </div>
    <div style='background:#FEF2F2; border:1px solid #FECACA; border-radius:10px;
                padding:11px 14px; margin-top:14px; font-size:12.5px; color:#991B1B;
                display:flex; gap:8px; align-items:flex-start;'>
      <span style='font-size:14px;'>⚠️</span>
      <span>This action cannot be undone. The document, its generated summary,
      flashcards, quiz, study plan, and chat history will be permanently removed.</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    col_cancel, col_delete = st.columns(2)
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
    with col_delete:
        with st.container(key="danger_delete_btn"):
            if st.button("🗑  Delete Permanently", use_container_width=True, type="primary"):
                delete_document_db(st.session_state.user_email, doc_id)
                delete_document_vectors(st.session_state.user_email, doc_id)
                if st.session_state.doc_id == doc_id:
                    st.session_state.doc_id        = None
                    st.session_state.doc_name      = ""
                    st.session_state.doc_text      = ""
                    st.session_state.doc_processed = False
                    st.session_state.ai_summary    = ""
                    st.session_state.ai_flashcards = []
                    st.session_state.ai_quiz       = []
                    st.session_state.ai_study_plan = []
                    st.session_state.chat_messages = []
                st.rerun()


def process_document(file):
    """Extract → detect → run all 5 agents → save to SQLite + ChromaDB.

    Shared between the sidebar uploader and the dashboard's empty-state
    upload card so both trigger the exact same pipeline.
    """
    with st.spinner("📄 Reading document..."):
        text, error = extract_text(file)

    if error:
        st.error(f"❌ {error}")
        return
    if len(text.strip()) < 50:
        st.error("❌ File has too little text to process.")
        return

    # Step 2 — Detect subject
    with st.spinner("🔍 Detecting subject..."):
        course = detect_subject(text)
        st.session_state.selected_course = course
    st.success(f"📚 Detected: **{course}**")

    # Step 3 — Save document to SQLite
    with st.spinner("💾 Saving document..."):
        doc_id = save_document(st.session_state.user_email, file.name, course, text)
        st.session_state.doc_id   = doc_id
        st.session_state.doc_name = file.name
        st.session_state.doc_text = text

    # Step 4 — Store in ChromaDB for RAG
    with st.spinner("🧠 Indexing for semantic search..."):
        store_document(st.session_state.user_email, doc_id, text)

    # Step 5 — Run all agents
    with st.spinner("📝 Generating summary..."):
        summary = generate_summary(text, course)
        st.session_state.ai_summary = summary

    with st.spinner("🃏 Creating flashcards..."):
        flashcards = generate_flashcards(text, course)
        st.session_state.ai_flashcards = flashcards
        st.session_state.fc_index      = 0
        st.session_state.fc_flipped    = False

    with st.spinner("🧪 Building quiz..."):
        quiz = generate_quiz(text, course)
        st.session_state.ai_quiz      = quiz
        st.session_state.quiz_index   = 0
        st.session_state.quiz_answered = None

    with st.spinner("📅 Creating study plan..."):
        study_plan = generate_study_plan(text, course)
        st.session_state.ai_study_plan = study_plan

    # Step 6 — Save all results to SQLite
    with st.spinner("💾 Saving results..."):
        save_results(
            st.session_state.user_email, doc_id, course,
            summary,
            [list(f) for f in flashcards],
            [list(q) for q in quiz],
            [list(p) for p in study_plan],
        )
        st.session_state.chat_messages = []
        st.session_state.doc_processed = True

    st.success("✅ Done! Check the tabs below.")


def render_auth_sidebar():
    with st.sidebar:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        _section_label("Support")
        if st.button("ℹ️  About", use_container_width=True):
            st.session_state.about_return_screen = st.session_state.screen
            st.session_state.screen = "about"
            st.rerun()
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        render_sidebar_footer()


def render_about_sidebar():
    with st.sidebar:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        _section_label("Navigation")
        if st.button("← Back", use_container_width=True):
            st.session_state.screen = st.session_state.get("about_return_screen", "login")
            st.rerun()
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        render_sidebar_footer()


def render_dashboard_sidebar():
    with st.sidebar:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        screen = st.session_state.screen

        _section_label("Navigation")
        if _nav_button("🏠  Dashboard", "home", screen):
            st.session_state.screen = "home"
            st.rerun()
        if _nav_button("💬  AI Chat", "chat", screen):
            st.session_state.screen = "chat"
            st.rerun()

        _section_label("Upload Study Material")
        st.caption("PDF, DOCX, PPTX, or TXT")
        uploaded_file = st.file_uploader(
            "Upload", type=["pdf", "docx", "pptx", "txt", "md"],
            label_visibility="collapsed",
        )
        if uploaded_file and uploaded_file.name != st.session_state.doc_name:
            process_document(uploaded_file)
            st.rerun()

        if st.session_state.doc_processed and st.session_state.doc_name:
            st.markdown(f"""
            <div style='background:#F0FDF4; border:1px solid #86EFAC; border-radius:10px;
                        padding:10px 12px; font-size:12px; color:#166534; margin-top:8px;'>
              ✅ <b>Active:</b> {st.session_state.doc_name}
            </div>""", unsafe_allow_html=True)

        # ── Past Documents ──
        _section_label("Previous Documents")
        docs = get_user_documents(st.session_state.user_email)
        if not docs:
            st.caption("No documents yet.")
        else:
            for doc in docs:
                col_btn, col_date, col_del = st.columns([3, 1.5, 0.7])
                label = doc["filename"][:20] + "…" if len(doc["filename"]) > 20 else doc["filename"]
                date  = doc["uploaded_at"][:10]
                with col_btn:
                    if st.button(f"📄 {label}", key=f"doc_{doc['id']}", use_container_width=True):
                        if load_document_into_session(doc["id"], st.session_state.user_email):
                            st.session_state.doc_name = doc["filename"]
                            st.rerun()
                with col_date:
                    st.markdown(f"<div style='font-size:10px; color:#9E828D; padding-top:8px;'>{date}</div>",
                                unsafe_allow_html=True)
                with col_del:
                    with st.container(key=f"del_trigger_{doc['id']}"):
                        if st.button("🗑", key=f"del_{doc['id']}", help="Delete this document permanently"):
                            _confirm_delete_dialog(doc["id"], doc["filename"])

        # ── User Card ──
        _section_label("Account")
        initials = "".join(w[0] for w in st.session_state.user_name.split()[:2]).upper()
        st.markdown(f"""
        <div style='background:#FDF9FA; border:1px solid #EADCE0; border-radius:12px;
                    padding:12px; display:flex; align-items:center; gap:10px'>
          <div style='width:34px; height:34px; border-radius:50%; background:#802B45;
                      color:white; display:flex; align-items:center; justify-content:center;
                      font-weight:700; font-size:12px; flex-shrink:0'>{initials}</div>
          <div>
            <div style='font-size:13px; font-weight:600; color:#1A0A0F;'>{st.session_state.user_name}</div>
            <div style='font-size:11px; color:#7A5864;'>{st.session_state.student_id}</div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Log Out", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def render_chat_sidebar():
    with st.sidebar:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        _section_label("Navigation")

        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.screen = "home"
            st.rerun()

        if st.session_state.doc_processed and st.session_state.doc_name:
            _section_label("Active Context")
            st.markdown(f"""
            <div style='background:#F0FDF4; border:1px solid #86EFAC; border-radius:10px;
                        padding:10px 12px; font-size:12px; color:#166534;'>
              ✅ <b>Context:</b> {st.session_state.doc_name}
            </div>""", unsafe_allow_html=True)

        _section_label("Session")
        if st.button("🗑 Clear Chat History", use_container_width=True):
            from data.database import clear_chat_history
            clear_chat_history(st.session_state.user_email, st.session_state.doc_id)
            st.session_state.chat_messages = []
            st.rerun() 