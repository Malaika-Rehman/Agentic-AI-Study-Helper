import streamlit as st
from data.database import set_onboarding_completed


def render_onboarding():

    st.markdown("""
    <style>
    header, [data-testid="stHeader"], .stAppHeader {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        visibility: hidden !important;
    }

    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    .st-key-sidebar_toggle_expanded,
    .st-key-sidebar_toggle_collapsed { display: none !important; }

    html, body {
        min-height: 100vh !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
    }
    .stApp {
        min-height: 100vh !important;
        background: white !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
    }
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .stMainBlockContainer {
        min-height: 100vh !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
    }

    .main .block-container,
    [data-testid="stMainBlockContainer"],
    .stMainBlockContainer,
    .block-container {
        padding: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
        min-height: 100vh !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
    }

    /* Make the column row fill height on desktop */
    [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        min-height: 100vh !important;
        align-items: stretch !important;
        flex-wrap: nowrap !important;
    }
    /* Each column fills height on desktop */
    [data-testid="stColumn"] {
        padding: 0 !important;
        min-height: 100vh !important;
    }

    /* ── Right column inner layout ── */
    [data-testid="stColumn"]:last-child > div:first-child {
        min-height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        padding: 36px 52px !important;
        background: white !important;
        border-left: 1px solid #EADCE0 !important;
        gap: 0 !important;
        box-sizing: border-box !important;
    }
    /* Streamlit wrappers inside right col */
    [data-testid="stColumn"]:last-child [data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        height: 100% !important;
        gap: 0 !important;
    }

    /* ── Button styles ── */
    .st-key-gs_signup > div > button {
        background: #802B45 !important;
        color: white !important;
        border: none !important;
        border-radius: 13px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        height: 52px !important;
        box-shadow: 0 4px 20px rgba(128,43,69,0.28) !important;
    }
    .st-key-gs_signup > div > button:hover {
        background: #6B2339 !important;
        box-shadow: 0 8px 28px rgba(128,43,69,0.40) !important;
        transform: translateY(-2px) !important;
    }
    .st-key-gs_login > div > button {
        background: white !important;
        border: 1.5px solid #EADCE0 !important;
        color: #802B45 !important;
        border-radius: 13px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        height: 48px !important;
    }
    .st-key-gs_login > div > button:hover {
        background: #FBF0F3 !important;
        border-color: #802B45 !important;
    }
    .st-key-gs_signup {
        margin: 0 0 16px 0 !important;
        margin-bottom: 16px !important;
    }
    .st-key-gs_signup > div {
        margin: 0 0 16px 0 !important;
        margin-bottom: 16px !important;
    }
    .st-key-gs_login { margin: 0 !important; }
    .st-key-gs_login > div { margin: 0 !important; }

    /* ── Mobile Responsive / Scrollable Styles ── */
    @media (max-width: 860px) {
        html, body, .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        .stMainBlockContainer,
        .main .block-container,
        [data-testid="stMainBlockContainer"],
        .block-container {
            height: auto !important;
            min-height: 100vh !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }

        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            flex-wrap: wrap !important;
            min-height: auto !important;
            height: auto !important;
        }

        [data-testid="stColumn"] {
            width: 100% !important;
            min-width: 100% !important;
            min-height: auto !important;
            height: auto !important;
            overflow: visible !important;
        }

        [data-testid="stColumn"]:last-child > div:first-child {
            min-height: auto !important;
            height: auto !important;
            padding: 32px 20px !important;
            border-left: none !important;
            border-top: 1px solid #EADCE0 !important;
        }

        [data-testid="stColumn"]:last-child [data-testid="stVerticalBlock"] {
            height: auto !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([5, 6])

    # ══════════════════════════════
    # LEFT — full-height maroon panel
    # ══════════════════════════════
    with col_left:
        st.html("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@400;500;600;700;800&display=swap');

        .gs-left {
            background: linear-gradient(150deg, #802B45 0%, #4E1828 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 44px 44px;
            position: relative;
            overflow: hidden;
            font-family: 'DM Sans', sans-serif;
            box-sizing: border-box;
        }
        .gs-ring {
            position: absolute; border-radius: 50%;
            border: 1.5px solid rgba(255,255,255,0.07);
            pointer-events: none;
        }
        .gs-r1 { width:440px;height:440px;top:-160px;right:-120px; }
        .gs-r2 { width:260px;height:260px;bottom:-90px;left:-70px;border-color:rgba(255,255,255,0.05); }

        .gs-logo {
            display: flex; align-items: center; gap: 10px;
            position: relative; z-index: 2;
            margin-bottom: 24px;
        }
        .gs-logo-ico  { font-size: 26px; }
        .gs-logo-name {
            font-family: 'DM Serif Display', serif;
            font-size: 17px; color: rgba(255,255,255,0.92);
        }
        .gs-main { position: relative; z-index: 2; }
        .gs-kicker {
            display: inline-block;
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.18);
            color: rgba(255,255,255,0.70);
            font-size: 11px; font-weight: 700;
            letter-spacing: 0.1em; text-transform: uppercase;
            padding: 5px 13px; border-radius: 100px;
            margin-bottom: 18px;
        }
        .gs-headline {
            font-family: 'DM Serif Display', serif;
            font-size: 44px; line-height: 1.12;
            color: white; margin: 0 0 18px;
            letter-spacing: -0.5px;
        }
        .gs-headline em { font-style: italic; color: #FFB3C6; }
        .gs-desc {
            font-size: 15px;
            color: rgba(255,255,255,0.68);
            line-height: 1.75; max-width: 360px;
        }
        .gs-stats {
            display: flex; gap: 10px; margin-top: 24px;
            position: relative; z-index: 2;
        }
        .gs-stat {
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 12px; padding: 12px 18px; text-align: center;
        }
        .gs-stat-n {
            font-family: 'DM Serif Display', serif;
            font-size: 26px; color: white; line-height: 1; margin-bottom: 3px;
        }
        .gs-stat-l { font-size: 11px; color: rgba(255,255,255,0.48); font-weight: 600; }

        @media (max-width: 860px) {
            .gs-left {
                min-height: auto !important;
                height: auto !important;
                padding: 32px 20px !important;
            }
            .gs-headline {
                font-size: 32px !important;
            }
            .gs-desc {
                font-size: 13.5px !important;
                max-width: 100% !important;
            }
            .gs-stats {
                flex-wrap: wrap !important;
            }
            .gs-stat {
                flex: 1 1 calc(33.333% - 8px) !important;
                padding: 10px 12px !important;
            }
        }
        </style>

        <div class="gs-left">
          <div class="gs-ring gs-r1"></div>
          <div class="gs-ring gs-r2"></div>

          <div class="gs-logo">
            <span class="gs-logo-ico">🎓</span>
            <span class="gs-logo-name">Agentic AI Study Helper</span>
          </div>

          <div class="gs-main">
            <span class="gs-kicker">AI-Powered Learning</span>
            <h1 class="gs-headline">
              Your notes.<br>Your AI.<br><em>Your success.</em>
            </h1>
            <p class="gs-desc">
              Upload any study file and the AI instantly creates
              your summary, flashcards, quiz, and study plan.
              No tech skills needed. Works for every subject.
            </p>
            <div class="gs-stats">
              <div class="gs-stat">
                <div class="gs-stat-n">8</div>
                <div class="gs-stat-l">Flashcards</div>
              </div>
              <div class="gs-stat">
                <div class="gs-stat-n">5</div>
                <div class="gs-stat-l">Quiz Questions</div>
              </div>
              <div class="gs-stat">
                <div class="gs-stat-n">∞</div>
                <div class="gs-stat-l">Subjects</div>
              </div>
            </div>
          </div>
        </div>
        """)

    # ══════════════════════════════
    # RIGHT — steps + CTA buttons
    # ══════════════════════════════
    with col_right:

        # Badge + heading — static HTML (no fixed height)
        st.html("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@400;500;600;700;800&display=swap');

        .gs-badge {
            display: inline-block;
            background: #FBE8EE; color: #802B45;
            font-family: 'DM Sans', sans-serif;
            font-size: 11px; font-weight: 800;
            letter-spacing: 0.09em; text-transform: uppercase;
            padding: 5px 14px; border-radius: 100px;
            margin-bottom: 16px;
        }
        .gs-rtitle {
            font-family: 'DM Serif Display', serif;
            font-size: 28px; color: #1A0A0F;
            margin: 0 0 6px; letter-spacing: -0.3px;
        }
        .gs-rsub {
            font-family: 'DM Sans', sans-serif;
            font-size: 14px; color: #7A5864;
            line-height: 1.65; margin: 0 0 24px;
        }
        .gs-step {
            display: flex; align-items: center; gap: 14px;
            padding: 14px 16px;
            background: #FDF7F8;
            border: 1px solid #EADCE0;
            border-radius: 14px;
            margin-bottom: 10px;
            font-family: 'DM Sans', sans-serif;
            cursor: default;
        }
        .gs-step:last-child { margin-bottom: 0; }
        .gs-step-ico {
            width: 46px; height: 46px; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 22px; flex-shrink: 0;
        }
        .s-pink  { background: #FBE8EE; }
        .s-blue  { background: #EFF6FF; }
        .s-green { background: #F0FDF4; }
        .gs-step-label {
            font-size: 14px; font-weight: 700; color: #1A0A0F; margin-bottom: 2px;
        }
        .gs-step-note {
            font-size: 12.5px; color: #7A5864;
        }
        .gs-step-num {
            margin-left: auto; width: 24px; height: 24px;
            border-radius: 50%; background: #FBE8EE;
            color: #802B45; font-size: 11px; font-weight: 800;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
        }
        .gs-divider {
            display: flex; align-items: center; gap: 10px;
            margin: 22px 0 16px;
        }
        .gs-divider-line { flex: 1; height: 1px; background: #EADCE0; }
        .gs-divider-text {
            font-family: 'DM Sans', sans-serif;
            font-size: 11px; font-weight: 700;
            color: #9E828D; letter-spacing: 0.08em;
            text-transform: uppercase; white-space: nowrap;
        }
        </style>

        <span class="gs-badge">Get Started — It's Free</span>
        <h2 class="gs-rtitle">How it works</h2>
        <p class="gs-rsub">Three simple steps. No setup. No tech knowledge needed.</p>

        <div class="gs-step">
          <div class="gs-step-ico s-pink">📄</div>
          <div>
            <div class="gs-step-label">Upload your study file</div>
            <div class="gs-step-note">PDF, Word doc, PowerPoint, or any text file</div>
          </div>
          <div class="gs-step-num">1</div>
        </div>

        <div class="gs-step">
          <div class="gs-step-ico s-blue">🤖</div>
          <div>
            <div class="gs-step-label">AI builds your study kit</div>
            <div class="gs-step-note">Summary, flashcards, quiz &amp; study plan — automatically</div>
          </div>
          <div class="gs-step-num">2</div>
        </div>

        <div class="gs-step">
          <div class="gs-step-ico s-green">🎯</div>
          <div>
            <div class="gs-step-label">Study smart &amp; ace your exams</div>
            <div class="gs-step-note">Chat with your notes like a personal AI tutor</div>
          </div>
          <div class="gs-step-num">3</div>
        </div>

        <div class="gs-divider">
          <span class="gs-divider-line"></span>
          <span class="gs-divider-text">Create your free account below</span>
          <span class="gs-divider-line"></span>
        </div>
        """)

        # ── Buttons — real Streamlit widgets, always visible ──
        if st.button("🚀  Get Started",
                     key="gs_signup",
                     use_container_width=True,
                     type="primary"):
            set_onboarding_completed()
            st.session_state.screen = "signup"
            st.rerun()

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        if st.button("I already have an account  →",
                     key="gs_login",
                     use_container_width=True):
            set_onboarding_completed()
            st.session_state.screen = "login"
            st.rerun()