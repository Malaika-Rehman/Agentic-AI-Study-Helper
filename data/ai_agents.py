import os
import json
import re
from groq import Groq

def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please add it to your .env file.")
    return Groq(api_key=api_key)

MODEL = "llama-3.3-70b-versatile"

FIXED_COURSES = [
    "CS301 – Cloud Computing",
    "CS401 – Computer Vision",
    "CS501 – Design & Analysis of Algorithm",
]


def _call(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
    client   = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


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
