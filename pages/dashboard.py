import streamlit as st

from data.app_data import get_course_info
from components.sidebar import (
    render_dashboard_sidebar,
    process_document,
)


def render_stat_card(value, label, progress=None, caption=None):
    """
    Render a statistics card using native Streamlit components.
    This avoids raw HTML rendering issues on Streamlit Cloud.
    """
    with st.container(border=True):
        st.metric(
            label=label,
            value=value,
        )

        if progress is not None:
            st.progress(
                max(0.0, min(1.0, progress)),
                text=None,
            )

        if caption:
            st.caption(caption)


def render_home():
    # ---------------------------------------------------------
    # Course / theme information
    # ---------------------------------------------------------
    course_name = st.session_state.get(
        "selected_course",
        "General Study Material",
    )

    course_info = get_course_info(course_name)
    color = course_info.get("color", "#802B45")

    # ---------------------------------------------------------
    # Sidebar
    # ---------------------------------------------------------
    render_dashboard_sidebar()

    # ---------------------------------------------------------
    # Page Header
    # ---------------------------------------------------------
    header_col1, header_col2 = st.columns([4, 1])

    with header_col1:
        st.markdown(
            """
            <div class="page-title">
                Study Workspace
            </div>
            <div class="page-subtitle">
                Your AI-powered academic study environment
            </div>
            """,
            unsafe_allow_html=True,
        )

    with header_col2:
        st.markdown(
            f"""
            <div class="course-badge"
                 style="
                    background:{color}15;
                    color:{color};
                    border:1px solid {color}35;
                 ">
                {course_name}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Launch Chat Button
    # ---------------------------------------------------------
    if st.button(
        "Launch Chat Agent",
        use_container_width=False,
        type="primary",
        key="launch_chat_agent",
    ):
        st.session_state.current_page = "chat"
        st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # No document uploaded
    # ---------------------------------------------------------
    if not st.session_state.get("doc_processed", False):

        with st.container(
            border=True,
            key="dash_upload_container",
        ):
            st.markdown(
                """
                <div class="upload-title">
                    Upload your study material
                </div>

                <div class="upload-subtitle">
                    Upload a PDF, DOCX, PPTX, TXT, or supported study file.
                    The AI agents will analyze it and prepare your study material.
                </div>
                """,
                unsafe_allow_html=True,
            )

            dash_file = st.file_uploader(
                "Choose your study material",
                type=[
                    "pdf",
                    "docx",
                    "pptx",
                    "txt",
                    "rtf",
                ],
                key="dashboard_file_uploader",
            )

            if dash_file is not None:

                current_doc = st.session_state.get(
                    "doc_name",
                    "",
                )

                if dash_file.name != current_doc:

                    success = process_document(dash_file)

                    if success:
                        st.rerun()

        return

    # ---------------------------------------------------------
    # Document information
    # ---------------------------------------------------------
    doc_name = st.session_state.get(
        "doc_name",
        "Study Material",
    )

    flashcard_count = len(
        st.session_state.get(
            "ai_flashcards",
            [],
        )
    )

    quiz_count = len(
        st.session_state.get(
            "ai_quiz",
            [],
        )
    )

    # ---------------------------------------------------------
    # Study plan progress
    # ---------------------------------------------------------
    study_plan = st.session_state.get(
        "ai_study_plan",
        [],
    )

    total_plan_items = len(study_plan)

    completed_plan_items = 0

    for item in study_plan:
        if isinstance(item, dict):
            if item.get("completed", False):
                completed_plan_items += 1

        elif isinstance(item, bool):
            if item:
                completed_plan_items += 1

    if total_plan_items > 0:
        plan_progress = (
            completed_plan_items / total_plan_items
        )
    else:
        plan_progress = 0.0

    # ---------------------------------------------------------
    # Agent Status Banner
    # ---------------------------------------------------------
    st.markdown(
        f"""
        <div class="agent-banner"
             style="
                border-left:4px solid {color};
             ">

            <div class="agent-banner-title">
                AI Study Workspace Ready
            </div>

            <div class="agent-banner-text">
                <strong>{doc_name}</strong> has been processed.
                Your summary, flashcards, quiz, and study plan
                are ready.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------
    st.markdown(
        """
        <div class="section-heading">
            Study Overview
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    # Flashcards
    with c1:
        render_stat_card(
            value=flashcard_count,
            label="Flashcards Generated",
            progress=1.0 if flashcard_count > 0 else 0.0,
            caption="AI-generated revision cards",
        )

    # Quiz
    with c2:
        render_stat_card(
            value=quiz_count,
            label="Quiz Questions",
            progress=1.0 if quiz_count > 0 else 0.0,
            caption="Questions generated from your material",
        )

    # Study Plan
    with c3:
        render_stat_card(
            value=f"{completed_plan_items}/{total_plan_items}",
            label="Study Plan Progress",
            progress=plan_progress,
            caption=(
                f"{int(plan_progress * 100)}% completed"
                if total_plan_items > 0
                else "No study plan available"
            ),
        )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Main Study Tabs
    # ---------------------------------------------------------
    tab_summary, tab_flashcards, tab_quiz, tab_plan = st.tabs(
        [
            "Summary",
            "Flashcards",
            "Quiz",
            "Study Plan",
        ]
    )

    # =========================================================
    # SUMMARY
    # =========================================================
    with tab_summary:

        summary = st.session_state.get(
            "ai_summary",
            "",
        )

        if summary:

            with st.container(
                border=True,
                key="summary_container",
            ):
                st.markdown(
                    "### AI Summary"
                )

                st.markdown(summary)

        else:

            st.info(
                "No summary has been generated yet."
            )

    # =========================================================
    # FLASHCARDS
    # =========================================================
    with tab_flashcards:

        flashcards = st.session_state.get(
            "ai_flashcards",
            [],
        )

        if flashcards:

            for index, card in enumerate(flashcards):

                if not isinstance(card, dict):
                    continue

                question = card.get(
                    "question",
                    card.get(
                        "front",
                        "",
                    ),
                )

                answer = card.get(
                    "answer",
                    card.get(
                        "back",
                        "",
                    ),
                )

                with st.container(
                    border=True,
                    key=f"flashcard_{index}",
                ):

                    st.markdown(
                        f"**Card {index + 1}**"
                    )

                    if question:
                        st.markdown(
                            f"**Question:** {question}"
                        )

                    if answer:
                        with st.expander(
                            "Show Answer",
                            expanded=False,
                        ):
                            st.markdown(answer)

        else:

            st.info(
                "No flashcards have been generated yet."
            )

    # =========================================================
    # QUIZ
    # =========================================================
    with tab_quiz:

        quiz = st.session_state.get(
            "ai_quiz",
            [],
        )

        if quiz:

            for index, question_data in enumerate(quiz):

                if not isinstance(question_data, dict):
                    continue

                question = question_data.get(
                    "question",
                    "",
                )

                options = question_data.get(
                    "options",
                    [],
                )

                answer = question_data.get(
                    "answer",
                    question_data.get(
                        "correct_answer",
                        "",
                    ),
                )

                with st.container(
                    border=True,
                    key=f"quiz_{index}",
                ):

                    st.markdown(
                        f"**Question {index + 1}**"
                    )

                    if question:
                        st.markdown(question)

                    if options:

                        st.radio(
                            "Select your answer:",
                            options,
                            key=f"quiz_answer_{index}",
                        )

                    if answer:

                        with st.expander(
                            "Show Correct Answer",
                            expanded=False,
                        ):
                            st.markdown(
                                f"**Correct Answer:** {answer}"
                            )

        else:

            st.info(
                "No quiz questions have been generated yet."
            )

    # =========================================================
    # STUDY PLAN
    # =========================================================
    with tab_plan:

        if study_plan:

            st.markdown(
                "### Personal Study Plan"
            )

            for index, item in enumerate(study_plan):

                if isinstance(item, dict):

                    title = item.get(
                        "title",
                        item.get(
                            "task",
                            item.get(
                                "topic",
                                f"Study Task {index + 1}",
                            ),
                        ),
                    )

                    description = item.get(
                        "description",
                        item.get(
                            "details",
                            "",
                        ),
                    )

                    completed = item.get(
                        "completed",
                        False,
                    )

                    with st.container(
                        border=True,
                        key=f"study_plan_{index}",
                    ):

                        col1, col2 = st.columns(
                            [5, 1]
                        )

                        with col1:

                            st.markdown(
                                f"**{title}**"
                            )

                            if description:
                                st.caption(
                                    description
                                )

                        with col2:

                            st.checkbox(
                                "Done",
                                value=completed,
                                key=f"plan_done_{index}",
                            )

                else:

                    with st.container(
                        border=True,
                        key=f"study_plan_{index}",
                    ):

                        st.write(
                            str(item)
                        )

        else:

            st.info(
                "No study plan has been generated yet."
            )


# -------------------------------------------------------------
# Streamlit entry point
# -------------------------------------------------------------
if __name__ == "__main__":
    render_home()