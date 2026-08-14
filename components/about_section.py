import streamlit as st


# ============================================================
# LOGIN ABOUT
# ============================================================

def render_login_about():
    """Render the About panel on the login page."""

    st.html("""
    <style>
        .login-about {
            width: 100%;
            padding: 10px 5px;
            box-sizing: border-box;
        }

        .login-about-badge {
            display: inline-block;
            padding: 7px 13px;
            border-radius: 30px;
            background: rgba(128, 43, 69, 0.10);
            color: #802B45;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.08em;
            margin-bottom: 18px;
        }

        .login-about-title {
            margin: 0;
            color: #1A0A0F;
            font-size: 40px;
            line-height: 1.08;
            font-weight: 800;
            letter-spacing: -0.03em;
        }

        .login-about-title span {
            color: #802B45;
        }

        .login-about-description {
            margin-top: 18px;
            margin-bottom: 28px;
            color: #705963;
            font-size: 14px;
            line-height: 1.7;
            max-width: 520px;
        }

        .login-about-feature {
            display: flex;
            gap: 14px;
            align-items: flex-start;
            margin-bottom: 20px;
        }

        .login-about-icon {
            width: 42px;
            height: 42px;
            min-width: 42px;
            border-radius: 12px;
            background: #F8EEF1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }

        .login-about-feature-title {
            color: #241117;
            font-size: 13px;
            font-weight: 800;
            margin-bottom: 4px;
        }

        .login-about-feature-text {
            color: #806A72;
            font-size: 11px;
            line-height: 1.5;
        }

        .login-about-stat-row {
            display: flex;
            gap: 12px;
            margin-top: 28px;
        }

        .login-about-stat {
            padding: 13px 17px;
            border-radius: 14px;
            background: #FBF7F8;
            border: 1px solid #EEE3E7;
        }

        .login-about-stat-number {
            color: #802B45;
            font-size: 18px;
            font-weight: 800;
        }

        .login-about-stat-label {
            color: #806A72;
            font-size: 9px;
            margin-top: 2px;
        }
    </style>

    <div class="login-about">

        <div class="login-about-badge">
            ✦ AGENTIC AI STUDY PLATFORM
        </div>

        <div class="login-about-title">
            Study Smarter.<br>
            <span>Learn Better.</span>
        </div>

        <div class="login-about-description">
            An intelligent study workspace that transforms your own
            documents into summaries, flashcards, quizzes, study plans
            and AI-powered learning assistance.
        </div>


        <div class="login-about-feature">

            <div class="login-about-icon">
                🤖
            </div>

            <div>
                <div class="login-about-feature-title">
                    Agentic AI
                </div>

                <div class="login-about-feature-text">
                    Five specialized AI agents work together to handle
                    different learning tasks.
                </div>
            </div>

        </div>


        <div class="login-about-feature">

            <div class="login-about-icon">
                📚
            </div>

            <div>
                <div class="login-about-feature-title">
                    Learn From Your Documents
                </div>

                <div class="login-about-feature-text">
                    Upload PDF, DOCX, PPTX or TXT files and turn them
                    into useful study resources.
                </div>
            </div>

        </div>


        <div class="login-about-feature">

            <div class="login-about-icon">
                🧠
            </div>

            <div>
                <div class="login-about-feature-title">
                    Personalized Learning
                </div>

                <div class="login-about-feature-text">
                    Generate learning resources based on your subjects,
                    documents and study goals.
                </div>
            </div>

        </div>


        <div class="login-about-stat-row">

            <div class="login-about-stat">
                <div class="login-about-stat-number">
                    5
                </div>

                <div class="login-about-stat-label">
                    AI AGENTS
                </div>
            </div>


            <div class="login-about-stat">
                <div class="login-about-stat-number">
                    4+
                </div>

                <div class="login-about-stat-label">
                    FILE TYPES
                </div>
            </div>


            <div class="login-about-stat">
                <div class="login-about-stat-number">
                    AI
                </div>

                <div class="login-about-stat-label">
                    POWERED
                </div>
            </div>

        </div>

    </div>
    """)


