"""
Supabase database layer for Agentic AI Study Helper.

Handles:
- users
- persistent sessions
- documents
- generated results
- chat history
- push notification subscriptions
- notification logs
- app settings
- onboarding state

The application uses Supabase as the shared cloud database so that
users can access their accounts and data from different laptops/devices.
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from supabase import create_client, Client


# ============================================================
# ENVIRONMENT / SUPABASE CONNECTION
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

if not SUPABASE_URL:
    raise RuntimeError(
        "SUPABASE_URL is missing. Please add it to your .env file."
    )

if not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_KEY is missing. Please add it to your .env file."
    )


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ============================================================
# HELPERS
# ============================================================

def _now() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def _clean_email(email: str) -> str:
    """Normalize email address."""
    return email.strip().lower()


def _hash(password: str) -> str:
    """Hash password using SHA-256.

    Kept compatible with the previous SQLite implementation so
    existing password logic remains unchanged.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _first(data):
    """Return first row from a Supabase response or None."""
    if not data:
        return None
    return data[0]


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():
    """
    Supabase tables are created from the Supabase SQL Editor.

    This function intentionally does not create SQLite tables.
    It is kept so existing app.py code can continue calling init_db().
    """
    return True


# ============================================================
# APP SETTINGS / ONBOARDING
# ============================================================

def is_onboarding_completed() -> bool:
    """Return True if onboarding has been completed."""
    try:
        response = (
            supabase
            .table("app_settings")
            .select("value")
            .eq("key", "onboarding_completed")
            .limit(1)
            .execute()
        )

        row = _first(response.data)

        return bool(row and row.get("value") == "1")

    except Exception:
        return False


def set_onboarding_completed():
    """Mark onboarding as completed."""
    try:
        (
            supabase
            .table("app_settings")
            .upsert(
                {
                    "key": "onboarding_completed",
                    "value": "1"
                },
                on_conflict="key"
            )
            .execute()
        )
    except Exception:
        pass


def get_app_setting(key: str, default: str = "") -> str:
    """Get an application setting."""
    try:
        response = (
            supabase
            .table("app_settings")
            .select("value")
            .eq("key", key)
            .limit(1)
            .execute()
        )

        row = _first(response.data)

        if row:
            return row.get("value", default)

        return default

    except Exception:
        return default


def set_app_setting(key: str, value: str):
    """Save an application setting."""
    try:
        (
            supabase
            .table("app_settings")
            .upsert(
                {
                    "key": key,
                    "value": value
                },
                on_conflict="key"
            )
            .execute()
        )
    except Exception:
        pass


# ============================================================
# AUTHENTICATION
# ============================================================

def register_user(
    email: str,
    password: str,
    name: str,
    student_id: str = ""
) -> tuple[bool, str]:
    """
    Create a new user.

    Returns:
        (True, success_message)
        (False, error_message)
    """

    clean_email = _clean_email(email)

    try:
        # Check whether account already exists.
        existing = (
            supabase
            .table("users")
            .select("id")
            .eq("email", clean_email)
            .limit(1)
            .execute()
        )

        if existing.data:
            return False, "An account with this email already exists."

        now = _now()

        data = {
            "email": clean_email,
            "password": _hash(password),
            "name": name.strip(),
            "student_id": student_id.strip() if student_id else "",
            "login_count": 0,
            "last_activity": now,
            "is_active": True,
        }

        response = (
            supabase
            .table("users")
            .insert(data)
            .execute()
        )

        if not response.data:
            return False, "Unable to create account."

        return True, "Account created successfully."

    except Exception as e:
        error = str(e)

        if "duplicate" in error.lower():
            return False, "An account with this email already exists."

        return False, f"Registration error: {error}"


def login_user(email: str, password: str) -> tuple[bool, dict | str]:
    """
    Authenticate user.

    Returns exactly the format expected by the existing login page:

        (True, user_dict)

    or

        (False, error_message)
    """

    clean_email = _clean_email(email)

    try:
        response = (
            supabase
            .table("users")
            .select("*")
            .eq("email", clean_email)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )

        row = _first(response.data)

        if not row:
            return False, "No account found with this email."

        if row.get("password") != _hash(password):
            return False, "Incorrect password."

        return True, dict(row)

    except Exception as e:
        return False, f"Login error: {e}"


