import os
import json
import re

from dotenv import load_dotenv
from groq import Groq


# ─────────────────────────────────────────────────────────────────────────────
# PROJECT / ENVIRONMENT CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

# ai_agents.py is inside:
#     Agentic AI Study Helper/data/ai_agents.py
#
# Therefore, going two levels appropriately resolves the project root:
#     Agentic AI Study Helper/
#
# The .env file should be located directly in the project root.

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

ENV_FILE = os.path.join(
    PROJECT_ROOT,
    ".env"
)

# Explicitly load the project's .env file.
load_dotenv(
    dotenv_path=ENV_FILE,
    override=False
)


# ─────────────────────────────────────────────────────────────────────────────
# GROQ MODELS
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# SUBJECT KEYWORD MAP
# ─────────────────────────────────────────────────────────────────────────────

_SUBJECT_KEYWORDS: dict[str, str] = {

    # Pakistan / Social Sciences
    "pakistan stud":        "Pakistan Studies",
    "pak stud":             "Pakistan Studies",
    "quaid-e-azam":         "Pakistan Studies",
    "jinnah":               "Pakistan Studies",

    "islamic stud":         "Islamic Studies",
    "islamiat":             "Islamic Studies",
    "quran":                "Islamic Studies",
    "hadith":               "Islamic Studies",
    "fiqh":                 "Islamic Studies",

    "urdu":                 "Urdu",
    "ادو":                  "Urdu",

    # Sciences
    "organic chemistry":    "Organic Chemistry",
    "inorganic chemistry":  "Inorganic Chemistry",
    "physical chemistry":   "Physical Chemistry",
    "chemistry":            "Chemistry",
    "biochemistry":         "Biochemistry",
    "biology":              "Biology",
    "botany":               "Botany",
    "zoology":              "Zoology",
    "microbiology":          "Microbiology",
    "genetics":             "Genetics",
    "anatomy":              "Anatomy",
    "physiology":           "Physiology",
    "pharmacology":         "Pharmacology",
    "pathology":            "Pathology",

    "physics":              "Physics",
    "thermodynamics":       "Physics – Thermodynamics",
    "quantum mechanic":     "Physics – Quantum Mechanics",
    "electromagnetism":     "Physics – Electromagnetism",
    "optics":               "Physics – Optics",

    "calculus":             "Mathematics – Calculus",
    "linear algebra":       "Mathematics – Linear Algebra",
    "discrete math":        "Discrete Mathematics",
    "statistics":           "Statistics",
    "probability":          "Probability & Statistics",
    "mathematics":          "Mathematics",
    "maths":                "Mathematics",

    # CS & IT
    "artificial intelligence": "Artificial Intelligence",
    "machine learning":        "Machine Learning",
    "deep learning":           "Deep Learning",
    "neural network":          "Deep Learning",
    "natural language":        "Natural Language Processing",
    "computer vision":         "Computer Vision",
    "cloud computing":         "Cloud Computing",

    "data structure":          "Data Structures",
    "algorithm":               "Design & Analysis of Algorithms",
    "operating system":        "Operating Systems",
    "computer network":        "Computer Networks",
    "networking":              "Computer Networks",
    "database":                "Database Systems",
    "software engineer":       "Software Engineering",
    "web develop":             "Web Development",
    "cybersecurity":           "Cybersecurity",
    "information security":    "Information Security",
    "computer architecture":   "Computer Architecture",
    "compiler":                "Compiler Design",
    "object oriented":         "Object-Oriented Programming",
    "programming":             "Programming",
    "python":                  "Python Programming",
    "java":                    "Java Programming",

    # Engineering
    "civil engineer":          "Civil Engineering",
    "mechanical engineer":     "Mechanical Engineering",
    "electrical engineer":     "Electrical Engineering",
    "electronics":             "Electronics",
    "telecommunication":       "Telecommunication",
    "chemical engineer":       "Chemical Engineering",
    "thermodynamic":           "Thermodynamics",

    # Business / Economics
    "economics":               "Economics",
    "microeconomics":          "Microeconomics",
    "macroeconomics":          "Macroeconomics",
    "accounting":              "Accounting",
    "finance":                 "Finance",
    "marketing":               "Marketing",
    "management":              "Management",
    "business":                "Business Studies",
    "entrepreneurship":        "Entrepreneurship",
    "human resource":          "Human Resource Management",

    # Humanities & Social Sciences
    "history":                 "History",
    "geography":               "Geography",
    "sociology":               "Sociology",
    "psychology":              "Psychology",
    "philosophy":              "Philosophy",
    "political science":       "Political Science",
    "international relation":  "International Relations",
    "law":                     "Law",
    "english literature":      "English Literature",
    "literature":              "Literature",
    "english":                 "English",
    "linguistics":             "Linguistics",
    "journalism":              "Journalism & Mass Communication",
    "mass communication":      "Mass Communication",

    # Medical
    "mbbs":                    "Medical Studies",
    "medicine":                "Medicine",
    "nursing":                 "Nursing",
    "dentistry":               "Dentistry",
    "public health":           "Public Health",

    # Others
    "environmental":           "Environmental Science",
    "agriculture":             "Agriculture",
    "architecture":            "Architecture",
    "fashion":                 "Fashion Design",
    "fine arts":               "Fine Arts",
    "education":               "Education",
    "food science":            "Food Science",
}