# ============================================================
# SIGNUP ABOUT
# ============================================================

def render_signup_about():
    """Render the About panel on the signup page."""

    st.html("""
    <style>
        .signup-about {
            width: 100%;
            padding: 10px 5px;
            box-sizing: border-box;
        }

        .signup-about-badge {
            display: inline-block;
            padding: 7px 13px;
            border-radius: 30px;
            background: rgba(128, 43, 69, 0.10);
            color: #802B45;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.08em;
            margin-bottom: 18px;
        }

        .signup-about-title {
            margin: 0;
            color: #1A0A0F;
            font-size: 40px;
            line-height: 1.08;
            font-weight: 800;
            letter-spacing: -0.03em;
        }

        .signup-about-title span {
            color: #802B45;
        }

        .signup-about-description {
            margin-top: 18px;
            margin-bottom: 28px;
            color: #705963;
            font-size: 14px;
            line-height: 1.7;
            max-width: 520px;
        }

        .signup-about-feature {
            display: flex;
            gap: 14px;
            align-items: flex-start;
            margin-bottom: 20px;
        }

        .signup-about-icon {
            width: 42px;
            height: 42px;
            min-width: 42px;
            border-radius: 12px;
            background: #F8EEF1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }

        .signup-about-feature-title {
            color: #241117;
            font-size: 13px;
            font-weight: 800;
            margin-bottom: 4px;
        }

        .signup-about-feature-text {
            color: #806A72;
            font-size: 11px;
            line-height: 1.5;
        }

        .signup-about-note {
            margin-top: 28px;
            padding: 15px 17px;
            background: #FBF7F8;
            border: 1px solid #EEE3E7;
            border-radius: 14px;
            color: #806A72;
            font-size: 11px;
            line-height: 1.55;
        }

        .signup-about-note strong {
            color: #802B45;
        }
    </style>

    <div class="signup-about">

        <div class="signup-about-badge">
            ✦ YOUR PERSONAL AI STUDY SPACE
        </div>

        <div class="signup-about-title">
            Build Your<br>
            <span>Smarter Workflow.</span>
        </div>

        <div class="signup-about-description">
            Create your account and get a dedicated study workspace
            where your documents, generated resources and learning
            activity can stay organized.
        </div>


        <div class="signup-about-feature">

            <div class="signup-about-icon">
                🔐
            </div>

            <div>
                <div class="signup-about-feature-title">
                    Secure Authentication
                </div>

                <div class="signup-about-feature-text">
                    Your account credentials are protected using secure
                    password hashing.
                </div>
            </div>

        </div>


        <div class="signup-about-feature">

            <div class="signup-about-icon">
                🗂️
            </div>

            <div>
                <div class="signup-about-feature-title">
                    Personal Workspace
                </div>

                <div class="signup-about-feature-text">
                    Keep your study material and generated resources
                    organized around your account.
                </div>
            </div>

        </div>


        <div class="signup-about-feature">

            <div class="signup-about-icon">
                ⚡
            </div>

            <div>
                <div class="signup-about-feature-title">
                    AI-Powered Productivity
                </div>

                <div class="signup-about-feature-text">
                    Spend less time preparing study material and more
                    time actually learning.
                </div>
            </div>

        </div>


        <div class="signup-about-note">
            <strong>One workspace.</strong>
            Your study material, AI-generated resources and learning
            workflow in one place.
        </div>

    </div>
    """)


# ============================================================
# STANDALONE ABOUT PAGE
# ============================================================

