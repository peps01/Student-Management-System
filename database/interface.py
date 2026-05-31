from abc import ABC, abstractmethod
from typing import Optional


class Repository(ABC):

    # ---- Auth / Users ----

    @abstractmethod
    def get_user(self, username: str) -> Optional[dict]:
        ...

    @abstractmethod
    def update_user(self, username: str, data: dict) -> bool:
        ...

    @abstractmethod
    def change_password(self, username: str, current: str, new: str) -> bool:
        ...

    @abstractmethod
    def create_user(self, username: str, name: str, email: str, password: str, role: str) -> dict:
        ...

    # ---- Departments ----

    @abstractmethod
    def list_departments(self) -> list[dict]:
        ...

    @abstractmethod
    def get_department(self, dept_id: int) -> Optional[dict]:
        ...

    @abstractmethod
    def add_department(self, data: dict) -> dict:
        ...

    @abstractmethod
    def update_department(self, dept_id: int, data: dict) -> bool:
        ...

    @abstractmethod
    def delete_department(self, dept_id: int) -> bool:
        ...

    # ---- Courses ----

    @abstractmethod
    def list_courses(self) -> list[dict]:
        ...

    @abstractmethod
    def get_course(self, course_id: int) -> Optional[dict]:
        ...

    @abstractmethod
    def add_course(self, data: dict) -> dict:
        ...

    @abstractmethod
    def update_course(self, course_id: int, data: dict) -> bool:
        ...

    @abstractmethod
    def delete_course(self, course_id: int) -> bool:
        ...

    # ---- Subjects ----

    @abstractmethod
    def list_subjects(self) -> list[dict]:
        ...

    @abstractmethod
    def get_subject(self, subject_id: int) -> Optional[dict]:
        ...

    @abstractmethod
    def add_subject(self, data: dict) -> dict:
        ...

    @abstractmethod
    def update_subject(self, subject_id: int, data: dict) -> bool:
        ...

    @abstractmethod
    def delete_subject(self, subject_id: int) -> bool:
        ...

    # ---- Faculty ----

    @abstractmethod
    def list_faculties(self) -> list[dict]:
        ...

    @abstractmethod
    def get_faculty(self, faculty_id: int) -> Optional[dict]:
        ...

    @abstractmethod
    def add_faculty(self, data: dict) -> dict:
        ...

    @abstractmethod
    def update_faculty(self, faculty_id: int, data: dict) -> bool:
        ...

    @abstractmethod
    def delete_faculty(self, faculty_id: int) -> bool:
        ...

    # ---- Class Offerings ----

    @abstractmethod
    def list_offerings(self) -> list[dict]:
        ...

    @abstractmethod
    def get_offering(self, offering_id: int) -> Optional[dict]:
        ...

    @abstractmethod
    def add_offering(self, data: dict) -> dict:
        ...

    @abstractmethod
    def update_offering(self, offering_id: int, data: dict) -> bool:
        ...

    @abstractmethod
    def delete_offering(self, offering_id: int) -> bool:
        ...

    # ---- Students ----

    @abstractmethod
    def list_students(self) -> list[dict]:
        ...

    @abstractmethod
    def get_student(self, student_id: int) -> Optional[dict]:
        ...

    @abstractmethod
    def add_student(self, data: dict) -> dict:
        ...

    @abstractmethod
    def update_student(self, student_id: int, data: dict) -> bool:
        ...

    @abstractmethod
    def delete_student(self, student_id: int) -> bool:
        ...

    # ---- Enrollments ----

    @abstractmethod
    def list_enrollments(self, status: Optional[str] = None) -> list[dict]:
        ...

    @abstractmethod
    def get_enrollment(self, enrollment_id: int) -> Optional[dict]:
        ...

    @abstractmethod
    def create_enrollment(self, student_id: int, offering_ids: list[int]) -> dict:
        ...

    @abstractmethod
    def approve_enrollment(self, enrollment_id: int) -> bool:
        ...

    @abstractmethod
    def reject_enrollment(self, enrollment_id: int) -> bool:
        ...

    @abstractmethod
    def get_student_enrollments(self, student_id: int) -> list[dict]:
        ...

    # ---- Attendance ----

    @abstractmethod
    def list_attendance(self, offering_id: int) -> list[dict]:
        ...

    @abstractmethod
    def get_attendance(self, offering_id: int, student_id: int) -> Optional[dict]:
        ...

    @abstractmethod
    def mark_attendance(self, offering_id: int, student_id: int, date: str, status: str) -> dict:
        ...

    @abstractmethod
    def get_student_attendance_summary(self, student_id: int) -> dict:
        ...

    # ---- Grades ----

    @abstractmethod
    def list_grades(self, offering_id: int) -> list[dict]:
        ...

    @abstractmethod
    def get_grade(self, offering_id: int, student_id: int) -> Optional[dict]:
        ...

    @abstractmethod
    def upsert_grade(self, offering_id: int, student_id: int, data: dict) -> dict:
        ...

    @abstractmethod
    def get_student_grades(self, student_id: int) -> list[dict]:
        ...

    # ---- Announcements ----

    @abstractmethod
    def list_announcements(self) -> list[dict]:
        ...

    @abstractmethod
    def add_announcement(self, data: dict) -> dict:
        ...

    # ---- Profile ----

    @abstractmethod
    def get_student_by_username(self, username: str) -> Optional[dict]:
        ...

    @abstractmethod
    def get_faculty_by_username(self, username: str) -> Optional[dict]:
        ...

    # ---- Dashboard / Reports ----

    @abstractmethod
    def get_dashboard_stats(self) -> dict:
        ...

    @abstractmethod
    def get_faculty_offerings(self, faculty_id: int) -> list[dict]:
        ...

    @abstractmethod
    def get_student_dashboard(self, student_id: int) -> dict:
        ...

    @abstractmethod
    def get_enrollment_report(self) -> dict:
        ...

    @abstractmethod
    def get_attendance_report(self, offering_id: int) -> dict:
        ...

    @abstractmethod
    def get_grade_report(self, offering_id: int) -> dict:
        ...

    # ---- Audit Log ----

    @abstractmethod
    def add_audit_log(self, user: str, action: str) -> None:
        ...

    @abstractmethod
    def list_audit_logs(self) -> list[dict]:
        ...
