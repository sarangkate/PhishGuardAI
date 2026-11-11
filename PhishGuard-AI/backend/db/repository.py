"""Small SQLite repository for privacy-conscious analysis metadata."""
from __future__ import annotations

from typing import Any, Dict, List
import sqlite3

from backend.db.database import DB_PATH, initialize_database


def _connect() -> sqlite3.Connection:
    initialize_database()
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def ensure_user(provider_subject: str) -> int:
    if not provider_subject:
        raise ValueError("provider_subject is required")
    with _connect() as connection:
        connection.execute(
            "INSERT INTO users(provider_subject) VALUES (?) ON CONFLICT(provider_subject) DO NOTHING",
            (provider_subject,),
        )
        row = connection.execute(
            "SELECT id FROM users WHERE provider_subject = ?", (provider_subject,)
        ).fetchone()
        return int(row["id"])


def mark_connection(user_id: int, provider: str = "google") -> None:
    with _connect() as connection:
        connection.execute(
            "UPDATE account_connections SET disconnected_at = CURRENT_TIMESTAMP "
            "WHERE user_id = ? AND provider = ? AND disconnected_at IS NULL",
            (user_id, provider),
        )
        connection.execute(
            "INSERT INTO account_connections(user_id, provider) VALUES (?, ?)",
            (user_id, provider),
        )


def save_analysis(
    user_id: int,
    message_id: str,
    sender: str,
    subject: str,
    message_date: str,
    classification: str,
    risk_score: int | None,
    trust_score: int | None,
    evidence: List[Dict[str, Any]],
) -> int:
    """Upsert metadata for one user's message and replace its findings.

    No body, raw MIME, headers, OAuth token, or URL is persisted.
    """
    with _connect() as connection:
        row = connection.execute(
            "SELECT id FROM analyses WHERE user_id = ? AND external_message_id = ?",
            (user_id, message_id),
        ).fetchone()
        if row:
            analysis_id = int(row["id"])
            connection.execute(
                """UPDATE analyses SET sender=?, subject=?, message_date=?, classification=?,
                   risk_score=?, trust_score=?, analyzed_at=CURRENT_TIMESTAMP
                   WHERE id=? AND user_id=?""",
                (sender, subject, message_date, classification, risk_score, trust_score, analysis_id, user_id),
            )
            connection.execute("DELETE FROM findings WHERE analysis_id = ?", (analysis_id,))
        else:
            cursor = connection.execute(
                """INSERT INTO analyses
                   (user_id, external_message_id, sender, subject, message_date,
                    classification, risk_score, trust_score)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, message_id, sender, subject, message_date, classification, risk_score, trust_score),
            )
            analysis_id = int(cursor.lastrowid)

        for item in evidence:
            connection.execute(
                """INSERT INTO findings(analysis_id, finding_code, category, severity, title)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    analysis_id,
                    str(item.get("id", "unknown")),
                    str(item.get("category", "unknown")),
                    str(item.get("severity", "low")),
                    str(item.get("title", "Security indicator")),
                ),
            )
        return analysis_id


def list_history(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    limit = max(1, min(int(limit), 100))
    with _connect() as connection:
        rows = connection.execute(
            """SELECT id, external_message_id AS message_id, sender, subject, message_date AS date,
                      classification, risk_score, trust_score, analyzed_at
               FROM analyses WHERE user_id = ? ORDER BY analyzed_at DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]


def clear_history(user_id: int) -> int:
    with _connect() as connection:
        cursor = connection.execute("DELETE FROM analyses WHERE user_id = ?", (user_id,))
        return cursor.rowcount


def purge_expired(retention_days: int = 30) -> int:
    from backend.db.database import purge_expired_history
    return purge_expired_history(retention_days)
