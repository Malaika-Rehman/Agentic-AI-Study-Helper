"""
Inactivity Notification Background Worker.
Can be executed as a standalone CLI command, Cron job, Windows Task Scheduler task,
or continuous background daemon.

Usage Examples:
    # Run a single inactivity check and exit (ideal for cron or Task Scheduler):
    python inactivity_worker.py --check-now

    # Run continuously as a background service checking every 1 hour (3600s):
    python inactivity_worker.py --daemon --interval 3600

    # Dry-run mode (list inactive users without sending reminders):
    python inactivity_worker.py --dry-run

    # Custom inactivity threshold (e.g. 5 days):
    python inactivity_worker.py --days 5 --check-now
"""
import sys
import os
import time
import argparse
from datetime import datetime, timezone
from dotenv import load_dotenv

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
load_dotenv()

from data.database import (
    init_db,
    get_inactive_users,
    get_recent_notification_logs,
)
from components.notification_manager import dispatch_inactivity_notification


def run_inactivity_check(inactivity_days: int = 7, dry_run: bool = False):
    """
    Perform a complete scan for users inactive for >= inactivity_days.
    Dispatches notifications and avoids sending duplicate reminders for the same inactive period.
    """
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"\n[{now_utc}] 🔍 Checking for inactive users (threshold: {inactivity_days} days)...")

    init_db()
    inactive_users = get_inactive_users(inactivity_days=inactivity_days)

    if not inactive_users:
        print(f"[{now_utc}] ✅ No users meet the inactivity criteria (0 notifications needed).")
        return 0

    print(f"[{now_utc}] 🔔 Found {len(inactive_users)} inactive user(s) requiring reminders:")

    processed_count = 0
    for user in inactive_users:
        email = user["email"]
        name = user.get("name", "Student")
        last_act = user.get("last_activity") or user.get("last_login") or "Never"
        last_rem = user.get("last_reminder_sent") or "None"

        print(f"  • {name} ({email}) | Last Activity: {last_act} | Previous Reminder: {last_rem}")

        if dry_run:
            print("    ↳ [DRY-RUN] Skipped dispatch.")
            continue

        success = dispatch_inactivity_notification(user)
        if success:
            print(f"    ↳ ✅ Dispatched inactivity reminder to {email}.")
            processed_count += 1
        else:
            print(f"    ↳ ⚠️ Failed or queued notification for {email}.")

    print(f"[{now_utc}] 🏁 Finished. Processed {processed_count} notification(s).\n")
    return processed_count


def start_daemon(interval_seconds: int = 3600, inactivity_days: int = 7):
    """
    Run in an infinite polling loop as a background service.
    """
    print(f"🚀 Starting Inactivity Notification Daemon (polling every {interval_seconds}s, threshold {inactivity_days} days)...")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            run_inactivity_check(inactivity_days=inactivity_days, dry_run=False)
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n🛑 Notification Daemon stopped by user.")


def main():
    parser = argparse.ArgumentParser(
        description="Agentic AI Study Helper Inactivity Notification Worker"
    )
    parser.add_argument(
        "--check-now",
        action="store_true",
        help="Run a single inactivity check and exit immediately (default action)",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run continuously as a background polling daemon",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Polling interval in seconds when running in daemon mode (default: 3600s / 1 hour)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Inactivity threshold in days (default: 7 days)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview inactive users without sending notifications",
    )
    parser.add_argument(
        "--logs",
        action="store_true",
        help="Display recent notification audit logs from the database",
    )

    args = parser.parse_args()

    if args.logs:
        init_db()
        logs = get_recent_notification_logs(limit=25)
        print("\n📜 Recent Notification Audit Logs:")
        if not logs:
            print("  No notification logs found.")
        for log in logs:
            print(f"  [{log['sent_at']}] {log['user_email']} | {log['notification_type']} | {log['channel']} | {log['status']} | {log.get('details', '')}")
        print()
        return

    if args.daemon:
        start_daemon(interval_seconds=args.interval, inactivity_days=args.days)
    else:
        run_inactivity_check(inactivity_days=args.days, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