def record_login(email: str) -> bool:
    """
    Increment login count and update login/activity timestamps.

    Returns True if this was the user's first login.
    """

    clean_email = _clean_email(email)

    try:
        response = (
            supabase
            .table("users")
            .select("login_count")
            .eq("email", clean_email)
            .limit(1)
            .execute()
        )

        row = _first(response.data)

        if not row:
            return False

        current_count = row.get("login_count", 0) or 0
        is_first_login = current_count == 0

        now = _now()

        (
            supabase
            .table("users")
            .update(
                {
                    "login_count": current_count + 1,
                    "last_login": now,
                    "last_activity": now
                }
            )
            .eq("email", clean_email)
            .execute()
        )

        return is_first_login

    except Exception:
        return False


# ============================================================
# PERSISTENT SESSIONS
# ============================================================

def create_user_session(
    email: str,
    days_valid: int = 30
) -> str:
    """Create a persistent login session."""

    clean_email = _clean_email(email)

    session_token = secrets.token_urlsafe(32)

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=days_valid)

    now_str = now.isoformat()
    expires_str = expires_at.isoformat()

    (
        supabase
        .table("user_sessions")
        .insert(
            {
                "user_email": clean_email,
                "session_token": session_token,
                "created_at": now_str,
                "last_activity": now_str,
                "expires_at": expires_str,
                "is_active": True
            }
        )
        .execute()
    )

    (
        supabase
        .table("users")
        .update(
            {
                "last_activity": now_str
            }
        )
        .eq("email", clean_email)
        .execute()
    )

    return session_token


def validate_session_token(token: str) -> dict | None:
    """Validate persistent session token."""

    if not token or not isinstance(token, str):
        return None

    clean_token = token.strip()
    now = datetime.now(timezone.utc)

    try:
        response = (
            supabase
            .table("user_sessions")
            .select(
                "session_token, expires_at, is_active, "
                "users(id,email,name,student_id,login_count,last_login,last_activity)"
            )
            .eq("session_token", clean_token)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )

        row = _first(response.data)

        if not row:
            return None

        expires_at_text = row.get("expires_at")

        if expires_at_text:
            expires_at = datetime.fromisoformat(
                expires_at_text.replace("Z", "+00:00")
            )

            if expires_at < now:
                (
                    supabase
                    .table("user_sessions")
                    .update({"is_active": False})
                    .eq("session_token", clean_token)
                    .execute()
                )

                return None

        now_str = now.isoformat()

        (
            supabase
            .table("user_sessions")
            .update(
                {
                    "last_activity": now_str
                }
            )
            .eq("session_token", clean_token)
            .execute()
        )

        user = row.get("users")

        if isinstance(user, list):
            user = _first(user)

        if not user:
            return None

        (
            supabase
            .table("users")
            .update(
                {
                    "last_activity": now_str
                }
            )
            .eq("email", user["email"])
            .execute()
        )

        return {
            "session_token": row.get("session_token"),
            "expires_at": row.get("expires_at"),
            "is_active": row.get("is_active"),
            "user_id": user.get("id"),
            "email": user.get("email"),
            "name": user.get("name"),
            "student_id": user.get("student_id"),
            "login_count": user.get("login_count"),
            "last_login": user.get("last_login"),
            "last_activity": user.get("last_activity"),
        }

    except Exception:
        return None


def revoke_session_token(token: str):
    """Revoke one session."""
    if not token:
        return

    try:
        (
            supabase
            .table("user_sessions")
            .update({"is_active": False})
            .eq("session_token", token.strip())
            .execute()
        )
    except Exception:
        pass


def revoke_all_user_sessions(email: str):
    """Revoke all sessions for a user."""
    try:
        (
            supabase
            .table("user_sessions")
            .update({"is_active": False})
            .eq("user_email", _clean_email(email))
            .execute()
        )
    except Exception:
        pass


# ============================================================
# USER ACTIVITY
# ============================================================

def update_user_activity(email: str):
    """Update user's last activity."""
    if not email:
        return

    try:
        (
            supabase
            .table("users")
            .update(
                {
                    "last_activity": _now()
                }
            )
            .eq("email", _clean_email(email))
            .execute()
        )
    except Exception:
        pass


# ============================================================
# PUSH NOTIFICATIONS
# ============================================================

def save_push_subscription(
    email: str,
    endpoint: str,
    p256dh: str,
    auth: str
):
    """Save or update browser push subscription."""

    clean_email = _clean_email(email)

    data = {
        "user_email": clean_email,
        "endpoint": endpoint.strip(),
        "p256dh": p256dh.strip(),
        "auth": auth.strip(),
        "created_at": _now()
    }

    (
        supabase
        .table("push_subscriptions")
        .upsert(
            data,
            on_conflict="endpoint"
        )
        .execute()
    )