# ─────────────────────────────────────────────────────────────────────────────
# GROQ API KEY
# ─────────────────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    """
    Get the Groq API key.

    Priority:
    1. Environment variable loaded from project-root .env
    2. Streamlit secrets

    The actual API key is never printed.
    """

    # First attempt: environment variable
    key = os.getenv(
        "GROQ_API_KEY",
        ""
    ).strip()

    if key:
        return key

    # Second attempt: explicitly reload the project .env
    try:
        load_dotenv(
            dotenv_path=ENV_FILE,
            override=False
        )

        key = os.getenv(
            "GROQ_API_KEY",
            ""
        ).strip()

        if key:
            return key

    except Exception as e:
        print(
            f"[Groq] Could not load .env file: {e}"
        )

    # Third attempt: Streamlit secrets
    try:
        import streamlit as st

        if "GROQ_API_KEY" in st.secrets:

            key = str(
                st.secrets["GROQ_API_KEY"]
            ).strip()

            if key:
                return key

    except Exception:
        pass

    return ""


# ─────────────────────────────────────────────────────────────────────────────
# GROQ CLIENT
# ─────────────────────────────────────────────────────────────────────────────

def get_client():
    """
    Create and return the Groq client.
    """

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. "
            f"Expected it in: {ENV_FILE} "
            "or Streamlit secrets."
        )

    return Groq(
        api_key=api_key
    )


# ─────────────────────────────────────────────────────────────────────────────
# GROQ MODEL CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

def get_configured_model() -> str:

    global _ACTIVE_MODEL

    if _ACTIVE_MODEL:
        return _ACTIVE_MODEL

    env_model = os.getenv(
        "GROQ_MODEL",
        ""
    ).strip()

    if not env_model:

        try:

            import streamlit as st

            if "GROQ_MODEL" in st.secrets:

                env_model = str(
                    st.secrets["GROQ_MODEL"]
                ).strip()

        except Exception:
            pass

    if env_model:

        _ACTIVE_MODEL = env_model

        return _ACTIVE_MODEL

    return DEFAULT_CANDIDATES[0]


# ─────────────────────────────────────────────────────────────────────────────
# COMMON GROQ CALL
# ─────────────────────────────────────────────────────────────────────────────

def _call(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 2000
) -> str:

    global _ACTIVE_MODEL

    client = get_client()

    current_model = get_configured_model()

    candidate_list = [
        current_model
    ] + [
        model
        for model in DEFAULT_CANDIDATES
        if model != current_model
    ]

    last_err = None

    for model_name in candidate_list:

        try:

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    },
                ],
                max_tokens=max_tokens,
                temperature=0.3,
            )

            _ACTIVE_MODEL = model_name

            content = (
                response.choices[0].message.content
                or ""
            )

            cleaned = re.sub(
                r"<think>.*?</think>",
                "",
                content,
                flags=re.DOTALL
            ).strip()

            return (
                cleaned
                if cleaned
                else content.strip()
            )

        except Exception as e:

            last_err = e

            continue

    raise (
        last_err
        or RuntimeError(
            "Failed to get response from Groq API."
        )
    )


# ─────────────────────────────────────────────────────────────────────────────
# FILENAME HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _parse_filename(filename: str) -> str:

    name = os.path.splitext(
        filename
    )[0]

    name = re.sub(
        r"[_\-]+",
        " ",
        name
    ).strip()

    generic = {
        "notes",
        "document",
        "file",
        "doc",
        "pdf",
        "slides",
        "lecture",
        "lec",
        "chapter",
        "ch",
        "unit",
        "book",
        "assignment",
        "homework",
        "exam",
        "test",
        "quiz",
        "final",
        "mid"
    }

    words = name.lower().split()

    meaningful_words = [
        word
        for word in words
        if word not in generic
        and len(word) > 1
    ]

    if not meaningful_words:
        return ""

    return name.title()


# ─────────────────────────────────────────────────────────────────────────────
# KEYWORD SUBJECT DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def _keyword_detect(
    text: str,
    filename: str = ""
) -> str:

    haystack = (
        filename
        + " "
        + text[:3000]
    ).lower()

    for keyword in sorted(
        _SUBJECT_KEYWORDS.keys(),
        key=len,
        reverse=True
    ):

        if keyword in haystack:

            return _SUBJECT_KEYWORDS[
                keyword
            ]

    return ""


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 1 — CONTROLLER
# ─────────────────────────────────────────────────────────────────────────────

def detect_subject(
    text: str,
    filename: str = ""
) -> str:

    filename_hint = _parse_filename(
        filename
    )

    # Layer 1 — keyword detection
    keyword_result = _keyword_detect(
        text,
        filename
    )

    if keyword_result:

        # Try LLM refinement
        try:

            refined = _llm_detect(
                text,
                filename_hint or keyword_result
            )

            if (
                refined
                and refined.lower() != "unknown"
            ):

                return refined

        except Exception:
            pass

        return keyword_result

    # Layer 2 — LLM detection
    try:

        result = _llm_detect(
            text,
            filename_hint
        )

        if (
            result
            and result.lower()
            not in (
                "unknown",
                "general",
                ""
            )
        ):

            return result

    except Exception:
        pass

    # Layer 3 — filename fallback
    if filename_hint:

        return filename_hint

    # Layer 4 — final fallback
    return "General Study Material"


# ─────────────────────────────────────────────────────────────────────────────
# LLM SUBJECT DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def _llm_detect(
    text: str,
    hint: str = ""
) -> str:

    hint_line = (
        f'The filename suggests: "{hint}". '
        "Use this as a strong hint.\n"
        if hint
        else ""
    )

    system = """You are an expert academic subject identifier.

