"""
Rich seed data script for Student Management System.
Clears all existing data and populates MongoDB with realistic demo data.

Usage:
    source venv/bin/activate && python seed_rich_data.py
"""

import random
import sys
from datetime import date, timedelta

from pymongo import MongoClient
from werkzeug.security import generate_password_hash

MONGO_URI = "mongodb://localhost:27017/student-management-record"
random.seed(42)


def main():
    client = MongoClient(MONGO_URI)
    db = client.get_default_database()

    print("Clearing existing data...")
    for coll in db.list_collection_names():
        db[coll].drop()
    print("Done.\n")

    sid = _Sequencer()

    # ── Departments ──────────────────────────────────────────────────
    departments = [
        ("College of Computer Studies", "CCS"),
        ("College of Engineering", "COE"),
        ("College of Business and Management", "CBM"),
        ("College of Education", "CED"),
        ("College of Arts and Sciences", "CAS"),
    ]
    dept_docs = []
    for name, code in departments:
        did = sid.next("departments")
        db.departments.insert_one({"_id": did, "name": name, "code": code})
        dept_docs.append({"id": did, "name": name, "code": code})
    print(f"  Departments: {len(dept_docs)}")

    # ── Courses ──────────────────────────────────────────────────────
    courses_data = [
        ("BS Information Technology", "BSIT", "CCS"),
        ("BS Computer Science", "BSCS", "CCS"),
        ("BS Civil Engineering", "BSCE", "COE"),
        ("BS Business Administration", "BSBA", "CBM"),
        ("BS Secondary Education", "BSEd", "CED"),
        ("BS Psychology", "BSP", "CAS"),
    ]
    course_docs = []
    for name, code, dept_code in courses_data:
        dept = next(d for d in dept_docs if d["code"] == dept_code)
        cid = sid.next("courses")
        db.courses.insert_one({
            "_id": cid, "name": name, "code": code, "department_id": dept["id"]
        })
        course_docs.append({"id": cid, "name": name, "code": code, "department_id": dept["id"]})
    print(f"  Courses: {len(course_docs)}")

    # ── Subjects ─────────────────────────────────────────────────────
    subjects_data = [
        ("Programming 1", "PROG1", "BSIT", 3),
        ("Database Management", "DBMS", "BSIT", 3),
        ("Networking Fundamentals", "NETW", "BSIT", 3),
        ("Web Development", "WEBDEV", "BSIT", 3),
        ("Software Engineering", "SWE", "BSCS", 3),
        ("Data Structures", "DSTRUC", "BSCS", 3),
        ("Calculus 1", "CALC1", "BSCE", 4),
        ("Business Ethics", "BETH", "BSBA", 3),
    ]
    subject_docs = []
    for name, code, course_code, units in subjects_data:
        course = next(c for c in course_docs if c["code"] == course_code)
        subj_id = sid.next("subjects")
        db.subjects.insert_one({
            "_id": subj_id, "name": name, "code": code,
            "course_id": course["id"], "units": units
        })
        subject_docs.append({
            "id": subj_id, "name": name, "code": code,
            "course_id": course["id"], "course_code": course_code
        })
    print(f"  Subjects: {len(subject_docs)}")

    # ── Admin User ───────────────────────────────────────────────────
    db.users.insert_one({
        "_id": "admin", "name": "Admin User", "email": "admin@school.edu",
        "password": generate_password_hash("admin123"), "bio": "System administrator.",
        "role": "Administrator", "join_date": str(date.today())
    })

    # ── Faculty ──────────────────────────────────────────────────────
    faculty_data = [
        ("jcruz", "Prof. John Cruz", "jcruz@school.edu", "CCS"),
        ("msantos", "Prof. Maria Santos", "msantos@school.edu", "CCS"),
        ("areyes", "Prof. Alex Reyes", "areyes@school.edu", "COE"),
        ("ltan", "Prof. Lisa Tan", "ltan@school.edu", "CBM"),
        ("cmendoza", "Prof. Carlos Mendoza", "cmendoza@school.edu", "CED"),
    ]
    faculty_docs = []
    for uname, name, email, dept_code in faculty_data:
        dept = next(d for d in dept_docs if d["code"] == dept_code)
        db.users.insert_one({
            "_id": uname, "name": name, "email": email,
            "password": generate_password_hash("faculty123"), "bio": "", "role": "Faculty",
            "join_date": str(date.today())
        })
        fid = sid.next("faculties")
        db.faculties.insert_one({
            "_id": fid, "username": uname, "name": name,
            "email": email, "department_id": dept["id"]
        })
        faculty_docs.append({
            "id": fid, "username": uname, "name": name,
            "department_id": dept["id"]
        })
    print(f"  Faculty: {len(faculty_docs)}")

    # ── Students ─────────────────────────────────────────────────────
    student_data = [
        # (student_number, name, email, course_code, year)
        ("2026-0001", "Juan Dela Cruz", "juan@email.com", "BSIT", 1),
        ("2026-0002", "Maria Lopez", "maria@email.com", "BSIT", 1),
        ("2026-0003", "Peter Reyes", "peter@email.com", "BSIT", 1),
        ("2026-0004", "Ana Gonzales", "ana@email.com", "BSCS", 1),
        ("2026-0005", "Ben Torres", "ben@email.com", "BSCE", 1),
        ("2025-0001", "Carla Fernandez", "carla@email.com", "BSBA", 2),
        ("2025-0002", "David Villanueva", "david@email.com", "BSCS", 2),
        ("2025-0003", "Elena Martinez", "elena@email.com", "BSEd", 2),
        ("2025-0004", "Francis Ramos", "francis@email.com", "BSIT", 2),
        ("2024-0001", "Gina Navarro", "gina@email.com", "BSP", 3),
        ("2024-0002", "Henry Lim", "henry@email.com", "BSCE", 3),
        ("2024-0003", "Isabel Cruz", "isabel@email.com", "BSBA", 3),
        ("2023-0001", "Jose Garcia", "jose@email.com", "BSEd", 4),
        ("2023-0002", "Katrina Bautista", "katrina@email.com", "BSIT", 4),
        ("2022-0001", "Leo Santiago", "leo@email.com", "BSCS", 5),
    ]
    student_docs = []
    for sn, name, email, course_code, yr in student_data:
        course = next(c for c in course_docs if c["code"] == course_code)
        uname = sn
        db.users.insert_one({
            "_id": uname, "name": name, "email": email,
            "password": generate_password_hash("student123"), "bio": "", "role": "Student",
            "join_date": str(date.today())
        })
        stid = sid.next("students")
        db.students.insert_one({
            "_id": stid, "student_number": sn, "name": name,
            "email": email, "course_id": course["id"],
            "year": yr, "username": uname
        })
        student_docs.append({
            "id": stid, "name": name, "course_id": course["id"],
            "course_code": course_code, "sn": sn
        })
    print(f"  Students: {len(student_docs)}")

    # ── Class Offerings ──────────────────────────────────────────────
    offerings_data = [
        (1, "BSIT-1A", "Mon-Wed 8:00 AM - 10:00 AM", "jcruz", "1st Sem", "2025-2026"),
        (2, "BSIT-1A", "Tue-Thu 10:00 AM - 12:00 PM", "msantos", "1st Sem", "2025-2026"),
        (3, "BSIT-1A", "Mon-Wed 1:00 PM - 3:00 PM", "jcruz", "1st Sem", "2025-2026"),
        (4, "BSIT-1A", "Fri 8:00 AM - 12:00 PM", "msantos", "1st Sem", "2025-2026"),
        (5, "BSCS-1A", "Tue-Thu 1:00 PM - 3:00 PM", "msantos", "1st Sem", "2025-2026"),
        (6, "BSCS-1A", "Mon-Wed 10:00 AM - 12:00 PM", "jcruz", "1st Sem", "2025-2026"),
        (7, "BSCE-1A", "Tue-Thu 8:00 AM - 10:00 AM", "areyes", "1st Sem", "2025-2026"),
        (8, "BSBA-1A", "Mon-Wed 3:00 PM - 5:00 PM", "ltan", "1st Sem", "2025-2026"),
    ]
    offering_docs = []
    for subj_code, section, sched, fac_uname, sem, sy in offerings_data:
        subj = next(s for s in subject_docs if s["id"] == subj_code)
        fac = next(f for f in faculty_docs if f["username"] == fac_uname)
        oid = sid.next("class_offerings")
        db.class_offerings.insert_one({
            "_id": oid, "subject_id": subj["id"], "section": section,
            "schedule": sched, "faculty_id": fac["id"],
            "semester": sem, "school_year": sy
        })
        offering_docs.append({
            "id": oid, "subject_id": subj["id"],
            "subject_name": subj["name"], "subject_code": subj["code"],
            "course_code": subj["course_code"]
        })
    print(f"  Offerings: {len(offering_docs)}")

    # ── Enrollments ──────────────────────────────────────────────────
    # Map each student to offering IDs based on their course
    course_offering_map = {
        "BSIT": [o["id"] for o in offering_docs if o["course_code"] == "BSIT"],
        "BSCS": [o["id"] for o in offering_docs if o["course_code"] == "BSCS"],
        "BSCE": [o["id"] for o in offering_docs if o["course_code"] == "BSCE"],
        "BSBA": [o["id"] for o in offering_docs if o["course_code"] == "BSBA"],
        "BSEd": [],
        "BSP": [],
    }
    # BSEd and BSP students get no offerings for now (no subjects defined)
    # Give them at least enrollment records without items for realistic empty state

    enrollment_data = []
    for st in student_docs:
        offering_ids = course_offering_map.get(st["course_code"], [])
        # 80% approved, 10% pending, 10% rejected
        roll = random.random()
        if roll < 0.8:
            status = "Approved"
        elif roll < 0.9:
            status = "Pending"
        else:
            status = "Rejected"

        # Some students have no course offerings available
        items = []
        for oid in offering_ids:
            offering = next(o for o in offering_docs if o["id"] == oid)
            items.append({
                "offering_id": oid,
                "subject_name": offering["subject_name"],
                "subject_code": offering["subject_code"],
            })

        enr_date = f"2025-06-{random.randint(1, 15):02d}"
        eid = sid.next("enrollments")
        db.enrollments.insert_one({
            "_id": eid, "student_id": st["id"],
            "status": status, "date": enr_date, "items": items
        })
        enrollment_data.append({
            "id": eid, "student_id": st["id"],
            "offering_ids": offering_ids, "status": status
        })
    print(f"  Enrollments: {len(enrollment_data)}")

    # ── Grades ───────────────────────────────────────────────────────
    approved_enrollments = [e for e in enrollment_data if e["status"] == "Approved"]

    # Grade distribution function for realism
    def random_grade():
        r = random.random()
        if r < 0.15:       # top performers
            return random.randint(90, 98)
        elif r < 0.55:     # average
            return random.randint(80, 89)
        elif r < 0.85:     # below average but passing
            return random.randint(75, 79)
        elif r < 0.95:     # borderline
            return random.randint(70, 74)
        else:              # failing
            return random.randint(50, 69)

    grade_count = 0
    for enr in approved_enrollments:
        for oid in enr["offering_ids"]:
            prelim = random_grade()
            midterm = random_grade()
            final = random_grade()
            fg = round((prelim + midterm + final) / 3, 2)
            gs = "Passed" if fg >= 75 else "Failed"
            gid = sid.next("grades")
            db.grades.insert_one({
                "_id": gid, "offering_id": oid,
                "student_id": enr["student_id"],
                "prelim": prelim, "midterm": midterm, "final": final,
                "final_grade": fg, "grade_status": gs
            })
            grade_count += 1
    print(f"  Grades: {grade_count}")

    # ── Attendance ───────────────────────────────────────────────────
    session_dates = []
    start = date(2025, 6, 2)
    for i in range(12):
        session_dates.append(str(start + timedelta(weeks=i // 2, days=(i % 2) * 2)))

    att_count = 0
    for enr in approved_enrollments:
        for oid in enr["offering_ids"]:
            for d in session_dates:
                r = random.random()
                status = "Present" if r > 0.15 else "Absent"
                aid = sid.next("attendance_records")
                db.attendance_records.insert_one({
                    "_id": aid, "offering_id": oid,
                    "student_id": enr["student_id"],
                    "date": d, "status": status
                })
                att_count += 1
    print(f"  Attendance: {att_count}")

    # ── Announcements ────────────────────────────────────────────────
    announcements = [
        ("Welcome to AY 2025-2026",
         "We are excited to welcome all students and faculty to the new academic year! "
         "Please check your schedules and enrollment status through the portal.",
         "Admin User", "2025-05-20 09:00"),
        ("Enrollment Period Now Open",
         "Enrollment for the 1st Semester is now open. All students must complete "
         "enrollment via the online portal before the deadline on June 30.",
         "Admin User", "2025-05-25 14:30"),
        ("Midterm Exam Schedule Released",
         "Midterm examinations will run from July 10 to July 20. "
         "Please coordinate with your instructors for specific schedules.",
         "Admin User", "2025-06-01 10:15"),
        ("Final Exam Guidelines",
         "Final examinations will begin on September 5. "
         "Students are reminded to settle all requirements before exam week.",
         "Admin User", "2025-08-01 09:00"),
        ("Scholarship Applications",
         "Applications for academic scholarships are now being accepted. "
         "Deadline for submission is August 30. See the registrar for details.",
         "Admin User", "2025-07-15 11:00"),
        ("System Maintenance",
         "The student portal will be down for scheduled maintenance on "
         "August 20 from 2:00 AM to 6:00 AM. We apologize for the inconvenience.",
         "Admin User", "2025-08-10 08:30"),
    ]
    for title, body, author, dt in announcements:
        aid = sid.next("announcements")
        db.announcements.insert_one({
            "_id": aid, "title": title, "body": body,
            "author": author, "date": dt
        })
    print(f"  Announcements: {len(announcements)}")

    # ── Audit Log ────────────────────────────────────────────────────
    lid = sid.next("audit_logs")
    db.audit_logs.insert_one({
        "_id": lid, "user": "system",
        "action": "Database initialized with rich seed data",
        "timestamp": str(date.today())
    })
    print(f"  Audit logs: 1")

    # ── Sync MongoDB counters ─────────────────────────────────────────
    for coll_name in ['departments', 'courses', 'subjects', 'faculties',
                      'students', 'class_offerings', 'enrollments',
                      'grades', 'attendance_records', 'announcements', 'audit_logs']:
        last = db[coll_name].find_one(sort=[("_id", -1)])
        if last:
            db.counters.update_one(
                {"_id": coll_name},
                {"$set": {"seq": last["_id"]}},
                upsert=True
            )

    # ── Summary ──────────────────────────────────────────────────────
    print()
    print("=" * 55)
    print("  Rich seed data loaded successfully!")
    print("=" * 55)
    print(f"  {'Departments':20} {len(departments):>3}")
    print(f"  {'Courses':20} {len(course_docs):>3}")
    print(f"  {'Subjects':20} {len(subject_docs):>3}")
    print(f"  {'Faculty':20} {len(faculty_docs):>3}")
    print(f"  {'Students':20} {len(student_docs):>3}")
    print(f"  {'Class Offerings':20} {len(offering_docs):>3}")
    print(f"  {'Enrollments':20} {len(enrollment_data):>3}")
    print(f"  {'Grades':20} {grade_count:>3}")
    print(f"  {'Attendance Records':20} {att_count:>4}")
    print(f"  {'Announcements':20} {len(announcements):>3}")
    print(f"  {'Audit Logs':20} {'1':>3}")
    print("=" * 55)
    print("  Login credentials:")
    print("  Admin:   admin / admin123")
    print("  Faculty: jcruz / faculty123")
    print("  Student: 2026-0001 / student123")
    print("=" * 55)


class _Sequencer:
    def __init__(self):
        self._counters = {}

    def next(self, name):
        self._counters[name] = self._counters.get(name, 0) + 1
        return self._counters[name]


if __name__ == "__main__":
    main()
