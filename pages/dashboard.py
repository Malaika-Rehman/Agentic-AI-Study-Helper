import streamlit as st
from data.app_data import COURSES
from components.sidebar import render_dashboard_sidebar, process_document
from components.helpers import progress_ring


def render_home():
    course_name = st.session_state.selected_course
    course      = COURSES.get(course_name, list(COURSES.values())[0])
    color       = course["color"]

    render_dashboard_sidebar()

    # ── One-time welcome banner (only true right after this user's
    #    very first-ever login, tracked server-side in the users table) ──
    if st.session_state.is_first_login:
        st.markdown(f"""
        <div style='background:#FDF4F0; border:1px solid #F3D9C4; border-radius:12px;
                    padding:14px 18px; margin-bottom:14px; font-size:14px; color:#7A4A2A;'>
          🎉 <b>Welcome, {st.session_state.user_name}!</b> Upload your first document below
          to get started — your AI summary, flashcards, quiz, and study plan will all be
          generated automatically.
        </div>
        """, unsafe_allow_html=True)
        st.session_state.is_first_login = False  # one-time only

    # ── Title Bar ──
    course_list = list(COURSES.keys())
    if st.session_state.selected_course not in course_list:
        st.session_state.selected_course = course_list[0]

    col_title, col_course, col_chat = st.columns([2.8, 2, 1.2])
    with col_title:
        st.markdown("<div class='section-title'>Study Workspace</div>", unsafe_allow_html=True)
        st.markdown("<div class='muted'>Shaheed Benazir Bhutto Women University AI Assistant</div>", unsafe_allow_html=True)
    with col_course:
        # Subject is auto-detected from the uploaded document (see detect_subject
        # in process_document) — no manual selection needed.
        st.markdown(f"""
        <div style='height:100%; display:flex; align-items:center; justify-content:flex-end;'>
          <div style='background:{color}1A; border:1px solid {color}40; color:{color};
                      border-radius:10px; padding:8px 16px; font-size:13px; font-weight:700;
                      white-space:nowrap;'>
            📚 {st.session_state.selected_course}
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col_chat:
        if st.button("🤖 Launch Chat Agent", use_container_width=True, type="primary"):
            st.session_state.screen = "chat"
            st.rerun()

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── No document uploaded yet ──
    if not st.session_state.doc_processed:
        with st.container(border=True, key="dash_upload_container"):
            st.markdown("""
            <div style='text-align:center; padding: 24px 24px 4px;'>
              <div style='font-size:40px; margin-bottom:16px;'>📄</div>
              <div style='font-size:18px; font-weight:700; color:#1A0A0F; margin-bottom:8px;'>
                Upload Your Study Material
              </div>
              <div style='font-size:14px; color:#7A5864; max-width:420px; margin:0 auto 22px;'>
                Add your notes, PDFs, or study files to get started. The AI will
                automatically detect the subject and generate your summary,
                flashcards, quiz, and study plan.
              </div>
            </div>
            """, unsafe_allow_html=True)

            _, col_upl, _ = st.columns([1, 2, 1])
            with col_upl:
                dash_file = st.file_uploader(
                    "Upload study material", type=["pdf", "docx", "pptx", "txt", "md"],
                    label_visibility="collapsed", key="dash_uploader",
                )
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if dash_file and dash_file.name != st.session_state.doc_name:
            process_document(dash_file)
            st.rerun()
        return

    # ── Agent Banner ──
    doc_name = st.session_state.doc_name
    flashcard_count = len(st.session_state.ai_flashcards)
    quiz_count      = len(st.session_state.ai_quiz)

    plan = st.session_state.ai_study_plan
    if plan:
        completed_weeks = sum(1 for _, _, done in plan if done)
        plan_progress   = int((completed_weeks / len(plan)) * 100)
    else:
        plan_progress = 0

    st.markdown(f"""
    <div class="agent-banner">
      <div class="banner-left">
        <span class="pulse-dot"></span>
        <div>
          <div style='font-size:15px; font-weight:700; color:{color}; letter-spacing:0.02em;'>
            PLANNER AGENT ACTIVE
          </div>
          <div style='font-size:13px; color:#7A5864; margin-top:3px'>
            📄 {doc_name} &nbsp;|&nbsp; {flashcard_count} flashcards &nbsp;|&nbsp; {quiz_count} quiz questions
          </div>
        </div>
      </div>
      <div>{progress_ring(plan_progress, color)}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stat Cards ──
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-val">{flashcard_count}</div>
          <div class="stat-lbl">Flashcards Generated</div>
          <div class="prog-bg"><div class="prog-fill" style="width:100%; background:{color}"></div></div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-val">{quiz_count}</div>
          <div class="stat-lbl">Quiz Questions</div>
          <div style='font-size:11px; color:#9E828D; margin-top:10px; font-weight:500;'>Generated from your document</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        plan_count = len(st.session_state.ai_study_plan)
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-val">{plan_progress}%</div>
          <div class="stat-lbl">Study Plan Progress ({plan_count} weeks)</div>
          <div class="prog-bg"><div class="prog-fill" style="width:{plan_progress}%; background:#22C55E"></div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "🃏 Flashcards", "🧪 Quiz", "📅 Study Plan"])

    # ── Tab 1: Summary ──
    with tab1:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        if st.session_state.ai_summary:
            st.markdown(st.session_state.ai_summary)
        else:
            st.info("Upload a document to generate a summary.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 2: Flashcards ──
    with tab2:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        cards = st.session_state.ai_flashcards
        if not cards:
            st.info("Upload a document to generate flashcards.")
        else:
            idx = st.session_state.fc_index % len(cards)
            q, a = cards[idx]

            st.markdown(f"<div style='font-size:12px; color:#7A5864; margin-bottom:12px; font-weight:600;'>Card {idx + 1} of {len(cards)}</div>", unsafe_allow_html=True)

            if not st.session_state.fc_flipped:
                st.markdown(f"<div class='flashcard'><div class='fc-label'>Question</div><div class='fc-text'>{q}</div><div class='fc-hint'>Click Flip to reveal the answer</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='flashcard' style='background:#230810'><div class='fc-label'>Answer</div><div class='fc-text'>{a}</div></div>", unsafe_allow_html=True)

            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            b1, b2, b3 = st.columns([1.5, 1, 1])
            with b1:
                if st.button("👁 Flip Card", use_container_width=True):
                    st.session_state.fc_flipped = not st.session_state.fc_flipped
                    st.rerun()
            with b2:
                if st.button("✓ Got It", use_container_width=True):
                    st.session_state.fc_index  += 1
                    st.session_state.fc_flipped = False
                    st.rerun()
            with b3:
                if st.button("Next →", use_container_width=True):
                    st.session_state.fc_index  += 1
                    st.session_state.fc_flipped = False
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 3: Quiz ──
    with tab3:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        questions = st.session_state.ai_quiz
        if not questions:
            st.info("Upload a document to generate quiz questions.")
        else:
            q_idx              = st.session_state.quiz_index % len(questions)
            q_text, opts, correct = questions[q_idx]
            answered           = st.session_state.quiz_answered

            st.markdown(f"<div style='font-size:12px; color:#7A5864; margin-bottom:10px; font-weight:600;'>Question {q_idx + 1} of {len(questions)}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight:600; font-size:15px; margin-bottom:16px;'>{q_text}</div>", unsafe_allow_html=True)

            for i, opt in enumerate(opts):
                prefix = ["A", "B", "C", "D"][i]
                if answered is not None:
                    if i == correct:
                        st.success(f"{prefix}. {opt}  ✔ Correct")
                    elif i == answered:
                        st.error(f"{prefix}. {opt}  ❌ Wrong")
                    else:
                        st.markdown(f"&nbsp;&nbsp;**{prefix}.** {opt}")
                else:
                    if st.button(f"{prefix}. {opt}", use_container_width=True, key=f"quiz_opt_{i}"):
                        st.session_state.quiz_answered = i
                        st.rerun()

            if answered is not None:
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                if st.button("Next Question →", type="primary"):
                    st.session_state.quiz_index   += 1
                    st.session_state.quiz_answered = None
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 4: Study Plan ──
    with tab4:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        plan = st.session_state.ai_study_plan
        if not plan:
            st.info("Upload a document to generate a study plan.")
        else:
            st.markdown(f"<div style='font-size:15px; font-weight:700; color:{color}; margin-bottom:4px'>Your Personalised Study Plan</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:12.5px; color:#7A5864; margin-bottom:16px;'>Check off each week as you complete it — your progress ring updates automatically.</div>", unsafe_allow_html=True)

            updated = False
            new_plan = []
            for i, (title, desc, done) in enumerate(plan):
                checked = st.checkbox(title, value=done, key=f"week_check_{i}")
                st.markdown(f"<div style='font-size:13px; color:#7A5864; margin-left:28px; margin-top:-8px; margin-bottom:14px;'>{desc}</div>", unsafe_allow_html=True)
                if checked != done:
                    updated = True
                new_plan.append((title, desc, checked))

            if updated:
                from data.database import update_study_plan
                st.session_state.ai_study_plan = new_plan
                update_study_plan(st.session_state.doc_id, [list(p) for p in new_plan])
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)