Your task: Read the document and identify its subject or course name.

IMPORTANT RULES:
- There is NO predefined list — identify the actual subject freely.
- Return ONLY the subject name. No explanation, no punctuation at the end.
- If there is a course code, include it: "CS301 – Data Structures"
- For general subjects: "Pakistan Studies", "Organic Chemistry", "World History"
- Be specific: "Thermodynamics" not just "Physics"
- Maximum 7 words.
- If truly uncertain, return your best guess — never return "Unknown"."""

    user = f"""{hint_line}Identify the subject of this document.

Here are the first 2500 characters:

{text[:2500]}

Reply with ONLY the subject name:"""

    result = _call(
        system,
        user,
        max_tokens=25
    ).strip()

    result = re.sub(
        r'^[\"\']|[\"\']$',
        "",
        result
    ).strip(
        " .,:"
    )

    return result


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 2 — SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def generate_summary(
    text: str,
    course: str
) -> str:

    system = f"""You are an expert academic summarizer helping a university student
studying {course}. Create a clear, structured summary with these exact sections:

1. **Overview** (2-3 sentences about the main topic)
2. **Key Concepts** (bullet points of the main ideas)
3. **Important Definitions** (bullet points: Term – Definition)
4. **Core Takeaways** (3-5 actionable bullet points)

Base everything strictly on the provided document content."""

    return _call(
        system,
        (
            f"Course: {course}\n\n"
            f"Document:\n{text[:6000]}\n\n"
            "Generate a structured summary."
        ),
        1500,
    )


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 3 — FLASHCARDS
# ─────────────────────────────────────────────────────────────────────────────

def generate_flashcards(
    text: str,
    course: str
) -> list[tuple[str, str]]:

    system = f"""You are a flashcard generation expert for {course}.
Create exactly 8 flashcards based strictly on the provided document.
Cover the most important concepts, definitions, and facts.

Respond with VALID JSON ONLY — no markdown fences, no explanation:

