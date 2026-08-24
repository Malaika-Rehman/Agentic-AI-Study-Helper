# ─────────────────────────────────────────────────────────────────────────────
# DATA — Shared constants and dynamic course helpers
# ─────────────────────────────────────────────────────────────────────────────

DUMMY_USERS = {
    "malaika@sbbwu.edu.pk": {
        "password": "1234",
        "name": "Malaika Rehman",
        "student_id": "BC-25(B)U/22",
    }
}

# ── Color map — covers every subject in ai_agents._SUBJECT_KEYWORDS ──────────
# Format: lowercase subject name → hex color
_KNOWN_COLORS: dict[str, str] = {
    # Pakistan / Social
    "pakistan studies":                  "#7B4A1E",
    "islamic studies":                   "#1E6B5A",
    "islamiat":                          "#1E6B5A",
    "urdu":                              "#6B2E6B",
    # Sciences
    "organic chemistry":                 "#2E7B4A",
    "inorganic chemistry":               "#1E7B62",
    "physical chemistry":                "#2E6B5A",
    "chemistry":                         "#1E7B62",
    "biochemistry":                      "#3A7B2E",
    "biology":                           "#2E7B3A",
    "botany":                            "#3A7B1E",
    "zoology":                           "#4A7B1E",
    "microbiology":                      "#2E8B4A",
    "genetics":                          "#1E8B62",
    "anatomy":                           "#6B3A2E",
    "physiology":                        "#7B3A2E",
    "pharmacology":                      "#8B2E4A",
    "pathology":                         "#7B2E5A",
    "physics":                           "#2E3A88",
    "physics – thermodynamics":          "#3A2E88",
    "physics – quantum mechanics":       "#4A2E88",
    "physics – electromagnetism":        "#2E4A88",
    "physics – optics":                  "#2E5A88",
    "thermodynamics":                    "#3A2E88",
    "mathematics – calculus":            "#2E5A88",
    "mathematics – linear algebra":      "#3A5A88",
    "discrete mathematics":              "#4A5A88",
    "statistics":                        "#5A4A88",
    "probability & statistics":          "#5A3A88",
    "mathematics":                       "#2E4A88",
    # CS & IT
    "artificial intelligence":           "#802B45",
    "machine learning":                  "#6B2A5A",
    "deep learning":                     "#5A2A6B",
    "natural language processing":       "#4A2A7B",
    "computer vision":                   "#3A2A8B",
    "cloud computing":                   "#2A3A8B",
    "data structures":                   "#2A4A7B",
    "design & analysis of algorithms":   "#2A5A6B",
    "operating systems":                 "#2A6B5A",
    "computer networks":                 "#2A7B4A",
    "database systems":                  "#2A8B3A",
    "software engineering":              "#3A8B2A",
    "web development":                   "#4A8B2A",
    "cybersecurity":                     "#8B2A2A",
    "information security":              "#7B2A3A",
    "computer architecture":             "#6B2A4A",
    "compiler design":                   "#5A2A5A",
    "object-oriented programming":       "#4A2A6B",
    "programming":                       "#3A2A7B",
    "python programming":                "#2A3A7B",
    "java programming":                  "#2A4A6B",
    # Engineering
    "civil engineering":                 "#5A6B2E",
    "mechanical engineering":            "#6B5A2E",
    "electrical engineering":            "#6B2E5A",
    "electronics":                       "#5A2E6B",
    "telecommunication":                 "#4A2E7B",
    "chemical engineering":              "#2E5A6B",
    # Business / Economics
    "economics":                         "#2E6B7B",
    "microeconomics":                    "#2E7B6B",
    "macroeconomics":                    "#3E7B5B",
    "accounting":                        "#4E6B4B",
    "finance":                           "#5E5B4B",
    "marketing":                         "#6E4B4B",
    "management":                        "#5B4B6E",
    "business studies":                  "#4B4B7E",
    "entrepreneurship":                  "#7E4B4B",
    "human resource management":         "#6E5B4B",
    # Humanities
    "history":                           "#7B3A2E",
    "geography":                         "#3A7B2E",
    "sociology":                         "#6B2A6B",
    "psychology":                        "#4A6B2A",
    "philosophy":                        "#2A4A6B",
    "political science":                 "#5A2A4A",
    "international relations":           "#4A2A5A",
    "law":                               "#8B4A2A",
    "english literature":                "#4A8B2A",
    "literature":                        "#3A8B3A",
    "english":                           "#2A8B4A",
    "linguistics":                       "#2A7B5A",
    "journalism & mass communication":   "#2A6B6B",
    "mass communication":                "#2A6B6B",
    # Medical
    "medical studies":                   "#8B2A2A",
    "medicine":                          "#7B2A3A",
    "nursing":                           "#6B2A4A",
    "dentistry":                         "#5A2A5A",
    "public health":                     "#4A2A6B",
    # Others
    "environmental science":             "#2A7B3A",
    "agriculture":                       "#3A7B2A",
    "architecture":                      "#6B6B2A",
    "fashion design":                    "#8B2A6B",
    "fine arts":                         "#7B2A7B",
    "education":                         "#2A6B8B",
    "food science":                      "#7B5A2A",
    "general study material":            "#5A5A5A",
}

# Fallback palette for subjects not in the map
_COLOR_PALETTE = [
    "#802B45", "#2E5A88", "#1E7B62", "#6B4C9A",
    "#B85C2A", "#2A7B8A", "#7B3A2E", "#3A7B2E",
    "#5A2E88", "#2E6B7B", "#88502E", "#6B2E6B",
]


def get_course_color(course_name: str) -> str:
    """
    Return a consistent hex color for any subject name.
    1. Exact match (case-insensitive)
    2. Partial match (e.g. "Calculus" inside "Mathematics – Calculus")
    3. Hash-based color from palette
    """
    if not course_name:
        return _COLOR_PALETTE[0]

    lower = course_name.lower().strip()

    # Exact match
    if lower in _KNOWN_COLORS:
        return _KNOWN_COLORS[lower]

    # Partial match — find any known subject whose name appears in the detected name
    for known, color in _KNOWN_COLORS.items():
        if known in lower or lower in known:
            return color

    # Hash-based deterministic fallback
    import hashlib
    h = int(hashlib.md5(course_name.encode()).hexdigest(), 16)
    return _COLOR_PALETTE[h % len(_COLOR_PALETTE)]


def get_course_info(course_name: str) -> dict:
    """
    Return a minimal course info dict for any dynamically detected subject.
    Replaces the old hard-coded COURSES dict everywhere in the app.
    """
    return {
        "color":      get_course_color(course_name),
        "completed":  0,
        "total":      0,
        "progress":   0,
        "flashcards": 0,
        "quiz_score": 0,
    }


# ── Legacy COURSES dict — kept so old imports don't break ────────────────────
COURSES: dict[str, dict] = {}