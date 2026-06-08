import random
from datetime import date
from typing import Optional
from pymongo import MongoClient
from .interface import Repository


class MongoRepository(Repository):
    def __init__(self, uri: str):
        self.client = MongoClient(uri)
        self.db = self.client.get_default_database()
        self._init_collections()
        self._seed_if_empty()

    def _next_id(self, name: str) -> int:
        result = self.db.counters.find_one_and_update(
            {"_id": name},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True,
        )
        return result["seq"]

    def _doc(self, doc):
        if doc is None:
            return None
        doc["id"] = doc.pop("_id")
        return doc

    def _docs(self, docs):
        return [self._doc(d) for d in docs]

    def _init_collections(self):
        pass

    def _seed_if_empty(self):
        if self.db.departments.count_documents({}) > 0:
            return
        self._seed()

    def _seed(self):
        dept_id = self._next_id("departments")
        self.db.departments.insert_one({
            "_id": dept_id, "name": "College of Computer Studies", "code": "CCS"
        })

        course1_id = self._next_id("courses")
        self.db.courses.insert_one({
            "_id": course1_id, "name": "BS Information Technology",
            "code": "BSIT", "department_id": dept_id
        })
        course2_id = self._next_id("courses")
        self.db.courses.insert_one({
            "_id": course2_id, "name": "BS Computer Science",
            "code": "BSCS", "department_id": dept_id
        })

        sub1_id = self._next_id("subjects")
        self.db.subjects.insert_one({
            "_id": sub1_id, "name": "Programming 1", "code": "PROG1",
            "course_id": course1_id, "units": 3
        })
        sub2_id = self._next_id("subjects")
        self.db.subjects.insert_one({
            "_id": sub2_id, "name": "Database Management", "code": "DBMS",
            "course_id": course1_id, "units": 3
        })
        sub3_id = self._next_id("subjects")
        self.db.subjects.insert_one({
            "_id": sub3_id, "name": "Networking Fundamentals", "code": "NETW",
            "course_id": course1_id, "units": 3
        })

        users_data = [
            ("admin", "Admin User", "admin@school.edu", "admin123",
             "System administrator.", "Administrator"),
            ("jcruz", "Prof. John Cruz", "jcruz@school.edu", "faculty123", "", "Faculty"),
            ("msantos", "Prof. Maria Santos", "msantos@school.edu", "faculty123", "", "Faculty"),
            ("2026-0001", "Juan Dela Cruz", "juan@email.com", "student123", "", "Student"),
            ("2026-0002", "Maria Lopez", "maria@email.com", "student123", "", "Student"),
            ("2026-0003", "Peter Reyes", "peter@email.com", "student123", "", "Student"),
        ]
        for uname, name, email, pwd, bio, role in users_data:
            self.db.users.insert_one({
                "_id": uname, "name": name, "email": email,
                "password": pwd, "bio": bio, "role": role,
                "join_date": str(date.today())
            })

        fac1_id = self._next_id("faculties")
        self.db.faculties.insert_one({
            "_id": fac1_id, "username": "jcruz", "name": "Prof. John Cruz",
            "email": "jcruz@school.edu", "department_id": dept_id
        })
        fac2_id = self._next_id("faculties")
        self.db.faculties.insert_one({
            "_id": fac2_id, "username": "msantos", "name": "Prof. Maria Santos",
            "email": "msantos@school.edu", "department_id": dept_id
        })

        stu1_id = self._next_id("students")
        self.db.students.insert_one({
            "_id": stu1_id, "student_number": "2026-0001",
            "name": "Juan Dela Cruz", "email": "juan@email.com",
            "course_id": course1_id, "year": 1, "username": "2026-0001"
        })
        stu2_id = self._next_id("students")
        self.db.students.insert_one({
            "_id": stu2_id, "student_number": "2026-0002",
            "name": "Maria Lopez", "email": "maria@email.com",
            "course_id": course1_id, "year": 1, "username": "2026-0002"
        })
        stu3_id = self._next_id("students")
        self.db.students.insert_one({
            "_id": stu3_id, "student_number": "2026-0003",
            "name": "Peter Reyes", "email": "peter@email.com",
            "course_id": course1_id, "year": 1, "username": "2026-0003"
        })

        off1_id = self._next_id("class_offerings")
        self.db.class_offerings.insert_one({
            "_id": off1_id, "subject_id": sub1_id, "section": "BSIT-1A",
            "schedule": "Mon-Wed 8:00 AM - 10:00 AM", "faculty_id": fac1_id,
            "semester": "1st Semester", "school_year": "2025-2026"
        })
        off2_id = self._next_id("class_offerings")
        self.db.class_offerings.insert_one({
            "_id": off2_id, "subject_id": sub2_id, "section": "BSIT-1A",
            "schedule": "Tue-Thu 10:00 AM - 12:00 PM", "faculty_id": fac2_id,
            "semester": "1st Semester", "school_year": "2025-2026"
        })
        off3_id = self._next_id("class_offerings")
        self.db.class_offerings.insert_one({
            "_id": off3_id, "subject_id": sub3_id, "section": "BSIT-1A",
            "schedule": "Mon-Wed 1:00 PM - 3:00 PM", "faculty_id": fac1_id,
            "semester": "1st Semester", "school_year": "2025-2026"
        })

        for sid, status, dt, oids in [
            (stu1_id, "Approved", "2025-06-01", [off1_id, off2_id, off3_id]),
            (stu2_id, "Approved", "2025-06-01", [off1_id]),
            (stu3_id, "Approved", "2025-06-01", [off1_id]),
        ]:
            eid = self._next_id("enrollments")
            items = []
            for oid in oids:
                offering = self.db.class_offerings.find_one({"_id": oid})
                subject = self.db.subjects.find_one({"_id": offering["subject_id"]})
                items.append({
                    "offering_id": oid,
                    "subject_name": subject["name"],
                    "subject_code": subject["code"],
                })
            self.db.enrollments.insert_one({
                "_id": eid, "student_id": sid, "status": status,
                "date": dt, "items": items
            })

        dates = ["2025-06-02", "2025-06-04", "2025-06-09", "2025-06-11", "2025-06-16"]
        for sid in [stu1_id, stu2_id, stu3_id]:
            for d in dates:
                status = "Present" if random.random() > 0.2 else "Absent"
                rid = self._next_id("attendance_records")
                self.db.attendance_records.insert_one({
                    "_id": rid, "offering_id": off1_id,
                    "student_id": sid, "date": d, "status": status
                })

        grades_data = [
            (stu1_id, 90, 92, 95),
            (stu2_id, 85, 88, 90),
            (stu3_id, 78, 80, 82),
        ]
        for sid, prelim, midterm, final in grades_data:
            fg = round((prelim + midterm + final) / 3, 2)
            gs = "Passed" if fg >= 75 else "Failed"
            gid = self._next_id("grades")
            self.db.grades.insert_one({
                "_id": gid, "offering_id": off1_id, "student_id": sid,
                "prelim": prelim, "midterm": midterm, "final": final,
                "final_grade": fg, "grade_status": gs
            })

        announcements = [
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
        for title, body, author, dt in announcements:
            aid = self._next_id("announcements")
            self.db.announcements.insert_one({
                "_id": aid, "title": title, "body": body,
                "author": author, "date": dt
            })

        log_id = self._next_id("audit_logs")
        self.db.audit_logs.insert_one({
            "_id": log_id, "user": "system",
            "action": "Database initialized and seeded",
            "timestamp": "2025-06-01 00:00:00"
        })

    def _log(self, user: str, action: str):
        lid = self._next_id("audit_logs")
        self.db.audit_logs.insert_one({
            "_id": lid, "user": user, "action": action,
            "timestamp": str(date.today())
        })

    # ======================== USERS ========================

    def get_user(self, username: str) -> Optional[dict]:
        doc = self.db.users.find_one({"_id": username})
        if doc:
            doc["username"] = doc.pop("_id")
            return doc
        return None

    def update_user(self, username: str, data: dict) -> bool:
        result = self.db.users.update_one(
            {"_id": username},
            {"$set": {"name": data["name"], "email": data["email"],
                       "bio": data.get("bio", "")}}
        )
        return result.modified_count > 0

    def change_password(self, username: str, current: str, new: str) -> bool:
        user = self.db.users.find_one({"_id": username})
        if user is None or user.get("password") != current:
            return False
        self.db.users.update_one(
            {"_id": username}, {"$set": {"password": new}}
        )
        return True

    def create_user(self, username: str, name: str, email: str, password: str, role: str) -> dict:
        self.db.users.insert_one({
            "_id": username, "name": name, "email": email,
            "password": password, "role": role, "bio": "",
            "join_date": str(date.today())
        })
        return {"username": username, "name": name, "email": email, "role": role}

    # ======================== DEPARTMENTS ========================

    def list_departments(self) -> list[dict]:
        return self._docs(self.db.departments.find().sort("_id", 1))

    def get_department(self, dept_id: int) -> Optional[dict]:
        return self._doc(self.db.departments.find_one({"_id": dept_id}))

    def add_department(self, data: dict) -> dict:
        did = self._next_id("departments")
        self.db.departments.insert_one({
            "_id": did, "name": data["name"], "code": data["code"]
        })
        return {"id": did, "name": data["name"], "code": data["code"]}

    def update_department(self, dept_id: int, data: dict) -> bool:
        result = self.db.departments.update_one(
            {"_id": dept_id},
            {"$set": {"name": data["name"], "code": data["code"]}}
        )
        return result.modified_count > 0

    def delete_department(self, dept_id: int) -> bool:
        result = self.db.departments.delete_one({"_id": dept_id})
        return result.deleted_count > 0

    # ======================== COURSES ========================

    def list_courses(self) -> list[dict]:
        return self._docs(self.db.courses.aggregate([
            {"$lookup": {"from": "departments", "localField": "department_id",
                          "foreignField": "_id", "as": "dept"}},
            {"$unwind": "$dept"},
            {"$project": {
                "id": "$_id", "name": 1, "code": 1,
                "department_id": 1, "department_name": "$dept.name"
            }},
            {"$sort": {"_id": 1}}
        ]))

    def get_course(self, course_id: int) -> Optional[dict]:
        return self._doc_one(self.db.courses.aggregate([
            {"$match": {"_id": course_id}},
            {"$lookup": {"from": "departments", "localField": "department_id",
                          "foreignField": "_id", "as": "dept"}},
            {"$unwind": "$dept"},
            {"$project": {
                "id": "$_id", "name": 1, "code": 1,
                "department_id": 1, "department_name": "$dept.name"
            }}
        ]))

    def add_course(self, data: dict) -> dict:
        cid = self._next_id("courses")
        self.db.courses.insert_one({
            "_id": cid, "name": data["name"], "code": data["code"],
            "department_id": data["department_id"]
        })
        return {"id": cid, **data}

    def update_course(self, course_id: int, data: dict) -> bool:
        result = self.db.courses.update_one(
            {"_id": course_id},
            {"$set": {
                "name": data["name"], "code": data["code"],
                "department_id": data["department_id"]
            }}
        )
        return result.modified_count > 0

    def delete_course(self, course_id: int) -> bool:
        result = self.db.courses.delete_one({"_id": course_id})
        return result.deleted_count > 0

    # ======================== SUBJECTS ========================

    def list_subjects(self) -> list[dict]:
        return self._docs(self.db.subjects.aggregate([
            {"$lookup": {"from": "courses", "localField": "course_id",
                          "foreignField": "_id", "as": "c"}},
            {"$unwind": "$c"},
            {"$project": {
                "id": "$_id", "name": 1, "code": 1, "course_id": 1,
                "units": 1, "course_name": "$c.name"
            }},
            {"$sort": {"_id": 1}}
        ]))

    def get_subject(self, subject_id: int) -> Optional[dict]:
        return self._doc_one(self.db.subjects.aggregate([
            {"$match": {"_id": subject_id}},
            {"$lookup": {"from": "courses", "localField": "course_id",
                          "foreignField": "_id", "as": "c"}},
            {"$unwind": "$c"},
            {"$project": {
                "id": "$_id", "name": 1, "code": 1, "course_id": 1,
                "units": 1, "course_name": "$c.name"
            }}
        ]))

    def add_subject(self, data: dict) -> dict:
        sid = self._next_id("subjects")
        self.db.subjects.insert_one({
            "_id": sid, "name": data["name"], "code": data["code"],
            "course_id": data["course_id"], "units": data.get("units", 3)
        })
        return {"id": sid, **data}

    def update_subject(self, subject_id: int, data: dict) -> bool:
        result = self.db.subjects.update_one(
            {"_id": subject_id},
            {"$set": {
                "name": data["name"], "code": data["code"],
                "course_id": data["course_id"], "units": data.get("units", 3)
            }}
        )
        return result.modified_count > 0

    def delete_subject(self, subject_id: int) -> bool:
        result = self.db.subjects.delete_one({"_id": subject_id})
        return result.deleted_count > 0

    # ======================== FACULTY ========================

    def list_faculties(self) -> list[dict]:
        return self._docs(self.db.faculties.aggregate([
            {"$lookup": {"from": "departments", "localField": "department_id",
                          "foreignField": "_id", "as": "dept"}},
            {"$unwind": "$dept"},
            {"$project": {
                "id": "$_id", "username": 1, "name": 1, "email": 1,
                "department_id": 1, "department_name": "$dept.name"
            }},
            {"$sort": {"_id": 1}}
        ]))

    def get_faculty(self, faculty_id: int) -> Optional[dict]:
        return self._doc_one(self.db.faculties.aggregate([
            {"$match": {"_id": faculty_id}},
            {"$lookup": {"from": "departments", "localField": "department_id",
                          "foreignField": "_id", "as": "dept"}},
            {"$unwind": "$dept"},
            {"$project": {
                "id": "$_id", "username": 1, "name": 1, "email": 1,
                "department_id": 1, "department_name": "$dept.name"
            }}
        ]))

    def add_faculty(self, data: dict) -> dict:
        pw = "faculty123"
        self.create_user(data["username"], data["name"], data["email"], pw, "Faculty")
        fid = self._next_id("faculties")
        self.db.faculties.insert_one({
            "_id": fid, "username": data["username"], "name": data["name"],
            "email": data["email"], "department_id": data["department_id"]
        })
        self._log("admin", f"Created faculty {data['username']}")
        return {"id": fid, **data, "password": pw}

    def update_faculty(self, faculty_id: int, data: dict) -> bool:
        result = self.db.faculties.update_one(
            {"_id": faculty_id},
            {"$set": {
                "name": data["name"], "email": data["email"],
                "department_id": data["department_id"]
            }}
        )
        if result.modified_count > 0:
            faculty = self.db.faculties.find_one({"_id": faculty_id})
            if faculty:
                self.db.users.update_one(
                    {"_id": faculty["username"]},
                    {"$set": {"name": data["name"], "email": data["email"]}}
                )
        return result.modified_count > 0

    def delete_faculty(self, faculty_id: int) -> bool:
        faculty = self.db.faculties.find_one({"_id": faculty_id})
        result = self.db.faculties.delete_one({"_id": faculty_id})
        if result.deleted_count > 0 and faculty:
            self.db.users.delete_one({"_id": faculty["username"]})
        return result.deleted_count > 0

    # ======================== CLASS OFFERINGS ========================

    def list_offerings(self) -> list[dict]:
        return self._docs(self.db.class_offerings.aggregate([
            {"$lookup": {"from": "subjects", "localField": "subject_id",
                          "foreignField": "_id", "as": "sub"}},
            {"$unwind": "$sub"},
            {"$lookup": {"from": "faculties", "localField": "faculty_id",
                          "foreignField": "_id", "as": "fac"}},
            {"$unwind": "$fac"},
            {"$project": {
                "id": "$_id", "subject_id": 1,
                "subject_name": "$sub.name", "subject_code": "$sub.code",
                "section": 1, "schedule": 1, "faculty_id": 1,
                "faculty_name": "$fac.name", "semester": 1, "school_year": 1
            }},
            {"$sort": {"_id": 1}}
        ]))

    def get_offering(self, offering_id: int) -> Optional[dict]:
        return self._doc_one(self.db.class_offerings.aggregate([
            {"$match": {"_id": offering_id}},
            {"$lookup": {"from": "subjects", "localField": "subject_id",
                          "foreignField": "_id", "as": "sub"}},
            {"$unwind": "$sub"},
            {"$lookup": {"from": "faculties", "localField": "faculty_id",
                          "foreignField": "_id", "as": "fac"}},
            {"$unwind": "$fac"},
            {"$project": {
                "id": "$_id", "subject_id": 1,
                "subject_name": "$sub.name", "subject_code": "$sub.code",
                "section": 1, "schedule": 1, "faculty_id": 1,
                "faculty_name": "$fac.name", "semester": 1, "school_year": 1
            }}
        ]))

    def add_offering(self, data: dict) -> dict:
        oid = self._next_id("class_offerings")
        self.db.class_offerings.insert_one({
            "_id": oid, "subject_id": data["subject_id"],
            "section": data["section"], "schedule": data["schedule"],
            "faculty_id": data["faculty_id"], "semester": data["semester"],
            "school_year": data["school_year"]
        })
        return {"id": oid, **data}

    def update_offering(self, offering_id: int, data: dict) -> bool:
        result = self.db.class_offerings.update_one(
            {"_id": offering_id},
            {"$set": {
                "subject_id": data["subject_id"], "section": data["section"],
                "schedule": data["schedule"], "faculty_id": data["faculty_id"],
                "semester": data["semester"], "school_year": data["school_year"]
            }}
        )
        return result.modified_count > 0

    def delete_offering(self, offering_id: int) -> bool:
        result = self.db.class_offerings.delete_one({"_id": offering_id})
        return result.deleted_count > 0

    # ======================== STUDENTS ========================

    def list_students(self) -> list[dict]:
        return self._docs(self.db.students.aggregate([
            {"$lookup": {"from": "courses", "localField": "course_id",
                          "foreignField": "_id", "as": "c"}},
            {"$unwind": "$c"},
            {"$project": {
                "id": "$_id", "student_number": 1, "name": 1, "email": 1,
                "course_id": 1, "course_name": "$c.name", "year": 1, "username": 1
            }},
            {"$sort": {"_id": 1}}
        ]))

    def get_student(self, student_id: int) -> Optional[dict]:
        return self._doc_one(self.db.students.aggregate([
            {"$match": {"_id": student_id}},
            {"$lookup": {"from": "courses", "localField": "course_id",
                          "foreignField": "_id", "as": "c"}},
            {"$unwind": "$c"},
            {"$project": {
                "id": "$_id", "student_number": 1, "name": 1, "email": 1,
                "course_id": 1, "course_name": "$c.name", "year": 1, "username": 1
            }}
        ]))

    def add_student(self, data: dict) -> dict:
        sn = data.get("student_number", "")
        username = sn
        pw = "student123"
        self.create_user(username, data["name"], data["email"], pw, "Student")
        sid = self._next_id("students")
        self.db.students.insert_one({
            "_id": sid, "student_number": sn, "name": data["name"],
            "email": data["email"], "course_id": data["course_id"],
            "year": data["year"], "username": username
        })
        self._log("admin", f"Created student {sn}")
        return {"id": sid, **data, "username": username, "password": pw}

    def update_student(self, student_id: int, data: dict) -> bool:
        result = self.db.students.update_one(
            {"_id": student_id},
            {"$set": {
                "name": data["name"], "email": data["email"],
                "course_id": data["course_id"], "year": data["year"]
            }}
        )
        if result.modified_count > 0:
            student = self.db.students.find_one({"_id": student_id})
            if student:
                self.db.users.update_one(
                    {"_id": student["username"]},
                    {"$set": {"name": data["name"], "email": data["email"]}}
                )
        return result.modified_count > 0

    def delete_student(self, student_id: int) -> bool:
        student = self.db.students.find_one({"_id": student_id})
        result = self.db.students.delete_one({"_id": student_id})
        if result.deleted_count > 0 and student:
            self.db.users.delete_one({"_id": student["username"]})
        return result.deleted_count > 0

    # ======================== ENROLLMENTS ========================

    def list_enrollments(self, status: Optional[str] = None) -> list[dict]:
        query = {}
        if status:
            query["status"] = status
        enrollments = list(self.db.enrollments.find(query).sort("_id", -1))
        result = []
        for enr in enrollments:
            enr["id"] = enr.pop("_id")
            student = self.db.students.find_one({"_id": enr["student_id"]})
            if student:
                enr["student_name"] = student["name"]
                enr["student_number"] = student["student_number"]
            result.append(enr)
        return result

    def get_enrollment(self, enrollment_id: int) -> Optional[dict]:
        enr = self.db.enrollments.find_one({"_id": enrollment_id})
        if enr is None:
            return None
        enr["id"] = enr.pop("_id")
        student = self.db.students.find_one({"_id": enr["student_id"]})
        if student:
            enr["student_name"] = student["name"]
            enr["student_number"] = student["student_number"]
        return enr

    def create_enrollment(self, student_id: int, offering_ids: list[int]) -> dict:
        eid = self._next_id("enrollments")
        items = []
        for oid in offering_ids:
            offering = self.db.class_offerings.find_one({"_id": oid})
            subject = self.db.subjects.find_one({"_id": offering["subject_id"]})
            items.append({
                "offering_id": oid,
                "subject_name": subject["name"],
                "subject_code": subject["code"],
            })
        self.db.enrollments.insert_one({
            "_id": eid, "student_id": student_id, "status": "Pending",
            "date": str(date.today()), "items": items
        })
        self._log("system", f"Enrollment {eid} created for student {student_id}")
        return self.get_enrollment(eid)

    def approve_enrollment(self, enrollment_id: int) -> bool:
        result = self.db.enrollments.update_one(
            {"_id": enrollment_id, "status": "Pending"},
            {"$set": {"status": "Approved"}}
        )
        if result.modified_count > 0:
            self._log("admin", f"Approved enrollment {enrollment_id}")
            return True
        return False

    def reject_enrollment(self, enrollment_id: int) -> bool:
        result = self.db.enrollments.update_one(
            {"_id": enrollment_id, "status": "Pending"},
            {"$set": {"status": "Rejected"}}
        )
        if result.modified_count > 0:
            self._log("admin", f"Rejected enrollment {enrollment_id}")
            return True
        return False

    def get_student_enrollments(self, student_id: int) -> list[dict]:
        enrollments = list(
            self.db.enrollments.find({"student_id": student_id}).sort("_id", -1)
        )
        result = []
        for enr in enrollments:
            enr["id"] = enr.pop("_id")
            student = self.db.students.find_one({"_id": enr["student_id"]})
            if student:
                enr["student_name"] = student["name"]
                enr["student_number"] = student["student_number"]
            result.append(enr)
        return result

    # ======================== ATTENDANCE ========================

    def list_attendance(self, offering_id: int) -> list[dict]:
        enrolled = list(self.db.enrollments.aggregate([
            {"$match": {"status": "Approved", "items.offering_id": offering_id}},
            {"$unwind": "$items"},
            {"$match": {"items.offering_id": offering_id}},
            {"$group": {"_id": "$student_id"}},
            {"$lookup": {
                "from": "students",
                "localField": "_id",
                "foreignField": "_id",
                "as": "student"
            }},
            {"$unwind": "$student"},
            {"$project": {
                "student_id": "$_id",
                "student_name": "$student.name"
            }}
        ]))
        result = []
        for row in enrolled:
            records = list(self.db.attendance_records.find(
                {"offering_id": offering_id, "student_id": row["student_id"]}
            ).sort("date", 1))
            result.append({
                "student_id": row["student_id"],
                "student_name": row["student_name"],
                "records": [{"id": r["_id"], "date": r["date"], "status": r["status"]}
                           for r in records]
            })
        return result

    def get_attendance(self, offering_id: int, student_id: int) -> Optional[dict]:
        records = list(self.db.attendance_records.find(
            {"offering_id": offering_id, "student_id": student_id}
        ).sort("date", 1))
        return {
            "student_id": student_id,
            "records": [{"id": r["_id"], "date": r["date"], "status": r["status"]}
                       for r in records]
        }

    def mark_attendance(self, offering_id: int, student_id: int, date: str, status: str) -> dict:
        self.db.attendance_records.update_one(
            {"offering_id": offering_id, "student_id": student_id, "date": date},
            {"$set": {"status": status}},
            upsert=True,
        )
        return {"offering_id": offering_id, "student_id": student_id, "date": date, "status": status}

    def get_student_attendance_summary(self, student_id: int) -> dict:
        rows = list(self.db.attendance_records.find({"student_id": student_id}))
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
        return list(self.db.enrollments.aggregate([
            {"$match": {"status": "Approved", "items.offering_id": offering_id}},
            {"$unwind": "$items"},
            {"$match": {"items.offering_id": offering_id}},
            {"$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "_id",
                "as": "student"
            }},
            {"$unwind": "$student"},
            {"$lookup": {
                "from": "grades",
                "let": {"sid": "$student_id", "oid": "$items.offering_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [
                        {"$eq": ["$student_id", "$$sid"]},
                        {"$eq": ["$offering_id", "$$oid"]}
                    ]}}}
                ],
                "as": "grade"
            }},
            {"$addFields": {
                "grade": {"$ifNull": [{"$arrayElemAt": ["$grade", 0]}, {}]}
            }},
            {"$project": {
                "_id": 0,
                "offering_id": "$items.offering_id",
                "student_id": 1,
                "student_name": "$student.name",
                "subject_name": "$items.subject_name",
                "prelim": {"$ifNull": ["$grade.prelim", 0]},
                "midterm": {"$ifNull": ["$grade.midterm", 0]},
                "final": {"$ifNull": ["$grade.final", 0]},
                "final_grade": {"$ifNull": ["$grade.final_grade", 0]},
                "grade_status": {"$ifNull": ["$grade.grade_status", ""]}
            }},
            {"$sort": {"student_name": 1}}
        ]))

    def get_grade(self, offering_id: int, student_id: int) -> Optional[dict]:
        return self._doc_one(self.db.grades.aggregate([
            {"$match": {"offering_id": offering_id, "student_id": student_id}},
            {"$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "_id",
                "as": "student"
            }},
            {"$unwind": "$student"},
            {"$lookup": {
                "from": "class_offerings",
                "localField": "offering_id",
                "foreignField": "_id",
                "as": "offering"
            }},
            {"$unwind": "$offering"},
            {"$lookup": {
                "from": "subjects",
                "localField": "offering.subject_id",
                "foreignField": "_id",
                "as": "sub"
            }},
            {"$unwind": "$sub"},
            {"$project": {
                "id": "$_id", "offering_id": 1, "student_id": 1,
                "student_name": "$student.name",
                "subject_name": "$sub.name",
                "prelim": 1, "midterm": 1, "final": 1,
                "final_grade": 1, "grade_status": 1
            }}
        ]))

    def upsert_grade(self, offering_id: int, student_id: int, data: dict) -> dict:
        prelim = float(data.get("prelim", 0))
        midterm = float(data.get("midterm", 0))
        final = float(data.get("final", 0))
        final_grade = round((prelim + midterm + final) / 3, 2)
        grade_status = "Passed" if final_grade >= 75 else "Failed"
        existing = self.db.grades.find_one(
            {"offering_id": offering_id, "student_id": student_id}
        )
        if existing:
            self.db.grades.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "prelim": prelim, "midterm": midterm, "final": final,
                    "final_grade": final_grade, "grade_status": grade_status
                }}
            )
        else:
            gid = self._next_id("grades")
            self.db.grades.insert_one({
                "_id": gid, "offering_id": offering_id, "student_id": student_id,
                "prelim": prelim, "midterm": midterm, "final": final,
                "final_grade": final_grade, "grade_status": grade_status
            })
        return self.get_grade(offering_id, student_id)

    def get_student_grades(self, student_id: int) -> list[dict]:
        return list(self.db.enrollments.aggregate([
            {"$match": {"student_id": student_id, "status": "Approved"}},
            {"$unwind": "$items"},
            {"$lookup": {
                "from": "grades",
                "let": {"sid": "$student_id", "oid": "$items.offering_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [
                        {"$eq": ["$student_id", "$$sid"]},
                        {"$eq": ["$offering_id", "$$oid"]}
                    ]}}}
                ],
                "as": "grade"
            }},
            {"$addFields": {
                "grade": {"$ifNull": [{"$arrayElemAt": ["$grade", 0]}, {}]}
            }},
            {"$project": {
                "_id": 0,
                "offering_id": "$items.offering_id",
                "student_id": 1,
                "student_name": 1,
                "subject_name": "$items.subject_name",
                "subject_code": "$items.subject_code",
                "prelim": {"$ifNull": ["$grade.prelim", 0]},
                "midterm": {"$ifNull": ["$grade.midterm", 0]},
                "final": {"$ifNull": ["$grade.final", 0]},
                "final_grade": {"$ifNull": ["$grade.final_grade", 0]},
                "grade_status": {"$ifNull": ["$grade.grade_status", ""]}
            }},
            {"$sort": {"subject_name": 1}}
        ]))

    # ======================== ANNOUNCEMENTS ========================

    def list_announcements(self) -> list[dict]:
        return self._docs(
            self.db.announcements.find().sort("_id", 1)
        )

    def add_announcement(self, data: dict) -> dict:
        aid = self._next_id("announcements")
        self.db.announcements.insert_one({
            "_id": aid, "title": data["title"], "body": data["body"],
            "author": data.get("author", "Admin"),
            "date": data.get("date", "")
        })
        return {"id": aid, **data}

    # ======================== PROFILE ========================

    def get_student_by_username(self, username: str) -> Optional[dict]:
        return self._doc_one(self.db.students.aggregate([
            {"$match": {"username": username}},
            {"$lookup": {"from": "courses", "localField": "course_id",
                          "foreignField": "_id", "as": "c"}},
            {"$unwind": "$c"},
            {"$project": {
                "id": "$_id", "student_number": 1, "name": 1, "email": 1,
                "course_id": 1, "course_name": "$c.name", "year": 1, "username": 1
            }}
        ]))

    def get_faculty_by_username(self, username: str) -> Optional[dict]:
        return self._doc_one(self.db.faculties.aggregate([
            {"$match": {"username": username}},
            {"$lookup": {"from": "departments", "localField": "department_id",
                          "foreignField": "_id", "as": "dept"}},
            {"$unwind": "$dept"},
            {"$project": {
                "id": "$_id", "username": 1, "name": 1, "email": 1,
                "department_id": 1, "department_name": "$dept.name"
            }}
        ]))

    # ======================== DASHBOARD / REPORTS ========================

    def get_dashboard_stats(self) -> dict:
        return {
            "total_students": self.db.students.count_documents({}),
            "total_faculties": self.db.faculties.count_documents({}),
            "total_offerings": self.db.class_offerings.count_documents({}),
            "pending_enrollments": self.db.enrollments.count_documents({"status": "Pending"}),
        }

    def get_faculty_offerings(self, faculty_id: int) -> list[dict]:
        offerings = list(
            self.db.class_offerings.find({"faculty_id": faculty_id}).sort("_id", 1)
        )
        result = []
        for o in offerings:
            oid = o["_id"]
            subject = self.db.subjects.find_one({"_id": o["subject_id"]})
            enrolled_count = self.db.enrollments.count_documents({
                "items.offering_id": oid, "status": "Approved"
            })
            result.append({
                "id": oid,
                "subject_id": o["subject_id"],
                "subject_name": subject["name"] if subject else "",
                "subject_code": subject["code"] if subject else "",
                "section": o["section"],
                "schedule": o["schedule"],
                "semester": o["semester"],
                "school_year": o["school_year"],
                "enrolled_count": enrolled_count,
            })
        return result

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
        total = self.db.enrollments.count_documents({})
        approved = self.db.enrollments.count_documents({"status": "Approved"})
        pending = self.db.enrollments.count_documents({"status": "Pending"})
        rejected = self.db.enrollments.count_documents({"status": "Rejected"})
        course_dist = list(self.db.enrollments.aggregate([
            {"$match": {"status": "Approved"}},
            {"$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "_id",
                "as": "student"
            }},
            {"$unwind": "$student"},
            {"$lookup": {
                "from": "courses",
                "localField": "student.course_id",
                "foreignField": "_id",
                "as": "course"
            }},
            {"$unwind": "$course"},
            {"$group": {"_id": "$course.name", "count": {"$sum": 1}}},
            {"$project": {"name": "$_id", "count": 1, "_id": 0}}
        ]))
        return {
            "total": total,
            "approved": approved,
            "pending": pending,
            "rejected": rejected,
            "course_distribution": course_dist,
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
        self._log(user, action)

    def list_audit_logs(self) -> list[dict]:
        return self._docs(
            self.db.audit_logs.find().sort("_id", -1).limit(100)
        )

    # ======================== HELPERS ========================

    def _doc_one(self, cursor):
        try:
            return self._doc(next(cursor))
        except (StopIteration, TypeError):
            return None
