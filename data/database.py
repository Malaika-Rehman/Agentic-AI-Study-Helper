"""
SQLite database layer.
Handles: users, documents metadata, generated results, chat history.
DB file: study_helper.db (auto-created in project root)
"""
import sqlite3
import hashlib
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "study_helper.db")


def _conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ─────────────────────────────────────────────
# INIT — Create all tables if not exist
# ─────────────────────────────────────────────
def init_db():
    with _conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            email       TEXT    UNIQUE NOT NULL,
            password    TEXT    NOT NULL,
            name        TEXT    NOT NULL,
            student_id  TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS documents (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email  TEXT    NOT NULL,
            filename    TEXT    NOT NULL,
            course      TEXT    NOT NULL,
            doc_text    TEXT    NOT NULL,
            uploaded_at TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_email) REFERENCES users(email)
        );

        CREATE TABLE IF NOT EXISTS results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email  TEXT    NOT NULL,
            doc_id      INTEGER NOT NULL,
            course      TEXT    NOT NULL,
            summary     TEXT,
            flashcards  TEXT,
            quiz        TEXT,
            study_plan  TEXT,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (doc_id) REFERENCES documents(id)
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email  TEXT    NOT NULL,
            doc_id      INTEGER,
            role        TEXT    NOT NULL,
            content     TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (doc_id) REFERENCES documents(id)
        );
        """)


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(email: str, password: str, name: str, student_id: str) -> tuple[bool, str]:
    """Returns (success, message)"""
    try:
        with _conn() as conn:
            conn.execute(
                "INSERT INTO users (email, password, name, student_id) VALUES (?, ?, ?, ?)",
                (email.strip().lower(), _hash(password), name.strip(), student_id.strip())
            )
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    except Exception as e:
        return False, f"Registration error: {e}"


def login_user(email: str, password: str) -> tuple[bool, dict | str]:
    """Returns (success, user_dict or error_message)"""
    try:
        with _conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email.strip().lower(),)
            ).fetchone()
        if not row:
            return False, "No account found with this email."
        if row["password"] != _hash(password):
            return False, "Incorrect password."
        return True, dict(row)
    except Exception as e:
        return False, f"Login error: {e}"


# ─────────────────────────────────────────────
# DOCUMENTS
# ─────────────────────────────────────────────
def save_document(user_email: str, filename: str, course: str, doc_text: str) -> int:
    """Save document and return its ID."""
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO documents (user_email, filename, course, doc_text) VALUES (?, ?, ?, ?)",
            (user_email, filename, course, doc_text)
        )
        return cur.lastrowid


def get_user_documents(user_email: str) -> list[dict]:
    """Get all documents for a user, newest first."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, filename, course, uploaded_at FROM documents WHERE user_email = ? ORDER BY uploaded_at DESC",
            (user_email,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_document_text(doc_id: int) -> str:
    with _conn() as conn:
        row = conn.execute("SELECT doc_text FROM documents WHERE id = ?", (doc_id,)).fetchone()
    return row["doc_text"] if row else ""


# ─────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────
def save_results(user_email: str, doc_id: int, course: str,
                 summary: str, flashcards: list, quiz: list, study_plan: list):
    with _conn() as conn:
        # Delete old result for same doc if re-processing
        conn.execute("DELETE FROM results WHERE doc_id = ?", (doc_id,))
        conn.execute(
            """INSERT INTO results (user_email, doc_id, course, summary, flashcards, quiz, study_plan)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_email, doc_id, course,
             summary,
             json.dumps(flashcards),
             json.dumps(quiz),
             json.dumps(study_plan))
        )


def get_results(doc_id: int) -> dict | None:
    with _conn() as conn:
        row = conn.execute("SELECT * FROM results WHERE doc_id = ?", (doc_id,)).fetchone()
    if not row:
        return None
    r = dict(row)
    r["flashcards"]  = json.loads(r["flashcards"]  or "[]")
    r["quiz"]        = json.loads(r["quiz"]         or "[]")
    r["study_plan"]  = json.loads(r["study_plan"]   or "[]")
    return r


def update_study_plan(doc_id: int, study_plan: list):
    """Save updated study plan (checkbox state) back to DB."""
    with _conn() as conn:
        conn.execute(
            "UPDATE results SET study_plan = ? WHERE doc_id = ?",
            (json.dumps(study_plan), doc_id)
        )


# ─────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────
def save_message(user_email: str, doc_id: int, role: str, content: str):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO chat_history (user_email, doc_id, role, content) VALUES (?, ?, ?, ?)",
            (user_email, doc_id, role, content)
        )


def get_chat_history(user_email: str, doc_id: int) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT role, content FROM chat_history WHERE user_email = ? AND doc_id = ? ORDER BY created_at ASC",
            (user_email, doc_id)
        ).fetchall()
    return [dict(r) for r in rows]


def clear_chat_history(user_email: str, doc_id: int):
    with _conn() as conn:
        conn.execute(
            "DELETE FROM chat_history WHERE user_email = ? AND doc_id = ?",
            (user_email, doc_id)
        )
