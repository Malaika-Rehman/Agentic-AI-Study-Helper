import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Preferred candidate models in order of priority
DEFAULT_CANDIDATES = [
    "groq/compound-mini",
    "openai/gpt-oss-20b",
    "allam-2-7b",
    "qwen/qwen3.6-27b",
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
]

_ACTIVE_MODEL = None

FIXED_COURSES = [
    "CS301 – Cloud Computing",
    "CS401 – Computer Vision",
    "CS501 – Design & Analysis of Algorithm",
]


def get_api_key() -> str:
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        try:
            import streamlit as st
            if "GROQ_API_KEY" in st.secrets:
                key = str(st.secrets["GROQ_API_KEY"]).strip()
        except Exception:
            pass
    return key


def get_client():
    api_key = get_api_key()
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please add it to your .env file or Streamlit secrets.")
    return Groq(api_key=api_key)


def get_configured_model() -> str:
    global _ACTIVE_MODEL
    if _ACTIVE_MODEL:
        return _ACTIVE_MODEL

    env_model = os.getenv("GROQ_MODEL", "").strip()
    if not env_model:
        try:
            import streamlit as st
            if "GROQ_MODEL" in st.secrets:
                env_model = str(st.secrets["GROQ_MODEL"]).strip()
        except Exception:
            pass

    if env_model:
        _ACTIVE_MODEL = env_model
        return _ACTIVE_MODEL

    return DEFAULT_CANDIDATES[0]


def _call(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
    global _ACTIVE_MODEL
    client = get_client()

    current_model = get_configured_model()
    candidate_list = [current_model] + [m for m in DEFAULT_CANDIDATES if m != current_model]

    last_err = None
    for model_name in candidate_list:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            _ACTIVE_MODEL = model_name
            content = response.choices[0].message.content or ""
            # Clean reasoning think tags if present
            cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
            return cleaned if cleaned else content.strip()
        except Exception as e:
            last_err = e
            # Try next fallback model
            continue

    # If all candidates failed, raise the last encountered error
    raise last_err or RuntimeError("Failed to get response from Groq API.")


# ── AGENT 1 — CONTROLLER: Detect Subject ──────────────────────
def detect_subject(text: str) -> str:
    system = """You are a subject classifier. Decide which ONE of these 3 courses the document belongs to:
- CS301 – Cloud Computing
- CS401 – Computer Vision
- CS501 – Design & Analysis of Algorithm
Reply with ONLY the exact course name. Nothing else."""
    result = _call(system, f"Document (first 3000 chars):\n{text[:3000]}", max_tokens=50)
    for course in FIXED_COURSES:
        if course.lower() in result.lower():
            return course
    text_lower = text.lower()
    if any(w in text_lower for w in ["computer vision", "image processing", "object detection", "opencv", "segmentation"]):
        return "CS401 – Computer Vision"
    elif any(w in text_lower for w in ["algorithm", "complexity", "big o", "sorting", "graph", "dynamic programming", "greedy"]):
        return "CS501 – Design & Analysis of Algorithm"
    return "CS301 – Cloud Computing"


# ── AGENT 2 — SUMMARY ─────────────────────────────────────────
def generate_summary(text: str, course: str) -> str:
    system = """You are an expert academic summarizer for university students.
Create a clear, structured summary with these sections:
1. **Overview** (2-3 sentences)
2. **Key Concepts** (bullet points)
3. **Important Definitions** (bullet points)
4. **Core Takeaways** (3-5 bullet points)"""
    return _call(system, f"Course: {course}\n\nMaterial:\n{text[:6000]}\n\nGenerate a structured summary.", 1500)


# ── AGENT 3 — FLASHCARDS ──────────────────────────────────────
def generate_flashcards(text: str, course: str) -> list[tuple[str, str]]:
    system = """You are a flashcard generation expert. Create exactly 8 flashcards.
Respond with VALID JSON ONLY — no markdown, no explanation:
[{"question": "...", "answer": "..."}, ...]"""
    raw = _call(system, f"Course: {course}\n\nMaterial:\n{text[:6000]}\n\nGenerate 8 flashcards as JSON.", 2000)
    try:
        cards = json.loads(re.sub(r"```json|```", "", raw).strip())
        return [(c["question"], c["answer"]) for c in cards if "question" in c and "answer" in c]
    except Exception:
        return [("Could not generate flashcards.", "Please try uploading the document again.")]


# ── AGENT 4 — QUIZ ────────────────────────────────────────────
def generate_quiz(text: str, course: str) -> list[tuple[str, list[str], int]]:
    system = """You are a quiz generation expert. Create exactly 5 MCQs.
Respond with VALID JSON ONLY — no markdown, no explanation:
[{"question": "...", "options": ["A", "B", "C", "D"], "correct": 0}, ...]
Where "correct" is the 0-based index of the correct option."""
    raw = _call(system, f"Course: {course}\n\nMaterial:\n{text[:6000]}\n\nGenerate 5 MCQs as JSON.", 2000)
    try:
        questions = json.loads(re.sub(r"```json|```", "", raw).strip())
        return [(q["question"], q["options"], q["correct"]) for q in questions
                if "question" in q and "options" in q and "correct" in q]
    except Exception:
        return [("Could not generate quiz.", ["Try again", "Re-upload document", "Check format", "Contact support"], 0)]


# ── AGENT 5 — PLANNER ─────────────────────────────────────────
def generate_study_plan(text: str, course: str) -> list[tuple[str, str, bool]]:
    system = """You are an academic study planner. Create a 4-week study plan.
Respond with VALID JSON ONLY — no markdown, no explanation:
[{"week": "Week 1 – Title", "description": "...", "completed": false}, ...]
Generate exactly 4 weeks."""
    raw = _call(system, f"Course: {course}\n\nMaterial:\n{text[:5000]}\n\nGenerate 4-week plan as JSON.", 1500)
    try:
        plan = json.loads(re.sub(r"```json|```", "", raw).strip())
        return [(p["week"], p["description"], p.get("completed", False)) for p in plan]
    except Exception:
        return [
            ("Week 1 – Foundations",    "Review core concepts from the document.",   False),
            ("Week 2 – Deep Dive",      "Study each topic in detail with examples.", False),
            ("Week 3 – Practice",       "Complete flashcards and quiz questions.",    False),
            ("Week 4 – Revision",       "Full revision and timed self-assessment.",   False),
        ]


# ── CHAT AGENT — RAG + General Fallback ───────────────────────
def answer_question(question: str, doc_context: str, course: str, use_general: bool = True) -> str:
    if doc_context.strip():
        system = f"""You are an intelligent study assistant for {course}.
Answer the student's question using the provided document context.
If the answer isn't in the context and use_general is true, use your general knowledge but clearly say so.
Be clear, accurate, and educational."""
        user = f"""Document context:
{doc_context}

Student question: {question}"""
    else:
        system = f"""You are an intelligent study assistant for {course}.
Answer the student's question using your general knowledge.
Be clear, accurate, and educational. Mention that no document is currently loaded."""
        user = question

    return _call(system, user, max_tokens=800)