def render_about_platform():
    """Render the complete standalone About page."""

    st.html("""
    <style>

        .platform-about {
            max-width: 1120px;
            margin: 0 auto;
            padding: 15px 25px 50px 25px;
            box-sizing: border-box;
        }


        /* HERO */

        .platform-hero {
            padding: 48px;
            border-radius: 28px;
            background:
                linear-gradient(
                    135deg,
                    rgba(128, 43, 69, 0.12),
                    rgba(255, 255, 255, 0.98)
                );
            border: 1px solid rgba(128, 43, 69, 0.14);
            position: relative;
            overflow: hidden;
            margin-bottom: 35px;
        }

        .platform-hero::after {
            content: "";
            position: absolute;
            width: 280px;
            height: 280px;
            right: -100px;
            top: -110px;
            border-radius: 50%;
            background: rgba(128, 43, 69, 0.07);
        }

        .platform-badge {
            display: inline-block;
            padding: 7px 14px;
            background: rgba(128, 43, 69, 0.09);
            border-radius: 30px;
            color: #802B45;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.1em;
            margin-bottom: 17px;
        }

        .platform-title {
            color: #1A0A0F;
            font-size: 44px;
            line-height: 1.08;
            font-weight: 800;
            letter-spacing: -0.04em;
        }

        .platform-title span {
            color: #802B45;
        }

        .platform-description {
            max-width: 780px;
            color: #705963;
            font-size: 14px;
            line-height: 1.75;
            margin-top: 18px;
        }


        /* SECTION */

        .platform-section {
            margin-top: 35px;
        }

        .platform-section-title {
            color: #1A0A0F;
            font-size: 23px;
            font-weight: 800;
            margin-bottom: 7px;
        }

        .platform-section-subtitle {
            color: #806A72;
            font-size: 12px;
            line-height: 1.6;
            margin-bottom: 18px;
        }


        /* FEATURE CARDS */

        .platform-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
        }

        .platform-card {
            background: #FFFFFF;
            border: 1px solid #EDE3E6;
            border-radius: 18px;
            padding: 22px;
            min-height: 145px;
            box-sizing: border-box;
        }

        .platform-icon {
            width: 43px;
            height: 43px;
            border-radius: 12px;
            background: #F8EEF1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            margin-bottom: 14px;
        }

        .platform-card-title {
            color: #241117;
            font-size: 14px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .platform-card-text {
            color: #806A72;
            font-size: 11.5px;
            line-height: 1.55;
        }


        /* AGENTS */

        .agent-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
        }

        .agent {
            background: #FFFFFF;
            border: 1px solid #EDE3E6;
            border-radius: 17px;
            padding: 20px 13px;
            text-align: center;
        }

        .agent-number {
            color: #A48790;
            font-size: 9px;
            font-weight: 800;
            letter-spacing: 0.1em;
        }

        .agent-icon {
            font-size: 25px;
            margin: 10px 0;
        }

        .agent-name {
            color: #241117;
            font-size: 12px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .agent-text {
            color: #806A72;
            font-size: 10px;
            line-height: 1.45;
        }


        /* WORKFLOW */

        .workflow-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }

        .workflow {
            background: #FBF8F9;
            border: 1px solid #EEE4E7;
            border-radius: 17px;
            padding: 20px 16px;
        }

        .workflow-number {
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #802B45;
            border-radius: 50%;
            color: white;
            font-size: 11px;
            font-weight: 800;
            margin-bottom: 12px;
        }

        .workflow-title {
            color: #241117;
            font-size: 13px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .workflow-text {
            color: #806A72;
            font-size: 10.5px;
            line-height: 1.5;
        }


        /* TECHNOLOGY */

        .technology {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .technology-pill {
            padding: 8px 13px;
            border-radius: 30px;
            background: #F8EEF1;
            border: 1px solid #EAD9DE;
            color: #6F3046;
            font-size: 10.5px;
            font-weight: 700;
        }


        /* BOTTOM */

        .platform-footer {
            margin-top: 40px;
            padding: 28px 30px;
            border-radius: 22px;
            background: #241117;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
        }

        .platform-footer-title {
            color: white;
            font-size: 17px;
            font-weight: 800;
            margin-bottom: 5px;
        }

        .platform-footer-text {
            color: #CDBBC1;
            font-size: 11px;
            line-height: 1.5;
        }

        .platform-footer-version {
            color: #E7D9DE;
            font-size: 10px;
            text-align: right;
            line-height: 1.6;
        }


        /* RESPONSIVE */

        @media (max-width: 900px) {

            .platform-grid {
                grid-template-columns: 1fr 1fr;
            }

            .agent-grid {
                grid-template-columns: repeat(3, 1fr);
            }

            .workflow-grid {
                grid-template-columns: 1fr 1fr;
            }

            .platform-title {
                font-size: 36px;
            }
        }


        @media (max-width: 600px) {

            .platform-about {
                padding: 10px 12px 35px 12px;
            }

            .platform-hero {
                padding: 32px 25px;
            }

            .platform-title {
                font-size: 31px;
            }

            .platform-grid,
            .agent-grid,
            .workflow-grid {
                grid-template-columns: 1fr;
            }

            .platform-footer {
                flex-direction: column;
                align-items: flex-start;
            }

            .platform-footer-version {
                text-align: left;
            }
        }

    </style>


    <div class="platform-about">


        <!-- HERO -->

        <div class="platform-hero">

            <div class="platform-badge">
                ✦ AGENTIC AI STUDY PLATFORM
            </div>

            <div class="platform-title">
                Your Study Material.<br>
                <span>Smarter with AI.</span>
            </div>

            <div class="platform-description">
                Agentic AI Study Helper is an intelligent learning platform
                designed to transform ordinary study material into
                personalized learning resources. Upload your documents,
                let specialized AI agents process them, and turn your
                material into summaries, flashcards, quizzes, study plans
                and AI-assisted learning experiences.
            </div>

        </div>


        <!-- FEATURES -->

        <div class="platform-section">

            <div class="platform-section-title">
                Everything You Need to Study Smarter
            </div>

            <div class="platform-section-subtitle">
                A study workspace built around your own academic material.
            </div>


            <div class="platform-grid">


                <div class="platform-card">

                    <div class="platform-icon">
                        📄
                    </div>

                    <div class="platform-card-title">
                        Document Intelligence
                    </div>

                    <div class="platform-card-text">
                        Upload PDF, DOCX, PPTX or TXT files and make your
                        study material available for AI-powered processing.
                    </div>

                </div>


                <div class="platform-card">

                    <div class="platform-icon">
                        🔎
                    </div>

                    <div class="platform-card-title">
                        RAG-Based Retrieval
                    </div>

                    <div class="platform-card-text">
                        Retrieve relevant information from uploaded
                        documents before generating learning resources.
                    </div>

                </div>


                <div class="platform-card">

                    <div class="platform-icon">
                        🤖
                    </div>

                    <div class="platform-card-title">
                        Agentic AI
                    </div>

                    <div class="platform-card-text">
                        Specialized agents handle different learning
                        tasks through a coordinated AI workflow.
                    </div>

                </div>


                <div class="platform-card">

                    <div class="platform-icon">
                        📝
                    </div>

                    <div class="platform-card-title">
                        Smart Summaries
                    </div>

                    <div class="platform-card-text">
                        Convert lengthy academic material into concise,
                        structured summaries.
                    </div>

                </div>


                <div class="platform-card">

                    <div class="platform-icon">
                        🎴
                    </div>

                    <div class="platform-card-title">
                        Flashcards
                    </div>

                    <div class="platform-card-text">
                        Turn important concepts into quick revision
                        flashcards for efficient practice.
                    </div>

                </div>


                <div class="platform-card">

                    <div class="platform-icon">
                        ❓
                    </div>

                    <div class="platform-card-title">
                        AI Quizzes
                    </div>

                    <div class="platform-card-text">
                        Generate questions from your material to test
                        understanding and identify knowledge gaps.
                    </div>

                </div>


            </div>

        </div>


        <!-- AGENTS -->

        <div class="platform-section">

            <div class="platform-section-title">
                Five Specialized AI Agents
            </div>

            <div class="platform-section-subtitle">
                Each agent has a focused responsibility inside the
                study workflow.
            </div>


            <div class="agent-grid">


                <div class="agent">

                    <div class="agent-number">
                        01
                    </div>

                    <div class="agent-icon">
                        🎯
                    </div>

                    <div class="agent-name">
                        Controller
                    </div>

                    <div class="agent-text">
                        Understands the request and selects the appropriate
                        workflow.
                    </div>

                </div>


                <div class="agent">

                    <div class="agent-number">
                        02
                    </div>

                    <div class="agent-icon">
                        📝
                    </div>

                    <div class="agent-name">
                        Summary
                    </div>

                    <div class="agent-text">
                        Extracts and organizes the important information
                        from study material.
                    </div>

                </div>


                <div class="agent">

                    <div class="agent-number">
                        03
                    </div>

                    <div class="agent-icon">
                        🎴
                    </div>

                    <div class="agent-name">
                        Flashcard
                    </div>

                    <div class="agent-text">
                        Converts important concepts into concise
                        revision cards.
                    </div>

                </div>


                <div class="agent">

                    <div class="agent-number">
                        04
                    </div>

                    <div class="agent-icon">
                        🧩
                    </div>

                    <div class="agent-name">
                        Quiz
                    </div>

                    <div class="agent-text">
                        Creates questions to help students practice
                        and evaluate their understanding.
                    </div>

                </div>


                <div class="agent">

                    <div class="agent-number">
                        05
                    </div>

                    <div class="agent-icon">
                        📅
                    </div>

                    <div class="agent-name">
                        Planner
                    </div>

                    <div class="agent-text">
                        Builds structured study plans around learning
                        goals and available time.
                    </div>

                </div>


            </div>

        </div>


        <!-- WORKFLOW -->

        <div class="platform-section">

            <div class="platform-section-title">
                How It Works
            </div>

            <div class="platform-section-subtitle">
                From your documents to a complete AI-assisted study
                workflow.
            </div>


            <div class="workflow-grid">


                <div class="workflow">

                    <div class="workflow-number">
                        1
                    </div>

                    <div class="workflow-title">
                        Upload
                    </div>

                    <div class="workflow-text">
                        Upload your notes, presentations, books or
                        supported study documents.
                    </div>

                </div>


                <div class="workflow">

                    <div class="workflow-number">
                        2
                    </div>

                    <div class="workflow-title">
                        Process
                    </div>

                    <div class="workflow-text">
                        Your material is processed and prepared for
                        intelligent retrieval.
                    </div>

                </div>


                <div class="workflow">

                    <div class="workflow-number">
                        3
                    </div>

                    <div class="workflow-title">
                        Generate
                    </div>

                    <div class="workflow-text">
                        AI agents create summaries, flashcards, quizzes,
                        plans and contextual responses.
                    </div>

                </div>


                <div class="workflow">

                    <div class="workflow-number">
                        4
                    </div>

                    <div class="workflow-title">
                        Learn
                    </div>

                    <div class="workflow-text">
                        Use your generated resources to revise, practice
                        and understand your subjects.
                    </div>

                </div>


            </div>

        </div>


        <!-- SUBJECTS -->

        <div class="platform-section">

            <div class="platform-section-title">
                Designed for Academic Work
            </div>

            <div class="platform-section-subtitle">
                Currently focused on practical university-level
                study workflows.
            </div>


            <div class="platform-grid">


                <div class="platform-card">

                    <div class="platform-icon">
                        ☁️
                    </div>

                    <div class="platform-card-title">
                        Cloud Computing
                    </div>

                    <div class="platform-card-text">
                        Review cloud concepts, architectures, services
                        and technical definitions.
                    </div>

                </div>


                <div class="platform-card">

                    <div class="platform-icon">
                        👁️
                    </div>

                    <div class="platform-card-title">
                        Computer Vision
                    </div>

                    <div class="platform-card-text">
                        Transform technical lectures and notes into
                        structured revision resources.
                    </div>

                </div>


                <div class="platform-card">

                    <div class="platform-icon">
                        ⚙️
                    </div>

                    <div class="platform-card-title">
                        Algorithms
                    </div>

                    <div class="platform-card-text">
                        Practice algorithmic concepts and problem-solving
                        material through AI-generated resources.
                    </div>

                </div>


            </div>

        </div>


        <!-- TECHNOLOGY -->

        <div class="platform-section">

            <div class="platform-section-title">
                Technology Behind the Platform
            </div>

            <div class="platform-section-subtitle">
                A combination of AI, retrieval and modern application
                technologies.
            </div>


            <div class="technology">

                <span class="technology-pill">
                    Python
                </span>

                <span class="technology-pill">
                    Streamlit
                </span>

                <span class="technology-pill">
                    Generative AI
                </span>

                <span class="technology-pill">
                    RAG
                </span>

                <span class="technology-pill">
                    Vector Search
                </span>

                <span class="technology-pill">
                    AI Agents
                </span>

                <span class="technology-pill">
                    Document Processing
                </span>

                <span class="technology-pill">
                    Persistent Storage
                </span>

            </div>

        </div>


        <!-- VALUES -->

        <div class="platform-section">

            <div class="platform-section-title">
                Built Around the Student
            </div>

            <div class="platform-section-subtitle">
                The platform focuses on reducing repetitive study work
                and making academic material easier to use.
            </div>


            <div class="platform-grid">


                <div class="platform-card">

                    <div class="platform-icon">
                        🔐
                    </div>

                    <div class="platform-card-title">
                        Secure Accounts
                    </div>

                    <div class="platform-card-text">
                        Account passwords are handled using secure
                        password hashing.
                    </div>

                </div>


                <div class="platform-card">

                    <div class="platform-icon">
                        💾
                    </div>

                    <div class="platform-card-title">
                        Persistent Workspace
                    </div>

                    <div class="platform-card-text">
                        Study activity and generated resources can remain
                        available between sessions.
                    </div>

                </div>


                <div class="platform-card">

                    <div class="platform-icon">
                        🎓
                    </div>

                    <div class="platform-card-title">
                        Student First
                    </div>

                    <div class="platform-card-text">
                        Spend less time preparing study material and
                        more time understanding it.
                    </div>

                </div>


            </div>

        </div>


        <!-- FOOTER -->

        <div class="platform-footer">

            <div>

                <div class="platform-footer-title">
                    Agentic AI Study Helper
                </div>

                <div class="platform-footer-text">
                    An AI-powered study companion for a smarter,
                    more organized learning experience.
                </div>

            </div>


            <div class="platform-footer-version">
                Production Release<br>
                Version 1.0.0<br>
                © 2026 SBBWU Study Companion
            </div>

        </div>


    </div>
    """)


# ============================================================
# SIDEBAR FOOTER
# ============================================================

def render_sidebar_footer():
    """Render the sidebar footer."""

    st.html("""
    <div style="
        text-align:center;
        padding:8px 6px;
        font-family:Arial,sans-serif;
    ">

        <div style="
            font-size:11.5px;
            color:#9E828D;
            line-height:1.6;
        ">

            <strong style="color:#802B45;">
                Agentic AI Study Helper
            </strong>

            <br>

            <span>
                Production Release &bull; v1.0.0
            </span>

            <br>

            <span style="font-size:10px;">
                &copy; 2026 SBBWU Study Companion.
                All rights reserved.
            </span>

        </div>

    </div>
    """)