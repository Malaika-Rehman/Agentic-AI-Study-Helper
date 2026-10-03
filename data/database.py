"""
SQLite database layer.
Handles: users, persistent sessions, documents metadata, generated results, chat history,
push notification subscriptions, and notification audit logs.
DB file: study_helper.db (auto-created in project root)
"""
import sqlite3
import hashlib
import os
import json
import secrets
from datetime import datetime, timedelta, timezone

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
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            email              TEXT    UNIQUE NOT NULL,
            password           TEXT    NOT NULL,
            name               TEXT    NOT NULL,
            student_id         TEXT    NOT NULL DEFAULT '',
            login_count        INTEGER NOT NULL DEFAULT 0,
            last_login         TEXT,
            last_activity      TEXT,
            last_reminder_sent TEXT,
            is_active          INTEGER NOT NULL DEFAULT 1,
            created_at         TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS user_sessions (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email    TEXT    NOT NULL,
            session_token TEXT    UNIQUE NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now')),
            last_activity TEXT    DEFAULT (datetime('now')),
            expires_at    TEXT    NOT NULL,
            is_active     INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_email) REFERENCES users(email)
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

        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email  TEXT    NOT NULL,
            endpoint    TEXT    UNIQUE NOT NULL,
            p256dh      TEXT    NOT NULL,
            auth        TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_email) REFERENCES users(email)
        );

        CREATE TABLE IF NOT EXISTS notification_logs (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email        TEXT    NOT NULL,
            notification_type TEXT    NOT NULL,
            channel           TEXT    NOT NULL DEFAULT 'webpush',
            status            TEXT    NOT NULL,
            details           TEXT,
            sent_at           TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_email) REFERENCES users(email)
        );

        CREATE TABLE IF NOT EXISTS app_settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """)

        # Safe schema migrations for existing database files
        migrations = [
            "ALTER TABLE users ADD COLUMN login_count INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE users ADD COLUMN last_login TEXT",
            "ALTER TABLE users ADD COLUMN last_activity TEXT",
            "ALTER TABLE users ADD COLUMN last_reminder_sent TEXT",
            "ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1",
        ]
        for mig in migrations:
            try:
                conn.execute(mig)
            except sqlite3.OperationalError:
                pass


# ─────────────────────────────────────────────
# APP SETTINGS & ONBOARDING STATE
# ─────────────────────────────────────────────
def is_onboarding_completed() -> bool:
    """Returns True if onboarding has already been completed/seen."""
    try:
        with _conn() as conn:
            row = conn.execute(
                "SELECT value FROM app_settings WHERE key = 'onboarding_completed'"
            ).fetchone()
            return bool(row and row["value"] == "1")
    except Exception:
        return False


def set_onboarding_completed():
    """Mark onboarding as completed so returning users go directly to login."""
    try:
        with _conn() as conn:
            conn.execute(
                "INSERT INTO app_settings (key, value) VALUES ('onboarding_completed', '1') "
                "ON CONFLICT(key) DO UPDATE SET value = '1'"
            )
    except Exception:
        pass


def get_app_setting(key: str, default: str = "") -> str:
    """Get an arbitrary setting from app_settings."""
    try:
        with _conn() as conn:
            row = conn.execute(
                "SELECT value FROM app_settings WHERE key = ?", (key,)
            ).fetchone()
            return row["value"] if row else default
    except Exception:
        return default


def set_app_setting(key: str, value: str):
    """Set an arbitrary setting in app_settings."""
    try:
        with _conn() as conn:
            conn.execute(
                "INSERT INTO app_settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = ?",
                (key, value, value)
            )
    except Exception:
        pass


# ─────────────────────────────────────────────
# AUTH & PASSWORD HASHING
# ─────────────────────────────────────────────
def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(email: str, password: str, name: str, student_id: str = "") -> tuple[bool, str]:
    """Returns (success, message)"""
    try:
        clean_email = email.strip().lower()
        now_str = datetime.now(timezone.utc).isoformat()
        with _conn() as conn:
            conn.execute(
                "INSERT INTO users (email, password, name, student_id, last_activity) VALUES (?, ?, ?, ?, ?)",
                (clean_email, _hash(password), name.strip(), student_id.strip() if student_id else "", now_str)
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


def record_login(email: str) -> bool:
    """Increments login_count, updates last_login and last_activity timestamps,
    and returns True if this was user's first-ever login."""
    clean_email = email.strip().lower()
    now_str = datetime.now(timezone.utc).isoformat()
    with _conn() as conn:
        row = conn.execute(
            "SELECT login_count FROM users WHERE email = ?", (clean_email,)
        ).fetchone()
        is_first_login = bool(row) and row["login_count"] == 0
        conn.execute(
            "UPDATE users SET login_count = login_count + 1, last_login = ?, last_activity = ? WHERE email = ?",
            (now_str, now_str, clean_email)
        )
    return is_first_login