def get_user_push_subscriptions(email: str) -> list[dict]:
    """Get push subscriptions for a user."""

    response = (
        supabase
        .table("push_subscriptions")
        .select("*")
        .eq("user_email", _clean_email(email))
        .execute()
    )

    return response.data or []


def delete_push_subscription(endpoint: str):
    """Delete push subscription."""

    (
        supabase
        .table("push_subscriptions")
        .delete()
        .eq("endpoint", endpoint.strip())
        .execute()
    )


# ============================================================
# INACTIVITY / NOTIFICATIONS
# ============================================================

def get_inactive_users(
    inactivity_days: int = 7
) -> list[dict]:
    """Find users inactive for specified number of days."""

    cutoff = (
        datetime.now(timezone.utc)
        - timedelta(days=inactivity_days)
    ).isoformat()

    try:
        response = (
            supabase
            .table("users")
            .select(
                "id,email,name,student_id,login_count,"
                "last_login,last_activity,last_reminder_sent"
            )
            .eq("is_active", True)
            .execute()
        )

        users = response.data or []

        inactive = []

        for user in users:
            activity = (
                user.get("last_activity")
                or user.get("last_login")
            )

            if not activity:
                continue

            if activity <= cutoff:
                reminder = user.get("last_reminder_sent")

                if not reminder or reminder < activity:
                    inactive.append(user)

        inactive.sort(
            key=lambda x: x.get("last_activity") or ""
        )

        return inactive

    except Exception:
        return []


def record_notification_sent(
    email: str,
    notification_type: str,
    channel: str = "webpush",
    status: str = "sent",
    details: str = ""
):
    """Record notification and update reminder timestamp."""

    clean_email = _clean_email(email)
    now = _now()

    try:
        (
            supabase
            .table("notification_logs")
            .insert(
                {
                    "user_email": clean_email,
                    "notification_type": notification_type,
                    "channel": channel,
                    "status": status,
                    "details": details,
                    "sent_at": now
                }
            )
            .execute()
        )

        if status == "sent":
            (
                supabase
                .table("users")
                .update(
                    {
                        "last_reminder_sent": now
                    }
                )
                .eq("email", clean_email)
                .execute()
            )

    except Exception:
        pass


def get_recent_notification_logs(
    limit: int = 50
) -> list[dict]:
    """Get recent notification logs."""

    response = (
        supabase
        .table("notification_logs")
        .select("*")
        .order("sent_at", desc=True)
        .limit(limit)
        .execute()
    )

    return response.data or []


# ============================================================
# VAPID KEYS
# ============================================================

def get_or_create_vapid_keys() -> tuple[str, str, str]:
    """
    Retrieve VAPID keys from environment or Supabase settings.
    Generate them if necessary.
    """

    env_pub = os.getenv("VAPID_PUBLIC_KEY", "")
    env_priv = os.getenv("VAPID_PRIVATE_KEY", "")
    env_email = os.getenv(
        "VAPID_CLAIM_EMAIL",
        "mailto:admin@studyhelper.ai"
    )

    if env_pub and env_priv:
        return env_pub, env_priv, env_email

    stored_pub = get_app_setting("vapid_public_key")
    stored_priv = get_app_setting("vapid_private_key")
    stored_email = get_app_setting(
        "vapid_claim_email",
        env_email
    )

    if stored_pub and stored_priv:
        return stored_pub, stored_priv, stored_email

    try:
        from py_vapid import Vapid
        import base64

        from cryptography.hazmat.primitives import serialization

        vapid = Vapid()
        vapid.generate_keys()

        raw_pub = vapid.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )

        pub_b64 = base64.urlsafe_b64encode(
            raw_pub
        ).decode("utf-8").rstrip("=")

        priv_pem = vapid.private_pem().decode("utf-8")

        set_app_setting(
            "vapid_public_key",
            pub_b64
        )

        set_app_setting(
            "vapid_private_key",
            priv_pem
        )

        set_app_setting(
            "vapid_claim_email",
            env_email
        )

        return pub_b64, priv_pem, env_email

    except Exception:
        return "", "", env_email


# ============================================================
# DOCUMENTS
# ============================================================

def save_document(
    user_email: str,
    filename: str,
    course: str,
    doc_text: str
) -> int:
    """Save document and return its ID."""

    clean_email = _clean_email(user_email)

    response = (
        supabase
        .table("documents")
        .insert(
            {
                "user_email": clean_email,
                "filename": filename,
                "course": course,
                "doc_text": doc_text
            }
        )
        .execute()
    )

    row = _first(response.data)

    if not row:
        raise RuntimeError(
            "Failed to save document."
        )

    update_user_activity(clean_email)

    return int(row["id"])


