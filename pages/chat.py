import html
import re

import streamlit as st
import streamlit.components.v1 as components

from data.app_data import get_course_info
from data.ai_agents import answer_question
from data.database import save_message
from data.vector_store import retrieve_chunks
from components.sidebar import render_chat_sidebar


# ------------------------------------------------------------
# HTML helpers
# ------------------------------------------------------------

def _to_html(text: str, escape: bool) -> str:
    """
    Convert text to HTML.
    Escape user text to prevent HTML injection.
    Convert new lines to <br>.
    """
    text = str(text)

    if escape:
        text = html.escape(text)

    return text.replace("\r\n", "\n").replace("\n", "<br>")


def _md_to_html(text: str) -> str:
    """
    Convert the AI markdown response to HTML that can be
    displayed inside the AI chat bubble.
    """

    text = str(text).replace("\r\n", "\n")

    try:
        import markdown

        out = markdown.markdown(
            text,
            extensions=[
                "extra",
                "nl2br",
                "sane_lists",
            ],
        )

    except ImportError:
        # Minimal fallback if markdown is not installed
        out = html.escape(text)

        # Bold
        out = re.sub(
            r"\*\*(.+?)\*\*",
            r"<b>\1</b>",
            out,
            flags=re.S,
        )

        # Italic
        out = re.sub(
            r"(?<!\*)\*([^\*]+?)\*(?!\*)",
            r"<i>\1</i>",
            out,
        )

        # Inline code
        out = re.sub(
            r"`([^`]+)`",
            r"<code>\1</code>",
            out,
        )

        out = out.replace("\n", "<br>")

    # Prevent whitespace/newline from turning HTML into
    # an unintended markdown code block.
    out = re.sub(
        r">\s*\n\s*<",
        "><",
        out,
    )

    return out.replace("\n", "&#10;")


# ------------------------------------------------------------
# AI bubble
# ------------------------------------------------------------

def _ai_bubble(content_html: str) -> str:
    return (
        "<div class='chat-row-ai'>"
        "<div class='bubble-wrap'>"
        "<div class='msg-header'>AI Study Agent</div>"
        f"<div class='bubble-ai'>{content_html}</div>"
        "</div>"
        "</div>"
    )


# ------------------------------------------------------------
# User bubble
# ------------------------------------------------------------

def _user_bubble(
    content_html: str,
    student_id: str,
) -> str:
    return (
        "<div class='chat-row-user'>"
        "<div class='bubble-wrap'>"
        f"<div class='msg-header-user'>"
        f"You ({html.escape(str(student_id))})"
        f"</div>"
        f"<div class='bubble-user'>{content_html}</div>"
        "</div>"
        "</div>"
    )


# ------------------------------------------------------------
# Main chat
# ------------------------------------------------------------

def render_chat():

    course_name = st.session_state.get(
        "selected_course",
        "General Study Material",
    )

    color = get_course_info(course_name)["color"]

    # Sidebar
    render_chat_sidebar()

    # ============================================================
    # HEADER
    # ============================================================

    st.markdown(
        "<div class='section-title'>AI Study Chat</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class='muted' style='margin-bottom:12px;'>
            Subject: {html.escape(course_name)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ============================================================
    # MESSAGES
    # ============================================================

    with st.container(key="chat_messages"):

        # --------------------------------------------------------
        # Initial AI message
        # --------------------------------------------------------

        if not st.session_state.chat_messages:

            if st.session_state.doc_processed:

                doc_ctx = (
                    f"I have read "
                    f"<b>{html.escape(str(st.session_state.doc_name))}</b> "
                    f"and I'm ready to answer your questions about "
                    f"<b>{html.escape(course_name)}</b>."
                )

            else:

                doc_ctx = (
                    "No document uploaded yet — upload one from the "
                    "dashboard sidebar first."
                )

            st.markdown(
                _ai_bubble(
                    f"Assalamu Alaikum "
                    f"{html.escape(str(st.session_state.user_name))}! "
                    f"{doc_ctx}"
                ),
                unsafe_allow_html=True,
            )

        # --------------------------------------------------------
        # Chat history
        # --------------------------------------------------------

        for msg in st.session_state.chat_messages:

            if msg["role"] == "user":

                st.markdown(
                    _user_bubble(
                        _to_html(
                            msg["content"],
                            escape=True,
                        ),
                        st.session_state.student_id,
                    ),
                    unsafe_allow_html=True,
                )

            else:

                st.markdown(
                    _ai_bubble(
                        _md_to_html(msg["content"])
                    ),
                    unsafe_allow_html=True,
                )

    # ============================================================
    # AUTO SCROLL
    # ============================================================

    if st.session_state.chat_messages:

        components.html(
            """
            <script>
            const doc = window.parent.document;

            setTimeout(function () {

                const main =
                    doc.querySelector('[data-testid="stMain"]') ||
                    doc.querySelector('section.main');

                if (main) {
                    main.scrollTo({
                        top: main.scrollHeight,
                        behavior: "smooth"
                    });
                }

            }, 100);
            </script>
            """,
            height=0,
        )

    # ============================================================
    # FIXED MESSAGE INPUT
    #
    # IMPORTANT:
    # Keep the input and Send button in horizontal columns.
    # The CSS controls the fixed positioning.
    # ============================================================

    with st.container(key="chat_input_fixed"):

        with st.form(
            "chat_input_form",
            clear_on_submit=True,
            border=False,
        ):

            col_in, col_btn = st.columns(
                [5, 1],
                vertical_alignment="center",
            )

            with col_in:

                query = st.text_input(
                    "Ask",
                    placeholder=(
                        f"Ask anything about {course_name}..."
                    ),
                    label_visibility="collapsed",
                )

            with col_btn:

                sent = st.form_submit_button(
                    "Send ⚡",
                    use_container_width=True,
                )

    # ============================================================
    # SEND MESSAGE
    # ============================================================

    if sent and query.strip():

        # --------------------------------------------------------
        # Document check
        # --------------------------------------------------------

        if not st.session_state.doc_processed:

            st.warning(
                "Please upload a document first from "
                "the dashboard sidebar."
            )

        else:

            # ----------------------------------------------------
            # Save user message
            # ----------------------------------------------------

            save_message(
                st.session_state.user_email,
                st.session_state.doc_id,
                "user",
                query,
            )

            st.session_state.chat_messages.append(
                {
                    "role": "user",
                    "content": query,
                }
            )

            # ----------------------------------------------------
            # Generate AI response
            # ----------------------------------------------------

            try:

                with st.spinner("Thinking..."):

                    context = retrieve_chunks(
                        st.session_state.user_email,
                        st.session_state.doc_id,
                        query,
                        n_results=5,
                    )

                    # ------------------------------------------------
                    # Fallback to document text
                    # ------------------------------------------------

                    if not context:

                        context = (
                            st.session_state.doc_text[:4000]
                        )

                    reply = answer_question(
                        query,
                        context,
                        course_name,
                    )

                # ------------------------------------------------
                # Save assistant response
                # ------------------------------------------------

                save_message(
                    st.session_state.user_email,
                    st.session_state.doc_id,
                    "assistant",
                    reply,
                )

                st.session_state.chat_messages.append(
                    {
                        "role": "assistant",
                        "content": reply,
                    }
                )

                # ------------------------------------------------
                # Refresh chat
                # ------------------------------------------------

                st.rerun()

            except Exception as e:

                st.error(
                    f"❌ Failed to generate response: {str(e)}"
                )