# ─────────────────────────────────────────────
# PERSISTENT SESSIONS (REMEMBER ME)
# ─────────────────────────────────────────────
def create_user_session(email: str, days_valid: int = 30) -> str:
    """Generate a secure random session token and store in user_sessions table."""
    clean_email = email.strip().lower()
    session_token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(days=days_valid)).isoformat()
    now_str = now.isoformat()

    with _conn() as conn:
        conn.execute(
            """INSERT INTO user_sessions (user_email, session_token, created_at, last_activity, expires_at, is_active)
               VALUES (?, ?, ?, ?, ?, 1)""",
            (clean_email, session_token, now_str, now_str, expires_at)
        )
        # Also update user's last_activity
        conn.execute(
            "UPDATE users SET last_activity = ? WHERE email = ?",
            (now_str, clean_email)
        )
    return session_token


def validate_session_token(token: str) -> dict | None:
    """Validate a persistent session token against the database.
    Returns the user dict if valid and unexpired; None otherwise."""
    if not token or not isinstance(token, str):
        return None

    clean_token = token.strip()
    now_str = datetime.now(timezone.utc).isoformat()

    try:
        with _conn() as conn:
            row = conn.execute(
                """SELECT s.session_token, s.expires_at, s.is_active,
                          u.id as user_id, u.email, u.name, u.student_id, u.login_count,
                          u.last_login, u.last_activity
                   FROM user_sessions s
                   JOIN users u ON s.user_email = u.email
                   WHERE s.session_token = ? AND s.is_active = 1""",
                (clean_token,)
            ).fetchone()

            if not row:
                return None

            # Check expiration
            expires_at = row["expires_at"]
            if expires_at and expires_at < now_str:
                # Expired session
                conn.execute(
                    "UPDATE user_sessions SET is_active = 0 WHERE session_token = ?",
                    (clean_token,)
                )
                return None

            # Update session and user activity
            conn.execute(
                "UPDATE user_sessions SET last_activity = ? WHERE session_token = ?",
                (now_str, clean_token)
            )
            conn.execute(
                "UPDATE users SET last_activity = ? WHERE email = ?",
                (now_str, row["email"])
            )

            return dict(row)
    except Exception:
        return None


def revoke_session_token(token: str):
    """Revoke a single session token (called during logout)."""
    if not token:
        return
    try:
        with _conn() as conn:
            conn.execute(
                "UPDATE user_sessions SET is_active = 0 WHERE session_token = ?",
                (token.strip(),)
            )
    except Exception:
        pass


def revoke_all_user_sessions(email: str):
    """Revoke all active sessions for a given user."""
    try:
        with _conn() as conn:
            conn.execute(
                "UPDATE user_sessions SET is_active = 0 WHERE user_email = ?",
                (email.strip().lower(),)
            )
    except Exception:
        pass