def get_user_documents(
    user_email: str
) -> list[dict]:
    """Get all documents for a user."""

    response = (
        supabase
        .table("documents")
        .select(
            "id,filename,course,uploaded_at"
        )
        .eq(
            "user_email",
            _clean_email(user_email)
        )
        .order(
            "uploaded_at",
            desc=True
        )
        .execute()
    )

    return response.data or []


def get_document_text(doc_id: int) -> str:
    """Get document text by ID."""

    response = (
        supabase
        .table("documents")
        .select("doc_text")
        .eq("id", doc_id)
        .limit(1)
        .execute()
    )

    row = _first(response.data)

    return row.get("doc_text", "") if row else ""


# ============================================================
# RESULTS
# ============================================================

def save_results(
    user_email: str,
    doc_id: int,
    course: str,
    summary: str,
    flashcards: list,
    quiz: list,
    study_plan: list
):
    """Save generated AI results."""

    clean_email = _clean_email(user_email)

    # Remove previous results for this document.
    (
        supabase
        .table("results")
        .delete()
        .eq("doc_id", doc_id)
        .execute()
    )

    (
        supabase
        .table("results")
        .insert(
            {
                "user_email": clean_email,
                "doc_id": doc_id,
                "course": course,
                "summary": summary,
                "flashcards": flashcards,
                "quiz": quiz,
                "study_plan": study_plan
            }
        )
        .execute()
    )

    update_user_activity(clean_email)


def get_results(
    doc_id: int
) -> dict | None:
    """Get generated results for a document."""

    response = (
        supabase
        .table("results")
        .select("*")
        .eq("doc_id", doc_id)
        .limit(1)
        .execute()
    )

    row = _first(response.data)

    if not row:
        return None

    result = dict(row)

    # Supabase JSONB normally returns Python lists/dicts.
    # These checks also support old string-style JSON values.
    for key in ["flashcards", "quiz", "study_plan"]:
        value = result.get(key)

        if isinstance(value, str):
            try:
                result[key] = json.loads(value)
            except Exception:
                result[key] = []

        elif value is None:
            result[key] = []

    return result


def update_study_plan(
    doc_id: int,
    study_plan: list
):
    """Update study plan."""

    (
        supabase
        .table("results")
        .update(
            {
                "study_plan": study_plan
            }
        )
        .eq("doc_id", doc_id)
        .execute()
    )


# ============================================================
# DELETE DOCUMENT
# ============================================================

def delete_document(
    user_email: str,
    doc_id: int
):
    """
    Delete a user's document.

    Results and chat history are deleted explicitly before
    deleting the document.
    """

    clean_email = _clean_email(user_email)

    (
        supabase
        .table("results")
        .delete()
        .eq("doc_id", doc_id)
        .eq("user_email", clean_email)
        .execute()
    )

    (
        supabase
        .table("chat_history")
        .delete()
        .eq("doc_id", doc_id)
        .eq("user_email", clean_email)
        .execute()
    )

    (
        supabase
        .table("documents")
        .delete()
        .eq("id", doc_id)
        .eq("user_email", clean_email)
        .execute()
    )

    update_user_activity(clean_email)


# ============================================================
# CHAT HISTORY
# ============================================================

def save_message(
    user_email: str,
    doc_id: int,
    role: str,
    content: str
):
    """Save chat message."""

    clean_email = _clean_email(user_email)

    (
        supabase
        .table("chat_history")
        .insert(
            {
                "user_email": clean_email,
                "doc_id": doc_id,
                "role": role,
                "content": content
            }
        )
        .execute()
    )

    update_user_activity(clean_email)


def get_chat_history(
    user_email: str,
    doc_id: int
) -> list[dict]:
    """Get chat history for a document."""

    response = (
        supabase
        .table("chat_history")
        .select("role,content")
        .eq(
            "user_email",
            _clean_email(user_email)
        )
        .eq(
            "doc_id",
            doc_id
        )
        .order(
            "created_at",
            desc=False
        )
        .execute()
    )

    return response.data or []


def clear_chat_history(
    user_email: str,
    doc_id: int
):
    """Delete chat history for a document."""

    clean_email = _clean_email(user_email)

    (
        supabase
        .table("chat_history")
        .delete()
        .eq("user_email", clean_email)
        .eq("doc_id", doc_id)
        .execute()
    )

    update_user_activity(clean_email)