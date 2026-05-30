import sqlite3
import os
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
                    role TEXT DEFAULT 'Administrator',
                    join_date TEXT DEFAULT (date('now')),
                    password TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    course TEXT NOT NULL,
                    year INTEGER NOT NULL CHECK(year >= 1 AND year <= 5)
                );
                CREATE TABLE IF NOT EXISTS grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL UNIQUE,
                    math REAL DEFAULT 0,
                    english REAL DEFAULT 0,
                    science REAL DEFAULT 0,
                    history REAL DEFAULT 0,
                    pe REAL DEFAULT 0,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL UNIQUE,
                    mon TEXT DEFAULT 'Present',
                    tue TEXT DEFAULT 'Present',
                    wed TEXT DEFAULT 'Present',
                    thu TEXT DEFAULT 'Present',
                    fri TEXT DEFAULT 'Present',
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    author TEXT NOT NULL,
                    date TEXT NOT NULL
                );
            """)

    def _seed_if_empty(self):
        with self._connect() as conn:
            if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
                return
            self._seed(conn)

    def _seed(self, conn):
        conn.execute(
            "INSERT INTO users (username, name, email, password, bio) VALUES (?, ?, ?, ?, ?)",
            ("admin", "Admin User", "admin@school.edu", "admin123",
             "System administrator at Springdale School. Managing student records and academic operations.")
        )

        students_data = [
            ("Alice Johnson", "alice@school.edu", "Computer Science", 3),
            ("Bob Smith", "bob@school.edu", "Mathematics", 2),
            ("Carol Williams", "carol@school.edu", "Physics", 4),
            ("David Brown", "david@school.edu", "Computer Science", 1),
            ("Eva Martinez", "eva@school.edu", "Engineering", 3),
            ("Frank Garcia", "frank@school.edu", "Mathematics", 2),
            ("Grace Lee", "grace@school.edu", "Biology", 3),
            ("Henry Wilson", "henry@school.edu", "Computer Science", 4),
        ]

        grades_data = [
            (95, 88, 92, 85, 90),
            (72, 80, 68, 75, 88),
            (88, 92, 85, 90, 78),
            (65, 70, 72, 68, 95),
            (91, 85, 89, 82, 76),
            (78, 74, 80, 71, 84),
            (93, 96, 91, 94, 88),
            (58, 62, 55, 60, 70),
        ]

        import random
        for i, (name, email, course, year) in enumerate(students_data):
            cur = conn.execute(
                "INSERT INTO students (name, email, course, year) VALUES (?, ?, ?, ?)",
                (name, email, course, year),
            )
            sid = cur.lastrowid
            g = grades_data[i]
            conn.execute(
                "INSERT INTO grades (student_id, math, english, science, history, pe) VALUES (?, ?, ?, ?, ?, ?)",
                (sid, *g),
            )
            records = tuple(
                "Present" if random.random() > 0.2 else "Absent" for _ in range(5)
            )
            conn.execute(
                "INSERT INTO attendance (student_id, mon, tue, wed, thu, fri) VALUES (?, ?, ?, ?, ?, ?)",
                (sid, *records),
            )

        announcements_data = [
            ("Welcome to Springdale School",
             "We are excited to welcome all students and faculty to the new academic year. Please check your schedules and reach out to your advisors for any concerns.",
             "Admin User", "2026-05-20 09:00"),
            ("Midterm Exam Schedule",
             "Midterm examinations will begin on June 10. Please review the exam schedule posted on the bulletin board and prepare accordingly.",
             "Admin User", "2026-05-22 14:30"),
            ("Science Fair Announcement",
             "The annual Science Fair will be held on June 25. All students are encouraged to participate. Registration forms are available at the science department office.",
             "Admin User", "2026-05-25 10:15"),
        ]
        conn.executemany(
            "INSERT INTO announcements (title, body, author, date) VALUES (?, ?, ?, ?)",
            announcements_data,
        )
        conn.commit()

    # ---- Users ----

    def get_user(self, username: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT username, name, email, bio, role, join_date, password FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            if row is None:
                return None
            return dict(row)

    def update_user(self, username: str, data: dict) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE users SET name = ?, email = ?, bio = ? WHERE username = ?",
                (data["name"], data["email"], data.get("bio", ""), username),
            )
            conn.commit()
            return cur.rowcount > 0

    def change_password(self, username: str, current: str, new: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT password FROM users WHERE username = ?", (username,)
            ).fetchone()
            if row is None or row["password"] != current:
                return False
            conn.execute(
                "UPDATE users SET password = ? WHERE username = ?", (new, username)
            )
            conn.commit()
            return True

    # ---- Students ----

    def list_students(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, email, course, year FROM students ORDER BY id"
            ).fetchall()
            return [dict(r) for r in rows]

    def get_student(self, student_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, name, email, course, year FROM students WHERE id = ?",
                (student_id,),
            ).fetchone()
            return dict(row) if row else None

    def add_student(self, data: dict) -> dict:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO students (name, email, course, year) VALUES (?, ?, ?, ?)",
                (data["name"], data["email"], data["course"], data["year"]),
            )
            sid = cur.lastrowid
            conn.execute(
                "INSERT INTO grades (student_id) VALUES (?)", (sid,)
            )
            conn.execute(
                "INSERT INTO attendance (student_id) VALUES (?)", (sid,)
            )
            conn.commit()
            return {"id": sid, **{k: data[k] for k in ("name", "email", "course", "year")}}

    def update_student(self, student_id: int, data: dict) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE students SET name = ?, email = ?, course = ?, year = ? WHERE id = ?",
                (data["name"], data["email"], data["course"], data["year"], student_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def delete_student(self, student_id: int) -> bool:
        with self._connect() as conn:
            conn.execute("DELETE FROM grades WHERE student_id = ?", (student_id,))
            conn.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
            cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()
            return cur.rowcount > 0

    # ---- Grades ----

    def list_grades(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT g.student_id, s.name, g.math, g.english, g.science, g.history, g.pe
                FROM grades g
                JOIN students s ON s.id = g.student_id
                ORDER BY g.student_id
            """).fetchall()
            result = []
            for r in rows:
                result.append({
                    "id": r["student_id"],
                    "name": r["name"],
                    "grades": {
                        "Math": r["math"],
                        "English": r["english"],
                        "Science": r["science"],
                        "History": r["history"],
                        "PE": r["pe"],
                    }
                })
            return result

    def update_grade(self, student_id: int, subject: str, score: float) -> bool:
        col = subject.lower()
        allowed = {"math", "english", "science", "history", "pe"}
        if col not in allowed:
            return False
        with self._connect() as conn:
            cur = conn.execute(
                f"UPDATE grades SET {col} = ? WHERE student_id = ?",
                (score, student_id),
            )
            conn.commit()
            return cur.rowcount > 0

    # ---- Attendance ----

    def list_attendance(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT a.student_id, s.name, a.mon, a.tue, a.wed, a.thu, a.fri
                FROM attendance a
                JOIN students s ON s.id = a.student_id
                ORDER BY a.student_id
            """).fetchall()
            result = []
            for r in rows:
                result.append({
                    "id": r["student_id"],
                    "name": r["name"],
                    "records": [r["mon"], r["tue"], r["wed"], r["thu"], r["fri"]],
                })
            return result

    def toggle_attendance(self, student_id: int, day_index: int) -> bool:
        cols = ["mon", "tue", "wed", "thu", "fri"]
        if day_index < 0 or day_index > 4:
            return False
        col = cols[day_index]
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT {col} FROM attendance WHERE student_id = ?", (student_id,)
            ).fetchone()
            if row is None:
                return False
            new_val = "Absent" if row[col] == "Present" else "Present"
            conn.execute(
                f"UPDATE attendance SET {col} = ? WHERE student_id = ?",
                (new_val, student_id),
            )
            conn.commit()
            return True

    # ---- Announcements ----

    def list_announcements(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, title, body, author, date FROM announcements ORDER BY id"
            ).fetchall()
            return [dict(r) for r in rows]

    def add_announcement(self, data: dict) -> dict:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO announcements (title, body, author, date) VALUES (?, ?, ?, ?)",
                (data["title"], data["body"], data.get("author", "Admin User"), data.get("date", "")),
            )
            conn.commit()
            new_id = cur.lastrowid
            return {"id": new_id, **data}
