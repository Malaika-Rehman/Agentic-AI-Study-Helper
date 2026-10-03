import streamlit as st
from data.app_data import get_course_info
from components.sidebar import render_dashboard_sidebar, process_document


def render_home():
    course_name = st.session_state.get(
        "selected_course",
        "General Study Material",
    )

    course = get_course_info(course_name)
    color = course["color"]

    render_dashboard_sidebar()

    # =========================================================
    # TITLE BAR
    # =========================================================

    col_title, col_course, col_chat = st.columns(
        [2.8, 1.8, 1.4],
        vertical_alignment="center",
    )

    with col_title:
        st.markdown(
            "<div class='section-title'>Study Workspace</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='muted'>"
            "Your AI-powered study workspace"
            "</div>",
            unsafe_allow_html=True,
        )

    with col_course:
        st.markdown(
            f"""
            <div class="course-badge-wrap">
                <div class="course-badge" title="{course_name}">
                    💻 {course_name}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_chat:
        if st.button(
            "🤖 Launch Chat Agent",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.screen = "chat"
            st.rerun()

    st.markdown(
        "<div class='spacer-small'></div>",
        unsafe_allow_html=True,
    )

    # =========================================================
    # EMPTY STATE / UPLOAD
    # =========================================================

    if not st.session_state.doc_processed:

        with st.container(
            border=True,
            key="dash_upload_container",
        ):

            st.html("""
            <div class="upload-intro">
                <div class="upload-icon">📄</div>
                <div class="upload-title">Upload Your Study Material</div>
                <div class="upload-description">
                    Upload any subject PDF, DOCX, PPTX, or TXT file.
                    The AI will automatically detect the subject and
                    generate your summary, flashcards, quiz, and
                    personalised study plan.
                </div>
            </div>
            """)

            _, col_upl, _ = st.columns([1, 2, 1])

            with col_upl:
                dash_file = st.file_uploader(
                    "Upload study material",
                    type=[
                        "pdf",
                        "docx",
                        "pptx",
                        "txt",
                        "md",
                    ],
                    label_visibility="collapsed",
                    key="dash_uploader",
                )

            st.markdown(
                "<div class='spacer-tiny'></div>",
                unsafe_allow_html=True,
            )

        if (
            dash_file
            and dash_file.name != st.session_state.doc_name
        ):
            success = process_document(dash_file)

            if success:
                st.rerun()

        return

    # =========================================================
    # DOCUMENT INFORMATION
    # =========================================================

    doc_name = st.session_state.doc_name

    flashcard_count = len(
        st.session_state.ai_flashcards
    )

    quiz_count = len(
        st.session_state.ai_quiz
    )

    plan = st.session_state.ai_study_plan

    if plan:
        completed_weeks = sum(
            1
            for _, _, done in plan
            if done
        )

        plan_progress = int(
            (completed_weeks / len(plan)) * 100
        )
    else:
        plan_progress = 0

    plan_count = len(plan)

    # =========================================================
    # PLANNER AGENT STATUS
    #
    # IMPORTANT:
    # No HTML is used for the banner content.
    # =========================================================

    with st.container(
        border=True,
        key="agent_status_container",
    ):

        banner_col1, banner_col2 = st.columns(
            [5, 1],
            vertical_alignment="center",
        )

        with banner_col1:
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:14px;">
                    <div class="pulse-dot"></div>
                    <div>
                        <div class="agent-title" style="margin-bottom:3px;">
                            PLANNER AGENT ACTIVE
                        </div>
                        <div style="font-size:12.5px; color:#64748B;">
                            📄 {doc_name} &nbsp;|&nbsp; {flashcard_count} flashcards &nbsp;|&nbsp; {quiz_count} quiz questions
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with banner_col2:
            _circ = 2 * 3.14159 * 26  # ≈ 163.36
            _offset = _circ * (1 - plan_progress / 100)
            st.markdown(
                f"""
                <div class="progress-ring-wrap">
                    <svg viewBox="0 0 64 64" width="58" height="58">
                        <circle cx="32" cy="32" r="26"
                                fill="none" stroke="#E2E8F0" stroke-width="4.5"/>
                        <circle cx="32" cy="32" r="26"
                                fill="none" stroke="#1E3A8A" stroke-width="4.5"
                                stroke-linecap="round"
                                stroke-dasharray="{_circ:.2f}"
                                stroke-dashoffset="{_offset:.2f}"
                                transform="rotate(-90 32 32)"/>
                    </svg>
                    <div class="progress-ring-label">{plan_progress}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        "<div class='spacer-medium'></div>",
        unsafe_allow_html=True,
    )

    # =========================================================
    # STATISTICS
    # =========================================================

    c1, c2, c3 = st.columns(3)

    # ---------------------------------------------------------
    # Flashcards
    # ---------------------------------------------------------

    with c1:
        with st.container(
            border=True,
            key="stat_flashcards",
        ):
            st.markdown(
                f"""
                <div class="stat-val">
                    {flashcard_count}
                </div>
                <div class="stat-lbl">
                    Flashcards Generated
                </div>
                <div class="prog-bg" style="margin-top:14px;">
                    <div class="prog-fill" style="width:100%; background:#1E3A8A;"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ---------------------------------------------------------
    # Quiz
    # ---------------------------------------------------------

    with c2:
        with st.container(
            border=True,
            key="stat_quiz_questions",
        ):
            st.markdown(
                f"""
                <div class="stat-val">
                    {quiz_count}
                </div>
                <div class="stat-lbl">
                    Quiz Questions
                </div>
                <div class="stat-sub">
                    Generated from your document
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ---------------------------------------------------------
    # Study Plan
    # ---------------------------------------------------------

    with c3:
        with st.container(
            border=True,
            key="stat_study_progress",
        ):
            st.markdown(
                f"""
                <div class="stat-val">
                    {plan_progress}%
                </div>
                <div class="stat-lbl">
                    Study Plan Progress ({plan_count} weeks)
                </div>
                <div class="prog-bg" style="margin-top:14px;">
                    <div class="prog-fill" style="width:{plan_progress}%; background:#22C55E;"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        "<div class='spacer-medium'></div>",
        unsafe_allow_html=True,
    )

    # =========================================================
    # TABS
    # =========================================================

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📋 Summary",
            "🎴 Flashcards",
            "🧪 Quiz",
            "📅 Study Plan",
        ]
    )

    # =========================================================
    # SUMMARY
    # =========================================================

    with tab1:

        with st.container(
            border=True,
            key="summary_content_container",
        ):

            if st.session_state.ai_summary:

                st.markdown(
                    st.session_state.ai_summary
                )

            else:

                st.info(
                    "Upload a document to generate a summary."
                )

    # =========================================================
    # FLASHCARDS
    # =========================================================

    with tab2:

        with st.container(
            border=True,
            key="flashcards_content_container",
        ):

            cards = st.session_state.ai_flashcards

            if not cards:

                st.info(
                    "Upload a document to generate flashcards."
                )

            else:

                idx = (
                    st.session_state.fc_index
                    % len(cards)
                )

                q, a = cards[idx]

                # Card counter
                st.caption(
                    f"Card {idx + 1} of {len(cards)}"
                )

                # -------------------------------------------------
                # Question / Answer card
                #
                # The content is now rendered using Streamlit
                # markdown instead of nested HTML.
                # -------------------------------------------------

                if not st.session_state.fc_flipped:

                    with st.container(
                        border=True,
                        key="flashcard_question",
                    ):

                        st.markdown(
                            "##### QUESTION"
                        )

                        st.markdown(
                            q
                        )

                        st.caption(
                            "Click Flip to reveal the answer"
                        )

                else:

                    with st.container(
                        border=True,
                        key="flashcard_answer",
                    ):

                        st.markdown(
                            "##### ANSWER"
                        )

                        st.markdown(
                            a
                        )

                st.markdown(
                    "<div class='spacer-small'></div>",
                    unsafe_allow_html=True,
                )

                # Buttons
                b1, b2, b3 = st.columns(
                    [1.5, 1, 1]
                )

                with b1:

                    if st.button(
                        "👁 Flip Card",
                        use_container_width=True,
                        key="flip_card_button",
                    ):

                        st.session_state.fc_flipped = (
                            not st.session_state.fc_flipped
                        )

                        st.rerun()

                with b2:

                    if st.button(
                        "✓ Got It",
                        use_container_width=True,
                        key="got_it_button",
                    ):

                        st.session_state.fc_index += 1
                        st.session_state.fc_flipped = False

                        st.rerun()

                with b3:

                    if st.button(
                        "Next →",
                        use_container_width=True,
                        key="next_card_button",
                    ):

                        st.session_state.fc_index += 1
                        st.session_state.fc_flipped = False

                        st.rerun()

    # =========================================================
    # QUIZ
    # =========================================================

    with tab3:

        with st.container(
            border=True,
            key="quiz_content_container",
        ):

            questions = st.session_state.ai_quiz

            if not questions:

                st.info(
                    "Upload a document to generate quiz questions."
                )

            else:

                q_idx = (
                    st.session_state.quiz_index
                    % len(questions)
                )

                q_text, opts, correct = questions[q_idx]

                answered = (
                    st.session_state.quiz_answered
                )

                st.caption(
                    f"Question {q_idx + 1} "
                    f"of {len(questions)}"
                )

                st.markdown(
                    f"**{q_text}**"
                )

                for i, opt in enumerate(opts):

                    prefix = [
                        "A",
                        "B",
                        "C",
                        "D",
                    ][i]

                    if answered is not None:

                        if i == correct:

                            st.success(
                                f"{prefix}. {opt}  ✔ Correct"
                            )

                        elif i == answered:

                            st.error(
                                f"{prefix}. {opt}  ❌ Wrong"
                            )

                        else:

                            st.markdown(
                                f"&nbsp;&nbsp;"
                                f"**{prefix}.** {opt}"
                            )

                    else:

                        if st.button(
                            f"{prefix}. {opt}",
                            use_container_width=True,
                            key=f"quiz_opt_{i}",
                        ):

                            st.session_state.quiz_answered = i

                            st.rerun()

                if answered is not None:

                    st.markdown(
                        "<div class='spacer-small'></div>",
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "Next Question →",
                        type="primary",
                        key="next_question_button",
                    ):

                        st.session_state.quiz_index += 1

                        st.session_state.quiz_answered = None

                        st.rerun()

    # =========================================================
    # STUDY PLAN
    # =========================================================

    with tab4:

        with st.container(
            border=True,
            key="study_plan_content_container",
        ):

            plan = st.session_state.ai_study_plan

            if not plan:

                st.info(
                    "Upload a document to generate a study plan."
                )

            else:

                st.markdown(
                    "<div style='font-family:\"DM Serif Display\",serif; font-size:22px; color:#1A0A0F; margin-bottom:4px; font-weight:700;'>Your Personalised Study Plan</div>",
                    unsafe_allow_html=True,
                )

                st.caption(
                    "Check off each week as you complete it — "
                    "your progress ring updates automatically."
                )

                updated = False
                new_plan = []

                for i, (title, desc, done) in enumerate(plan):

                    checked = st.checkbox(
                        title,
                        value=done,
                        key=f"week_check_{i}",
                    )

                    st.caption(desc)

                    if checked != done:
                        updated = True

                    new_plan.append(
                        (
                            title,
                            desc,
                            checked,
                        )
                    )

                if updated:

                    from data.database import (
                        update_study_plan,
                        update_user_activity,
                    )

                    st.session_state.ai_study_plan = new_plan

                    update_study_plan(
                        st.session_state.doc_id,
                        [
                            list(p)
                            for p in new_plan
                        ],
                    )

                    update_user_activity(
                        st.session_state.user_email
                    )

                    st.rerun()