# ─────────────────────────────────────────────
# USER ACTIVITY TRACKING
# ─────────────────────────────────────────────
def update_user_activity(email: str):
    """Update last_activity timestamp for a user.
    Called whenever the user interacts with the app."""
    if not email:
        return
    clean_email = email.strip().lower()
    now_str = datetime.now(timezone.utc).isoformat()
    try:
        with _conn() as conn:
            conn.execute(
                "UPDATE users SET last_activity = ? WHERE email = ?",
                (now_str, clean_email)
            )
    except Exception:
        pass


# ─────────────────────────────────────────────
# PUSH NOTIFICATION SUBSCRIPTIONS
# ─────────────────────────────────────────────
def save_push_subscription(email: str, endpoint: str, p256dh: str, auth: str):
    """Store or update a browser push subscription for a user."""
    clean_email = email.strip().lower()
    now_str = datetime.now(timezone.utc).isoformat()
    with _conn() as conn:
        conn.execute(
            """INSERT INTO push_subscriptions (user_email, endpoint, p256dh, auth, created_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(endpoint) DO UPDATE SET
                   user_email = excluded.user_email,
                   p256dh = excluded.p256dh,
                   auth = excluded.auth,
                   created_at = excluded.created_at""",
            (clean_email, endpoint.strip(), p256dh.strip(), auth.strip(), now_str)
        )


def get_user_push_subscriptions(email: str) -> list[dict]:
    """Retrieve all push subscriptions for a user."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM push_subscriptions WHERE user_email = ?",
            (email.strip().lower(),)
        ).fetchall()
    return [dict(r) for r in rows]


def delete_push_subscription(endpoint: str):
    """Remove an expired or invalid push subscription."""
    with _conn() as conn:
        conn.execute(
            "DELETE FROM push_subscriptions WHERE endpoint = ?",
            (endpoint.strip(),)
        )


# ─────────────────────────────────────────────
# INACTIVITY AUDIT & NOTIFICATION LOGS
# ─────────────────────────────────────────────
def get_inactive_users(inactivity_days: int = 7) -> list[dict]:
    """
    Find users who:
    1. Have last_activity older than `inactivity_days` days (or last_login if last_activity is null).
    2. Have NOT already received a reminder for this inactivity cycle
       (i.e., last_reminder_sent is NULL or last_reminder_sent < last_activity).
    3. Are active users (is_active = 1).
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=inactivity_days)).isoformat()
    with _conn() as conn:
        query = """
        SELECT id, email, name, student_id, login_count, last_login, last_activity, last_reminder_sent
        FROM users
        WHERE is_active = 1
          AND COALESCE(last_activity, last_login, created_at) <= ?
          AND (
              last_reminder_sent IS NULL
              OR last_reminder_sent < COALESCE(last_activity, last_login, created_at)
          )
        ORDER BY last_activity ASC
        """
        rows = conn.execute(query, (cutoff,)).fetchall()
    return [dict(r) for r in rows]


