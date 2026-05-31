import sqlite3
import os
import random
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
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    code TEXT NOT NULL UNIQUE
                );
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL,
                    department_id INTEGER NOT NULL,
                    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL,
                    course_id INTEGER NOT NULL,
                    units INTEGER DEFAULT 3,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS faculties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    department_id INTEGER NOT NULL,
                    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_number TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    course_id INTEGER NOT NULL,
                    year INTEGER NOT NULL CHECK(year >= 1 AND year <= 5),
                    username TEXT NOT NULL UNIQUE,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS class_offerings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER NOT NULL,
                    section TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    faculty_id INTEGER NOT NULL,
                    semester TEXT NOT NULL,
                    school_year TEXT NOT NULL,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
                    FOREIGN KEY (faculty_id) REFERENCES faculties(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS enrollments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'Pending',
                    date TEXT DEFAULT (date('now')),
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS enrollment_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    enrollment_id INTEGER NOT NULL,
                    offering_id INTEGER NOT NULL,
                    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
                    FOREIGN KEY (offering_id) REFERENCES class_offerings(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS attendance_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    offering_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT DEFAULT 'Present',
                    FOREIGN KEY (offering_id) REFERENCES class_offerings(id) ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    UNIQUE(offering_id, student_id, date)
                );
                CREATE TABLE IF NOT EXISTS grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    offering_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    prelim REAL DEFAULT 0,
                    midterm REAL DEFAULT 0,
                    final REAL DEFAULT 0,
                    final_grade REAL DEFAULT 0,
                    grade_status TEXT DEFAULT '',
                    FOREIGN KEY (offering_id) REFERENCES class_offerings(id) ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    UNIQUE(offering_id, student_id)
                );
                CREATE TABLE IF NOT EXISTS announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    author TEXT NOT NULL,
                    date TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TEXT DEFAULT (datetime('now'))
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

        conn.execute("INSERT INTO departments (name, code) VALUES (?, ?)",
                     ("College of Computer Studies", "CCS"))

        conn.execute("INSERT INTO courses (name, code, department_id) VALUES (?, ?, ?)",
                     ("BS Information Technology", "BSIT", 1))
        conn.execute("INSERT INTO courses (name, code, department_id) VALUES (?, ?, ?)",
                     ("BS Computer Science", "BSCS", 1))

        conn.execute("INSERT INTO subjects (name, code, course_id, units) VALUES (?, ?, ?, ?)",
                     ("Programming 1", "PROG1", 1, 3))
        conn.execute("INSERT INTO subjects (name, code, course_id, units) VALUES (?, ?, ?, ?)",
                     ("Database Management", "DBMS", 1, 3))
        conn.execute("INSERT INTO subjects (name, code, course_id, units) VALUES (?, ?, ?, ?)",
                     ("Networking Fundamentals", "NETW", 1, 3))

        conn.execute(
            "INSERT INTO users (username, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
            ("jcruz", "Prof. John Cruz", "jcruz@school.edu", "faculty123", "Faculty"))
        conn.execute(
            "INSERT INTO faculties (username, name, email, department_id) VALUES (?, ?, ?, ?)",
            ("jcruz", "Prof. John Cruz", "jcruz@school.edu", 1))

        conn.execute(
            "INSERT INTO users (username, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
            ("msantos", "Prof. Maria Santos", "msantos@school.edu", "faculty123", "Faculty"))
        conn.execute(
            "INSERT INTO faculties (username, name, email, department_id) VALUES (?, ?, ?, ?)",
            ("msantos", "Prof. Maria Santos", "msantos@school.edu", 1))

        conn.execute(
            "INSERT INTO users (username, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
            ("2026-0001", "Juan Dela Cruz", "juan@email.com", "student123", "Student"))
        conn.execute(
            "INSERT INTO students (student_number, name, email, course_id, year, username) VALUES (?, ?, ?, ?, ?, ?)",
            ("2026-0001", "Juan Dela Cruz", "juan@email.com", 1, 1, "2026-0001"))

        for sn, name, email in [
            ("2026-0002", "Maria Lopez", "maria@email.com"),
            ("2026-0003", "Peter Reyes", "peter@email.com"),
        ]:
            uname = sn
            conn.execute(
                "INSERT INTO users (username, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
                (uname, name, email, "student123", "Student"))
            conn.execute(
                "INSERT INTO students (student_number, name, email, course_id, year, username) VALUES (?, ?, ?, ?, ?, ?)",
                (sn, name, email, 1, 1, uname))

        conn.execute(
            "INSERT INTO class_offerings (subject_id, section, schedule, faculty_id, semester, school_year) VALUES (?, ?, ?, ?, ?, ?)",
            (1, "BSIT-1A", "Mon-Wed 8:00 AM - 10:00 AM", 1, "1st Semester", "2025-2026"))
        conn.execute(
            "INSERT INTO class_offerings (subject_id, section, schedule, faculty_id, semester, school_year) VALUES (?, ?, ?, ?, ?, ?)",
            (2, "BSIT-1A", "Tue-Thu 10:00 AM - 12:00 PM", 2, "1st Semester", "2025-2026"))
        conn.execute(
            "INSERT INTO class_offerings (subject_id, section, schedule, faculty_id, semester, school_year) VALUES (?, ?, ?, ?, ?, ?)",
            (3, "BSIT-1A", "Mon-Wed 1:00 PM - 3:00 PM", 1, "1st Semester", "2025-2026"))

        # Enroll Juan in all 3 offerings
        conn.execute(
            "INSERT INTO enrollments (student_id, status, date) VALUES (?, ?, ?)",
            (1, "Approved", "2025-06-01"))
        eid = 1
        for oid in [1, 2, 3]:
            conn.execute(
                "INSERT INTO enrollment_items (enrollment_id, offering_id) VALUES (?, ?)",
                (eid, oid))

        # Enroll Maria & Peter in Programming 1
        for sid in [2, 3]:
            conn.execute(
                "INSERT INTO enrollments (student_id, status, date) VALUES (?, ?, ?)",
                (sid, "Approved", "2025-06-01"))
            eid = sid
            conn.execute(
                "INSERT INTO enrollment_items (enrollment_id, offering_id) VALUES (?, ?)",
                (eid, 1))

        # Attendance records
        dates = ["2025-06-02", "2025-06-04", "2025-06-09", "2025-06-11", "2025-06-16"]
        for sid in [1, 2, 3]:
            for d in dates:
                status = "Present" if random.random() > 0.2 else "Absent"
                conn.execute(
                    "INSERT OR IGNORE INTO attendance_records (offering_id, student_id, date, status) VALUES (?, ?, ?, ?)",
                    (1, sid, d, status))

        # Grade records
        for sid, prelim, midterm, final in [
            (1, 90, 92, 95),
            (2, 85, 88, 90),
            (3, 78, 80, 82),
        ]:
            fg = round((prelim + midterm + final) / 3, 2)
            gs = "Passed" if fg >= 75 else "Failed"
            conn.execute(
                "INSERT OR IGNORE INTO grades (offering_id, student_id, prelim, midterm, final, final_grade, grade_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (1, sid, prelim, midterm, final, fg, gs))

        announcements_data = [
            ("Welcome to the New Academic Year",
             "We are excited to welcome all students and faculty to the new academic year at the College of Computer Studies.",
             "Admin User", "2025-05-20 09:00"),
            ("Enrollment Period is Now Open",
             "Enrollment for the 1st Semester of AY 2025-2026 is now open. Please proceed to the enrollment module.",
             "Admin User", "2025-05-25 14:30"),
            ("Midterm Exam Schedule",
             "Midterm examinations will begin on July 10. Please check your class schedules for specific dates.",
             "Admin User", "2025-06-01 10:15"),
        ]
        conn.executemany(
            "INSERT INTO announcements (title, body, author, date) VALUES (?, ?, ?, ?)",
            announcements_data,
        )

        conn.execute(
            "INSERT INTO audit_logs (user, action) VALUES (?, ?)",
            ("system", "Database initialized and seeded")
        )
        conn.commit()

    def _log(self, user: str, action: str):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO audit_logs (user, action) VALUES (?, ?)", (user, action))
            conn.commit()

    # ======================== USERS ========================

    def get_user(self, username: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT username, name, email, bio, role, join_date, password FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            return dict(row) if row else None

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

    def create_user(self, username: str, name: str, email: str, password: str, role: str) -> dict:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO users (username, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
                (username, name, email, password, role),
            )
            conn.commit()
            return {"username": username, "name": name, "email": email, "role": role}

    # ======================== DEPARTMENTS ========================

    def list_departments(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, code FROM departments ORDER BY id"
            ).fetchall()
            return [dict(r) for r in rows]

    def get_department(self, dept_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, name, code FROM departments WHERE id = ?", (dept_id,)
            ).fetchone()
            return dict(row) if row else None

    def add_department(self, data: dict) -> dict:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO departments (name, code) VALUES (?, ?)",
                (data["name"], data["code"]),
            )
            conn.commit()
            return {"id": cur.lastrowid, "name": data["name"], "code": data["code"]}

    def update_department(self, dept_id: int, data: dict) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE departments SET name = ?, code = ? WHERE id = ?",
                (data["name"], data["code"], dept_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def delete_department(self, dept_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM departments WHERE id = ?", (dept_id,))
            conn.commit()
            return cur.rowcount > 0

    # ======================== COURSES ========================

    def list_courses(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT c.id, c.name, c.code, c.department_id, d.name AS department_name
                FROM courses c
                JOIN departments d ON d.id = c.department_id
                ORDER BY c.id
            """).fetchall()
            return [dict(r) for r in rows]

    def get_course(self, course_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("""
                SELECT c.id, c.name, c.code, c.department_id, d.name AS department_name
                FROM courses c
                JOIN departments d ON d.id = c.department_id
                WHERE c.id = ?
            """, (course_id,)).fetchone()
            return dict(row) if row else None

    def add_course(self, data: dict) -> dict:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO courses (name, code, department_id) VALUES (?, ?, ?)",
                (data["name"], data["code"], data["department_id"]),
            )
            conn.commit()
            return {"id": cur.lastrowid, **data}

    def update_course(self, course_id: int, data: dict) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE courses SET name = ?, code = ?, department_id = ? WHERE id = ?",
                (data["name"], data["code"], data["department_id"], course_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def delete_course(self, course_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))
            conn.commit()
            return cur.rowcount > 0

    # ======================== SUBJECTS ========================

    def list_subjects(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT s.id, s.name, s.code, s.course_id, s.units, c.name AS course_name
                FROM subjects s
                JOIN courses c ON c.id = s.course_id
                ORDER BY s.id
            """).fetchall()
            return [dict(r) for r in rows]

    def get_subject(self, subject_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("""
                SELECT s.id, s.name, s.code, s.course_id, s.units, c.name AS course_name
                FROM subjects s
                JOIN courses c ON c.id = s.course_id
                WHERE s.id = ?
            """, (subject_id,)).fetchone()
            return dict(row) if row else None

    def add_subject(self, data: dict) -> dict:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO subjects (name, code, course_id, units) VALUES (?, ?, ?, ?)",
                (data["name"], data["code"], data["course_id"], data.get("units", 3)),
            )
            conn.commit()
            return {"id": cur.lastrowid, **data}

    def update_subject(self, subject_id: int, data: dict) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE subjects SET name = ?, code = ?, course_id = ?, units = ? WHERE id = ?",
                (data["name"], data["code"], data["course_id"], data.get("units", 3), subject_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def delete_subject(self, subject_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
            conn.commit()
            return cur.rowcount > 0

    # ======================== FACULTY ========================

    def list_faculties(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT f.id, f.username, f.name, f.email, f.department_id, d.name AS department_name
                FROM faculties f
                JOIN departments d ON d.id = f.department_id
                ORDER BY f.id
            """).fetchall()
            return [dict(r) for r in rows]

    def get_faculty(self, faculty_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("""
                SELECT f.id, f.username, f.name, f.email, f.department_id, d.name AS department_name
                FROM faculties f
                JOIN departments d ON d.id = f.department_id
                WHERE f.id = ?
            """, (faculty_id,)).fetchone()
            return dict(row) if row else None

    def add_faculty(self, data: dict) -> dict:
        with self._connect() as conn:
            import random
            pw = "faculty123"
            self.create_user(data["username"], data["name"], data["email"], pw, "Faculty")
            cur = conn.execute(
                "INSERT INTO faculties (username, name, email, department_id) VALUES (?, ?, ?, ?)",
                (data["username"], data["name"], data["email"], data["department_id"]),
            )
            conn.commit()
            self._log("admin", f"Created faculty {data['username']}")
            return {"id": cur.lastrowid, **data, "password": pw}

    def update_faculty(self, faculty_id: int, data: dict) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE faculties SET name = ?, email = ?, department_id = ? WHERE id = ?",
                (data["name"], data["email"], data["department_id"], faculty_id),
            )
            if cur.rowcount > 0:
                faculty = conn.execute(
                    "SELECT username FROM faculties WHERE id = ?", (faculty_id,)
                ).fetchone()
                if faculty:
                    conn.execute(
                        "UPDATE users SET name = ?, email = ? WHERE username = ?",
                        (data["name"], data["email"], faculty["username"]),
                    )
            conn.commit()
            return cur.rowcount > 0

    def delete_faculty(self, faculty_id: int) -> bool:
        with self._connect() as conn:
            faculty = conn.execute(
                "SELECT username FROM faculties WHERE id = ?", (faculty_id,)
            ).fetchone()
            cur = conn.execute("DELETE FROM faculties WHERE id = ?", (faculty_id,))
            if cur.rowcount > 0 and faculty:
                conn.execute(
                    "DELETE FROM users WHERE username = ?", (faculty["username"],))
            conn.commit()
            return cur.rowcount > 0

    # ======================== CLASS OFFERINGS ========================

    def list_offerings(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT o.id, o.subject_id, s.name AS subject_name, s.code AS subject_code,
                       o.section, o.schedule, o.faculty_id,
                       f.name AS faculty_name, o.semester, o.school_year
                FROM class_offerings o
                JOIN subjects s ON s.id = o.subject_id
                JOIN faculties f ON f.id = o.faculty_id
                ORDER BY o.id
            """).fetchall()
            return [dict(r) for r in rows]

    def get_offering(self, offering_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("""
                SELECT o.id, o.subject_id, s.name AS subject_name, s.code AS subject_code,
                       o.section, o.schedule, o.faculty_id,
                       f.name AS faculty_name, o.semester, o.school_year
                FROM class_offerings o
                JOIN subjects s ON s.id = o.subject_id
                JOIN faculties f ON f.id = o.faculty_id
                WHERE o.id = ?
            """, (offering_id,)).fetchone()
            return dict(row) if row else None

    def add_offering(self, data: dict) -> dict:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO class_offerings (subject_id, section, schedule, faculty_id, semester, school_year) VALUES (?, ?, ?, ?, ?, ?)",
                (data["subject_id"], data["section"], data["schedule"],
                 data["faculty_id"], data["semester"], data["school_year"]),
            )
            conn.commit()
            return {"id": cur.lastrowid, **data}

    def update_offering(self, offering_id: int, data: dict) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE class_offerings SET subject_id = ?, section = ?, schedule = ?, faculty_id = ?, semester = ?, school_year = ? WHERE id = ?",
                (data["subject_id"], data["section"], data["schedule"],
                 data["faculty_id"], data["semester"], data["school_year"], offering_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def delete_offering(self, offering_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM class_offerings WHERE id = ?", (offering_id,))
            conn.commit()
            return cur.rowcount > 0

    # ======================== STUDENTS ========================

    def list_students(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT s.id, s.student_number, s.name, s.email, s.course_id,
                       c.name AS course_name, s.year, s.username
                FROM students s
                JOIN courses c ON c.id = s.course_id
                ORDER BY s.id
            """).fetchall()
            return [dict(r) for r in rows]

    def get_student(self, student_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("""
                SELECT s.id, s.student_number, s.name, s.email, s.course_id,
                       c.name AS course_name, s.year, s.username
                FROM students s
                JOIN courses c ON c.id = s.course_id
                WHERE s.id = ?
            """, (student_id,)).fetchone()
            return dict(row) if row else None

    def add_student(self, data: dict) -> dict:
        with self._connect() as conn:
            import random
            sn = data.get("student_number", "")
            username = sn
            pw = "student123"
            self.create_user(username, data["name"], data["email"], pw, "Student")
            cur = conn.execute(
                "INSERT INTO students (student_number, name, email, course_id, year, username) VALUES (?, ?, ?, ?, ?, ?)",
                (sn, data["name"], data["email"], data["course_id"], data["year"], username),
            )
            conn.commit()
            self._log("admin", f"Created student {sn}")
            return {"id": cur.lastrowid, **data, "username": username, "password": pw}

    def update_student(self, student_id: int, data: dict) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE students SET name = ?, email = ?, course_id = ?, year = ? WHERE id = ?",
                (data["name"], data["email"], data["course_id"], data["year"], student_id),
            )
            if cur.rowcount > 0:
                student = conn.execute(
                    "SELECT username FROM students WHERE id = ?", (student_id,)
                ).fetchone()
                if student:
                    conn.execute(
                        "UPDATE users SET name = ?, email = ? WHERE username = ?",
                        (data["name"], data["email"], student["username"]),
                    )
            conn.commit()
            return cur.rowcount > 0

    def delete_student(self, student_id: int) -> bool:
        with self._connect() as conn:
            student = conn.execute(
                "SELECT username FROM students WHERE id = ?", (student_id,)
            ).fetchone()
            cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
            if cur.rowcount > 0 and student:
                conn.execute(
                    "DELETE FROM users WHERE username = ?", (student["username"],))
            conn.commit()
            return cur.rowcount > 0

    # ======================== ENROLLMENTS ========================

    def list_enrollments(self, status: Optional[str] = None) -> list[dict]:
        with self._connect() as conn:
            query = """
                SELECT e.id, e.student_id, s.name AS student_name, s.student_number,
                       e.status, e.date
                FROM enrollments e
                JOIN students s ON s.id = e.student_id
            """
            params = []
            if status:
                query += " WHERE e.status = ?"
                params.append(status)
            query += " ORDER BY e.id DESC"
            rows = conn.execute(query, params).fetchall()
            result = []
            for r in rows:
                enr = dict(r)
                items = conn.execute("""
                    SELECT ei.id, ei.offering_id, sub.name AS subject_name, sub.code AS subject_code
                    FROM enrollment_items ei
                    JOIN class_offerings co ON co.id = ei.offering_id
                    JOIN subjects sub ON sub.id = co.subject_id
                    WHERE ei.enrollment_id = ?
                """, (r["id"],)).fetchall()
                enr["items"] = [dict(it) for it in items]
                result.append(enr)
            return result

    def get_enrollment(self, enrollment_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("""
                SELECT e.id, e.student_id, s.name AS student_name, s.student_number,
                       e.status, e.date
                FROM enrollments e
                JOIN students s ON s.id = e.student_id
                WHERE e.id = ?
            """, (enrollment_id,)).fetchone()
            if row is None:
                return None
            enr = dict(row)
            items = conn.execute("""
                SELECT ei.id, ei.offering_id, sub.name AS subject_name, sub.code AS subject_code
                FROM enrollment_items ei
                JOIN class_offerings co ON co.id = ei.offering_id
                JOIN subjects sub ON sub.id = co.subject_id
                WHERE ei.enrollment_id = ?
            """, (enrollment_id,)).fetchall()
            enr["items"] = [dict(it) for it in items]
            return enr

    def create_enrollment(self, student_id: int, offering_ids: list[int]) -> dict:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO enrollments (student_id, status) VALUES (?, 'Pending')",
                (student_id,),
            )
            eid = cur.lastrowid
            for oid in offering_ids:
                conn.execute(
                    "INSERT INTO enrollment_items (enrollment_id, offering_id) VALUES (?, ?)",
                    (eid, oid),
                )
            conn.commit()
            self._log("system", f"Enrollment {eid} created for student {student_id}")
            return self.get_enrollment(eid)

    def approve_enrollment(self, enrollment_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE enrollments SET status = 'Approved' WHERE id = ? AND status = 'Pending'",
                (enrollment_id,),
            )
            conn.commit()
            if cur.rowcount > 0:
                self._log("admin", f"Approved enrollment {enrollment_id}")
                return True
            return False

    def reject_enrollment(self, enrollment_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE enrollments SET status = 'Rejected' WHERE id = ? AND status = 'Pending'",
                (enrollment_id,),
            )
            conn.commit()
            if cur.rowcount > 0:
                self._log("admin", f"Rejected enrollment {enrollment_id}")
                return True
            return False

    def get_student_enrollments(self, student_id: int) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT e.id, e.student_id, s.name AS student_name, s.student_number,
                       e.status, e.date
                FROM enrollments e
                JOIN students s ON s.id = e.student_id
                WHERE e.student_id = ?
                ORDER BY e.id DESC
            """, (student_id,)).fetchall()
            result = []
            for r in rows:
                enr = dict(r)
                items = conn.execute("""
                    SELECT ei.id, ei.offering_id, sub.name AS subject_name, sub.code AS subject_code
                    FROM enrollment_items ei
                    JOIN class_offerings co ON co.id = ei.offering_id
                    JOIN subjects sub ON sub.id = co.subject_id
                    WHERE ei.enrollment_id = ?
                """, (r["id"],)).fetchall()
                enr["items"] = [dict(it) for it in items]
                result.append(enr)
            return result

    # ======================== ATTENDANCE ========================

    def list_attendance(self, offering_id: int) -> list[dict]:
        with self._connect() as conn:
            enrolled = conn.execute("""
                SELECT DISTINCT e.student_id, s.name AS student_name
                FROM enrollment_items ei
                JOIN enrollments e ON e.id = ei.enrollment_id
                JOIN students s ON s.id = e.student_id
                WHERE ei.offering_id = ? AND e.status = 'Approved'
            """, (offering_id,)).fetchall()
            result = []
            for row in enrolled:
                records = conn.execute("""
                    SELECT id, date, status FROM attendance_records
                    WHERE offering_id = ? AND student_id = ?
                    ORDER BY date
                """, (offering_id, row["student_id"])).fetchall()
                result.append({
                    "student_id": row["student_id"],
                    "student_name": row["student_name"],
                    "records": [dict(r) for r in records],
                })
            return result

    def get_attendance(self, offering_id: int, student_id: int) -> Optional[dict]:
        with self._connect() as conn:
            records = conn.execute("""
                SELECT id, date, status FROM attendance_records
                WHERE offering_id = ? AND student_id = ?
                ORDER BY date
            """, (offering_id, student_id)).fetchall()
            return {"student_id": student_id, "records": [dict(r) for r in records]}

    def mark_attendance(self, offering_id: int, student_id: int, date: str, status: str) -> dict:
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO attendance_records (offering_id, student_id, date, status)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(offering_id, student_id, date) DO UPDATE SET status = ?
            """, (offering_id, student_id, date, status, status))
            conn.commit()
            return {"offering_id": offering_id, "student_id": student_id, "date": date, "status": status}

    def get_student_attendance_summary(self, student_id: int) -> dict:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT ar.status, sub.name AS subject_name
                FROM attendance_records ar
                JOIN class_offerings co ON co.id = ar.offering_id
                JOIN subjects sub ON sub.id = co.subject_id
                WHERE ar.student_id = ?
            """, (student_id,)).fetchall()
            total = len(rows)
            present = sum(1 for r in rows if r["status"] == "Present")
            absent = total - present
            return {
                "total": total,
                "present": present,
                "absent": absent,
                "percentage": round((present / total * 100), 1) if total else 0,
            }

    # ======================== GRADES ========================

    def list_grades(self, offering_id: int) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT DISTINCT ei.offering_id, e.student_id, s.name AS student_name,
                       sub.name AS subject_name,
                       COALESCE(g.prelim, 0) AS prelim,
                       COALESCE(g.midterm, 0) AS midterm,
                       COALESCE(g.final, 0) AS final,
                       COALESCE(g.final_grade, 0) AS final_grade,
                       COALESCE(g.grade_status, '') AS grade_status
                FROM enrollment_items ei
                JOIN enrollments e ON e.id = ei.enrollment_id AND e.status = 'Approved'
                JOIN students s ON s.id = e.student_id
                JOIN class_offerings co ON co.id = ei.offering_id
                JOIN subjects sub ON sub.id = co.subject_id
                LEFT JOIN grades g ON g.offering_id = ei.offering_id AND g.student_id = e.student_id
                WHERE ei.offering_id = ?
                ORDER BY s.name
            """, (offering_id,)).fetchall()
            return [dict(r) for r in rows]

    def get_grade(self, offering_id: int, student_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("""
                SELECT g.id, g.offering_id, g.student_id, s.name AS student_name,
                       sub.name AS subject_name,
                       g.prelim, g.midterm, g.final, g.final_grade, g.grade_status
                FROM grades g
                JOIN students s ON s.id = g.student_id
                JOIN class_offerings co ON co.id = g.offering_id
                JOIN subjects sub ON sub.id = co.subject_id
                WHERE g.offering_id = ? AND g.student_id = ?
            """, (offering_id, student_id)).fetchone()
            return dict(row) if row else None

    def upsert_grade(self, offering_id: int, student_id: int, data: dict) -> dict:
        prelim = float(data.get("prelim", 0))
        midterm = float(data.get("midterm", 0))
        final = float(data.get("final", 0))
        final_grade = round((prelim + midterm + final) / 3, 2)
        grade_status = "Passed" if final_grade >= 75 else "Failed"
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO grades (offering_id, student_id, prelim, midterm, final, final_grade, grade_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(offering_id, student_id) DO UPDATE SET
                    prelim = ?, midterm = ?, final = ?, final_grade = ?, grade_status = ?
            """, (offering_id, student_id, prelim, midterm, final, final_grade, grade_status,
                  prelim, midterm, final, final_grade, grade_status))
            conn.commit()
            return self.get_grade(offering_id, student_id)

    def get_student_grades(self, student_id: int) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT DISTINCT ei.offering_id, e.student_id, s.name AS student_name,
                       sub.name AS subject_name, sub.code AS subject_code,
                       COALESCE(g.prelim, 0) AS prelim,
                       COALESCE(g.midterm, 0) AS midterm,
                       COALESCE(g.final, 0) AS final,
                       COALESCE(g.final_grade, 0) AS final_grade,
                       COALESCE(g.grade_status, '') AS grade_status
                FROM enrollments e
                JOIN enrollment_items ei ON ei.enrollment_id = e.id
                JOIN students s ON s.id = e.student_id
                JOIN class_offerings co ON co.id = ei.offering_id
                JOIN subjects sub ON sub.id = co.subject_id
                LEFT JOIN grades g ON g.offering_id = ei.offering_id AND g.student_id = e.student_id
                WHERE e.student_id = ? AND e.status = 'Approved'
                ORDER BY sub.name
            """, (student_id,)).fetchall()
            return [dict(r) for r in rows]

    # ======================== ANNOUNCEMENTS ========================

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
                (data["title"], data["body"], data.get("author", "Admin"),
                 data.get("date", "")),
            )
            conn.commit()
            return {"id": cur.lastrowid, **data}

    # ======================== PROFILE ========================

    def get_student_by_username(self, username: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("""
                SELECT s.id, s.student_number, s.name, s.email, s.course_id,
                       c.name AS course_name, s.year, s.username
                FROM students s
                JOIN courses c ON c.id = s.course_id
                WHERE s.username = ?
            """, (username,)).fetchone()
            return dict(row) if row else None

    def get_faculty_by_username(self, username: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("""
                SELECT f.id, f.username, f.name, f.email, f.department_id, d.name AS department_name
                FROM faculties f
                JOIN departments d ON d.id = f.department_id
                WHERE f.username = ?
            """, (username,)).fetchone()
            return dict(row) if row else None

    # ======================== DASHBOARD / REPORTS ========================

    def get_dashboard_stats(self) -> dict:
        with self._connect() as conn:
            total_students = conn.execute(
                "SELECT COUNT(*) FROM students").fetchone()[0]
            total_faculties = conn.execute(
                "SELECT COUNT(*) FROM faculties").fetchone()[0]
            total_offerings = conn.execute(
                "SELECT COUNT(*) FROM class_offerings").fetchone()[0]
            pending_enrollments = conn.execute(
                "SELECT COUNT(*) FROM enrollments WHERE status = 'Pending'").fetchone()[0]
            return {
                "total_students": total_students,
                "total_faculties": total_faculties,
                "total_offerings": total_offerings,
                "pending_enrollments": pending_enrollments,
            }

    def get_faculty_offerings(self, faculty_id: int) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT o.id, o.subject_id, s.name AS subject_name, s.code AS subject_code,
                       o.section, o.schedule, o.semester, o.school_year,
                       (SELECT COUNT(*) FROM enrollment_items ei
                        JOIN enrollments e ON e.id = ei.enrollment_id
                        WHERE ei.offering_id = o.id AND e.status = 'Approved') AS enrolled_count
                FROM class_offerings o
                JOIN subjects s ON s.id = o.subject_id
                WHERE o.faculty_id = ?
                ORDER BY o.id
            """, (faculty_id,)).fetchall()
            return [dict(r) for r in rows]

    def get_student_dashboard(self, student_id: int) -> dict:
        enrollments = self.get_student_enrollments(student_id)
        approved_enrs = [e for e in enrollments if e["status"] == "Approved"]
        subjects = []
        for e in approved_enrs:
            for item in e["items"]:
                offering = self.get_offering(item["offering_id"])
                if offering:
                    subjects.append(offering)
        attendance = self.get_student_attendance_summary(student_id)
        grades = self.get_student_grades(student_id)
        return {
            "subjects": subjects,
            "attendance": attendance,
            "grades": grades,
            "enrollments": enrollments,
        }

    def get_enrollment_report(self) -> dict:
        with self._connect() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM enrollments").fetchone()[0]
            approved = conn.execute(
                "SELECT COUNT(*) FROM enrollments WHERE status = 'Approved'").fetchone()[0]
            pending = conn.execute(
                "SELECT COUNT(*) FROM enrollments WHERE status = 'Pending'").fetchone()[0]
            rejected = conn.execute(
                "SELECT COUNT(*) FROM enrollments WHERE status = 'Rejected'").fetchone()[0]
            course_dist = conn.execute("""
                SELECT c.name, COUNT(*) as count
                FROM enrollments e
                JOIN students s ON s.id = e.student_id
                JOIN courses c ON c.id = s.course_id
                WHERE e.status = 'Approved'
                GROUP BY c.name
            """).fetchall()
            return {
                "total": total,
                "approved": approved,
                "pending": pending,
                "rejected": rejected,
                "course_distribution": [dict(r) for r in course_dist],
            }

    def get_attendance_report(self, offering_id: int) -> dict:
        records = self.list_attendance(offering_id)
        total_sessions = set()
        student_stats = []
        for r in records:
            sessions = len(r["records"])
            present = sum(1 for rec in r["records"] if rec["status"] == "Present")
            absent = sessions - present
            for rec in r["records"]:
                total_sessions.add(rec["date"])
            student_stats.append({
                "student_id": r["student_id"],
                "student_name": r["student_name"],
                "total": sessions,
                "present": present,
                "absent": absent,
                "percentage": round((present / sessions * 100), 1) if sessions else 0,
            })
        return {
            "offering_id": offering_id,
            "total_sessions": len(total_sessions),
            "students": student_stats,
        }

    def get_grade_report(self, offering_id: int) -> dict:
        grades = self.list_grades(offering_id)
        if not grades:
            return {"offering_id": offering_id, "students": [], "average": 0, "passing_rate": 0}
        total = len(grades)
        passed = sum(1 for g in grades if g["grade_status"] == "Passed")
        avg = round(sum(g["final_grade"] for g in grades) / total, 2)
        return {
            "offering_id": offering_id,
            "students": grades,
            "average": avg,
            "passing_rate": round((passed / total) * 100, 1),
        }

    # ======================== AUDIT LOG ========================

    def add_audit_log(self, user: str, action: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO audit_logs (user, action) VALUES (?, ?)", (user, action))
            conn.commit()

    def list_audit_logs(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, user, action, timestamp FROM audit_logs ORDER BY id DESC LIMIT 100"
            ).fetchall()
            return [dict(r) for r in rows]