[{{"question": "...", "answer": "..."}}, ...]"""

    raw = _call(
        system,
        (
            f"Course: {course}\n\n"
            f"Document:\n{text[:6000]}\n\n"
            "Generate 8 flashcards as JSON."
        ),
        2000,
    )

    try:

        cards = json.loads(
            re.sub(
                r"```json|```",
                "",
                raw
            ).strip()
        )

        result = [
            (
                card["question"],
                card["answer"]
            )
            for card in cards
            if (
                "question" in card
                and "answer" in card
            )
        ]

        if result:
            return result

    except Exception:
        pass

    return [
        (
            "Could not generate flashcards.",
            "Please try re-uploading the document."
        )
    ]


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 4 — QUIZ
# ─────────────────────────────────────────────────────────────────────────────

def generate_quiz(
    text: str,
    course: str
) -> list[tuple[str, list[str], int]]:

    system = f"""You are a quiz generation expert for {course}.
Create exactly 5 multiple-choice questions (MCQs) based strictly on the document.

Respond with VALID JSON ONLY — no markdown fences, no explanation:

[{{"question": "...", "options": ["A...", "B...", "C...", "D..."], "correct": 0}}, ...]

"correct" is the 0-based index of the correct answer."""

    raw = _call(
        system,
        (
            f"Course: {course}\n\n"
            f"Document:\n{text[:6000]}\n\n"
            "Generate 5 MCQs as JSON."
        ),
        2000,
    )

    try:

        questions = json.loads(
            re.sub(
                r"```json|```",
                "",
                raw
            ).strip()
        )

        result = [
            (
                question["question"],
                question["options"],
                int(question["correct"])
            )
            for question in questions
            if (
                "question" in question
                and "options" in question
                and "correct" in question
            )
        ]

        if result:
            return result

    except Exception:
        pass

    return [
        (
            "Could not generate quiz questions.",
            [
                "Try again",
                "Re-upload",
                "Check format",
                "Contact support"
            ],
            0
        )
    ]


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 5 — STUDY PLANNER
# ─────────────────────────────────────────────────────────────────────────────

def generate_study_plan(
    text: str,
    course: str
) -> list[tuple[str, str, bool]]:

    system = f"""You are an academic study planner for {course}.
Create a practical 4-week study plan based on the actual topics in the document.
Each week should build on the previous one.

Respond with VALID JSON ONLY — no markdown fences, no explanation:

[{{"week": "Week 1 – Topic Title", "description": "What to study and how.", "completed": false}}, ...]

Generate exactly 4 weeks."""

    raw = _call(
        system,
        (
            f"Course: {course}\n\n"
            f"Document:\n{text[:5000]}\n\n"
            "Generate a 4-week study plan as JSON."
        ),
        1500,
    )

    try:

        plan = json.loads(
            re.sub(
                r"```json|```",
                "",
                raw
            ).strip()
        )

        result = [
            (
                item["week"],
                item["description"],
                bool(
                    item.get(
                        "completed",
                        False
                    )
                )
            )
            for item in plan
        ]

        if result:
            return result

    except Exception:
        pass

    return [
        (
            "Week 1 – Foundations",
            "Review core concepts and key definitions from the document.",
            False
        ),
        (
            "Week 2 – Deep Dive",
            "Study each major topic in depth with examples and notes.",
            False
        ),
        (
            "Week 3 – Practice",
            "Complete all flashcards and quiz questions multiple times.",
            False
        ),
        (
            "Week 4 – Final Revision",
            "Full revision, timed self-assessment, and weak-area review.",
            False
        ),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# CHAT AGENT — RAG + GENERAL FALLBACK
# ─────────────────────────────────────────────────────────────────────────────

def answer_question(
    question: str,
    doc_context: str,
    course: str
) -> str:

    if doc_context.strip():

        system = f"""You are an intelligent study assistant for {course} at SBBWU.
Answer the student's question using the provided document context.

If the answer is not in the context, use your general knowledge but say:
"This isn't directly in your document, but generally..."

Be clear, accurate, concise, and educational."""

        user = (
            f"Document context:\n"
            f"{doc_context}\n\n"
            f"Student question: {question}"
        )

    else:

        system = f"""You are an intelligent study assistant for {course} at SBBWU.
No document is loaded. Answer using your general knowledge.

Tell the student to upload a document for document-specific answers.

Be clear, accurate, and educational."""

        user = question

    return _call(
        system,
        user,
        max_tokens=800
    )