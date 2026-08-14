import streamlit as st
from data.app_data import COURSES
from data.ai_agents import answer_question
from data.database import save_message
from data.vector_store import retrieve_chunks
from components.sidebar import render_chat_sidebar


def render_chat():
    course_name = st.session_state.selected_course
    color       = COURSES.get(course_name, list(COURSES.values())[0])["color"]

    render_chat_sidebar()

    st.markdown("<div class='section-title'>AI Study Chat</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='muted' style='margin-bottom:20px;'>Course: {course_name}</div>",
                unsafe_allow_html=True)

    # ── Chat messages ──
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    if not st.session_state.chat_messages:
        doc_ctx = (f"I have read <b>{st.session_state.doc_name}</b> and I'm ready to answer questions."
                   if st.session_state.doc_processed
                   else "No document uploaded yet — upload one from the dashboard sidebar first.")
        st.markdown(f"""
        <div class='chat-row-ai'>
          <div class='bubble-wrap'>
            <div class='msg-header'>AI Study Agent</div>
            <div class='bubble-ai'>Assalamu Alaikum {st.session_state.user_name}! {doc_ctx}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class='chat-row-user'>
              <div class='bubble-wrap'>
                <div class='msg-header-user'>You ({st.session_state.student_id})</div>
                <div class='bubble-user'>{msg['content']}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='chat-row-ai'>
              <div class='bubble-wrap'>
                <div class='msg-header'>AI Study Agent</div>
                <div class='bubble-ai'>{msg['content']}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Input ──
    with st.form("chat_input_form", clear_on_submit=True):
        col_in, col_btn = st.columns([5, 1])
        with col_in:
            query = st.text_input("Ask", placeholder="Ask anything about your document...",
                                  label_visibility="collapsed")
        with col_btn:
            sent = st.form_submit_button("Send ⚡", use_container_width=True)

    if sent and query.strip():
        if not st.session_state.doc_processed:
            st.warning("Please upload a document first from the dashboard sidebar.")
        else:
            # Save user message to DB
            save_message(st.session_state.user_email, st.session_state.doc_id, "user", query)
            st.session_state.chat_messages.append({"role": "user", "content": query})

            with st.spinner("Thinking..."):
                # RAG — retrieve relevant chunks from ChromaDB
                context = retrieve_chunks(
                    st.session_state.user_email,
                    st.session_state.doc_id,
                    query,
                    n_results=5
                )
                # Fallback to full doc text if ChromaDB returns nothing
                if not context:
                    context = st.session_state.doc_text[:4000]

                reply = answer_question(query, context, course_name)

            # Save AI reply to DB
            save_message(st.session_state.user_email, st.session_state.doc_id, "assistant", reply)
            st.session_state.chat_messages.append({"role": "assistant", "content": reply})
            st.rerun()
