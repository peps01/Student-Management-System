import sqlite3
from typing import Optional
from .interface import Repository


class SqliteRepository(Repository):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
        self._seed_if_empty()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    bio TEXT DEFAULT '',
                    role TEXT DEFAULT 'Student',
                    join_date TEXT DEFAULT (date('now')),
                    password TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS dashboard_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_name TEXT NOT NULL UNIQUE,
                    stat_value INTEGER NOT NULL DEFAULT 0
                );
            """)

    def _seed_if_empty(self):
        with self._connect() as conn:
            if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
                return
            self._seed(conn)

    def _seed(self, conn):
        conn.execute(
            "INSERT INTO users (username, name, email, password, bio, role) VALUES (?, ?, ?, ?, ?, ?)",
            ("admin", "Admin User", "admin@school.edu", "admin123",
             "System administrator.", "Administrator")
        )
        conn.execute(
            "INSERT INTO users (username, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
            ("mario", "Prof. Mario Santos", "mario@school.edu", "faculty123", "Faculty")
        )
        conn.execute(
            "INSERT INTO users (username, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
            ("2026-0004", "Ana Ramirez", "ana@email.com", "student123", "Student")
        )

        stats = [
            ("total_students", 1250),
            ("total_faculties", 85),
            ("total_offerings", 42),
            ("pending_enrollments", 18),
        ]
        for name, val in stats:
            conn.execute(
                "INSERT INTO dashboard_stats (stat_name, stat_value) VALUES (?, ?)",
                (name, val)
            )
        conn.commit()

    def get_user(self, username: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT username, name, email, bio, role, join_date, password FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            return dict(row) if row else None

    def create_user(self, username: str, name: str, email: str, password: str, role: str = "Student") -> dict:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO users (username, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
                (username, name, email, password, role),
            )
            conn.commit()
            return {
                "username": username,
                "name": name,
                "email": email,
                "role": role,
            }

    def get_dashboard_stats(self) -> dict:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT stat_name, stat_value FROM dashboard_stats"
            ).fetchall()
            return {row["stat_name"]: row["stat_value"] for row in rows}
