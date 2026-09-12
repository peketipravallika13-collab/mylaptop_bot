"""SQLite database persistence for Command History and Assistant Memory."""
import sqlite3
import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from config.settings import DB_PATH


class MemoryDatabase:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create necessary tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Commands History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    raw_command TEXT NOT NULL,
                    category TEXT,
                    action_plan TEXT,
                    status TEXT NOT NULL, -- 'SUCCESS', 'FAILED', 'CANCELLED', 'REQUIRES_CONFIRMATION'
                    result_message TEXT,
                    execution_time_ms INTEGER DEFAULT 0
                )
            """)

            # Key-Value Memory / Context Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_memory (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def log_command(
        self,
        raw_command: str,
        category: str,
        action_plan: str,
        status: str,
        result_message: str,
        execution_time_ms: int = 0
    ) -> int:
        """Log a user command and its result with privacy sanitization."""
        from safety.privacy_guard import privacy_guard
        clean_raw = privacy_guard.sanitize_log(raw_command)
        clean_msg = privacy_guard.sanitize_log(result_message)
        timestamp = datetime.datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO command_history (timestamp, raw_command, category, action_plan, status, result_message, execution_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, clean_raw, category, action_plan, status, clean_msg, execution_time_ms))
            conn.commit()
            return cursor.lastrowid

    def get_recent_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent command executions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, raw_command, category, status, result_message, execution_time_ms
                FROM command_history
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def set_context(self, key: str, value: str):
        """Store a context variable."""
        updated_at = datetime.datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO context_memory (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            """, (key, value, updated_at))
            conn.commit()

    def get_context(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a context variable."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM context_memory WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return row["value"]
            return default


# Singleton instance
memory_db = MemoryDatabase()