def record_notification_sent(email: str, notification_type: str, channel: str = "webpush",
                            status: str = "sent", details: str = ""):
    """Record a dispatched reminder in notification_logs and update users.last_reminder_sent."""
    clean_email = email.strip().lower()
    now_str = datetime.now(timezone.utc).isoformat()
    with _conn() as conn:
        conn.execute(
            """INSERT INTO notification_logs (user_email, notification_type, channel, status, details, sent_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (clean_email, notification_type, channel, status, details, now_str)
        )
        if status == "sent":
            conn.execute(
                "UPDATE users SET last_reminder_sent = ? WHERE email = ?",
                (now_str, clean_email)
            )


def get_recent_notification_logs(limit: int = 50) -> list[dict]:
    """Fetch latest notification logs."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM notification_logs ORDER BY sent_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────
# VAPID KEY GENERATION & STORAGE
# ─────────────────────────────────────────────
def get_or_create_vapid_keys() -> tuple[str, str, str]:
    """
    Retrieve existing VAPID keys from environment or app_settings,
    or generate a fresh VAPID keypair if none exists.
    Returns (public_key_b64, private_key_pem, claim_email)
    """
    env_pub = os.getenv("VAPID_PUBLIC_KEY", "")
    env_priv = os.getenv("VAPID_PRIVATE_KEY", "")
    env_email = os.getenv("VAPID_CLAIM_EMAIL", "mailto:admin@studyhelper.ai")

    if env_pub and env_priv:
        return env_pub, env_priv, env_email

    stored_pub = get_app_setting("vapid_public_key")
    stored_priv = get_app_setting("vapid_private_key")
    stored_email = get_app_setting("vapid_claim_email", "mailto:admin@studyhelper.ai")

    if stored_pub and stored_priv:
        return stored_pub, stored_priv, stored_email

    # Generate new VAPID keys using py_vapid / cryptography
    try:
        from py_vapid import Vapid
        vapid = Vapid()
        vapid.generate_keys()
        import base64
        from cryptography.hazmat.primitives import serialization
        raw_pub = vapid.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        pub_b64 = base64.urlsafe_b64encode(raw_pub).decode("utf-8").rstrip("=")
        priv_pem = vapid.private_pem().decode("utf-8")

        set_app_setting("vapid_public_key", pub_b64)
        set_app_setting("vapid_private_key", priv_pem)
        set_app_setting("vapid_claim_email", env_email)

        return pub_b64, priv_pem, env_email
    except Exception as e:
        return "", "", env_email


# ─────────────────────────────────────────────
# DOCUMENTS
# ─────────────────────────────────────────────
def save_document(user_email: str, filename: str, course: str, doc_text: str) -> int:
    """Save document and return its ID."""
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO documents (user_email, filename, course, doc_text) VALUES (?, ?, ?, ?)",
            (user_email.strip().lower(), filename, course, doc_text)
        )
        doc_id = cur.lastrowid
    update_user_activity(user_email)
    return doc_id


def get_user_documents(user_email: str) -> list[dict]:
    """Get all documents for a user, newest first."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, filename, course, uploaded_at FROM documents WHERE user_email = ? ORDER BY uploaded_at DESC",
            (user_email.strip().lower(),)
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
    clean_email = user_email.strip().lower()
    with _conn() as conn:
        # Delete old result for same doc if re-processing
        conn.execute("DELETE FROM results WHERE doc_id = ?", (doc_id,))
        conn.execute(
            """INSERT INTO results (user_email, doc_id, course, summary, flashcards, quiz, study_plan)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (clean_email, doc_id, course,
             summary,
             json.dumps(flashcards),
             json.dumps(quiz),
             json.dumps(study_plan))
        )
    update_user_activity(clean_email)


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
# DELETE DOCUMENT
# ─────────────────────────────────────────────
def delete_document(user_email: str, doc_id: int):
    """Permanently delete a document and everything tied to it
    (generated results, chat history). Scoped to user_email so a
    user can only ever delete their own documents."""
    clean_email = user_email.strip().lower()
    with _conn() as conn:
        conn.execute("DELETE FROM documents WHERE id = ? AND user_email = ?", (doc_id, clean_email))
        conn.execute("DELETE FROM results WHERE doc_id = ?", (doc_id,))
        conn.execute("DELETE FROM chat_history WHERE doc_id = ? AND user_email = ?", (doc_id, clean_email))
    update_user_activity(clean_email)


# ─────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────
def save_message(user_email: str, doc_id: int, role: str, content: str):
    clean_email = user_email.strip().lower()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO chat_history (user_email, doc_id, role, content) VALUES (?, ?, ?, ?)",
            (clean_email, doc_id, role, content)
        )
    update_user_activity(clean_email)


def get_chat_history(user_email: str, doc_id: int) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT role, content FROM chat_history WHERE user_email = ? AND doc_id = ? ORDER BY created_at ASC",
            (user_email.strip().lower(), doc_id)
        ).fetchall()
    return [dict(r) for r in rows]


def clear_chat_history(user_email: str, doc_id: int):
    clean_email = user_email.strip().lower()
    with _conn() as conn:
        conn.execute(
            "DELETE FROM chat_history WHERE user_email = ? AND doc_id = ?",
            (clean_email, doc_id)
        )
    update_user_activity(clean_email)