import streamlit as st


def render_login_about():
    """Renders the 'About' section for the Login page."""
    st.markdown("""
    <div class="auth-left">
      <div class="auth-badge">✦ Agentic AI Platform</div>
      <h1>Study Smarter,<br/><em>Not Harder</em></h1>
      <p>Your AI-powered study companion for SBBWU. Upload documents, get instant
         summaries, flashcards, quizzes and study plans — all powered by 5 AI agents.</p>
      <div class="auth-feature">
        <span style="font-size:20px; margin-top:2px;">📄</span>
        <div>
          <div class="auth-feature-title">RAG Document Engine</div>
          <div class="auth-feature-sub">Deep semantic search across your uploaded docs</div>
        </div>
      </div>
      <div class="auth-feature">
        <span style="font-size:20px; margin-top:2px;">🧠</span>
        <div>
          <div class="auth-feature-title">5 AI Agents</div>
          <div class="auth-feature-sub">Controller, Summary, Flashcard, Quiz & Planner</div>
        </div>
      </div>
      <div class="auth-feature">
        <span style="font-size:20px; margin-top:2px;">💾</span>
        <div>
          <div class="auth-feature-title">Persistent Storage</div>
          <div class="auth-feature-sub">Your results & chat history saved automatically</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_signup_about():
    """Renders the 'About' section for the Signup page."""
    st.markdown("""
    <div class="auth-left">
      <div class="auth-badge">✦ Create Your Account</div>
      <h1>Join Your<br/><em>AI Cohort</em></h1>
      <p>Register to get your personal AI study workspace. Your documents, results
         and chat history will be saved and accessible every time you log in.</p>
      <div class="auth-feature">
        <span style="font-size:20px; margin-top:2px;">🔐</span>
        <div>
          <div class="auth-feature-title">Secure Authentication</div>
          <div class="auth-feature-sub">Passwords hashed — never stored in plain text</div>
        </div>
      </div>
      <div class="auth-feature">
        <span style="font-size:20px; margin-top:2px;">📊</span>
        <div>
          <div class="auth-feature-title">Personal Dashboard</div>
          <div class="auth-feature-sub">Your documents, results & progress — all saved</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_about_platform():
    """Renders the 'About This Platform' sections shown in the sidebar."""
    st.markdown("""
    <div style='padding:4px 6px;'>
      <div style='font-size:12px; font-weight:700; color:#7A5864; text-transform:uppercase;
                  letter-spacing:0.05em; margin-bottom:14px;'>About This Platform</div>
      <div style='display:flex; gap:10px; margin-bottom:16px;'>
        <span style='font-size:18px;'>🤖</span>
        <div>
          <div style='font-size:13px; font-weight:700; color:#1A0A0F;'>5 AI Agents</div>
          <div style='font-size:11.5px; color:#7A5864; line-height:1.4;'>
            Controller, Summary, Flashcard, Quiz &amp; Planner</div>
        </div>
      </div>
      <div style='display:flex; gap:10px; margin-bottom:16px;'>
        <span style='font-size:18px;'>📄</span>
        <div>
          <div style='font-size:13px; font-weight:700; color:#1A0A0F;'>Any Document</div>
          <div style='font-size:11.5px; color:#7A5864; line-height:1.4;'>
            PDF, DOCX, PPTX or TXT — subject auto-detected</div>
        </div>
      </div>
      <div style='display:flex; gap:10px; margin-bottom:16px;'>
        <span style='font-size:18px;'>💾</span>
        <div>
          <div style='font-size:13px; font-weight:700; color:#1A0A0F;'>Everything Saved</div>
          <div style='font-size:11.5px; color:#7A5864; line-height:1.4;'>
            Results &amp; chat history persist across sessions</div>
        </div>
      </div>
      <div style='display:flex; gap:10px; margin-bottom:16px;'>
        <span style='font-size:18px;'>🎯</span>
        <div>
          <div style='font-size:13px; font-weight:700; color:#1A0A0F;'>3 Core Subjects</div>
          <div style='font-size:11.5px; color:#7A5864; line-height:1.4;'>
            Cloud Computing, Computer Vision, Algorithms</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_footer():
    """Renders a production-ready footer for the sidebar."""
    st.markdown("""
    <div style='text-align:center; padding:8px 6px;'>
      <div style='font-size:11.5px; color:#9E828D; line-height:1.6;'>
        <b style='color:#802B45;'>Agentic AI Study Helper</b><br/>
        <span>Production Release &bull; v1.0.0</span><br/>
        <span style='font-size:10px;'>&copy; 2026 SBBWU Study Companion. All rights reserved.</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

