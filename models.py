from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    username: str
    name: str
    email: str
    password: str
    bio: str = ""
    role: str = "Student"
    join_date: str = ""


@dataclass
class Student:
    id: Optional[int] = None
    student_number: str = ""
    name: str = ""
    email: str = ""
    course_id: int = 0
    course_name: str = ""
    year: int = 1
    username: str = ""
    section_id: Optional[int] = None


@dataclass
class Department:
    id: Optional[int] = None
    name: str = ""
    code: str = ""


@dataclass
class Course:
    id: Optional[int] = None
    name: str = ""
    code: str = ""
    department_id: int = 0
    department_name: str = ""


@dataclass
class Subject:
    id: Optional[int] = None
    name: str = ""
    code: str = ""
    course_id: int = 0
    course_name: str = ""
    units: int = 3


@dataclass
class Faculty:
    id: Optional[int] = None
    username: str = ""
    name: str = ""
    email: str = ""
    department_id: int = 0
    department_name: str = ""


@dataclass
class ClassOffering:
    id: Optional[int] = None
    subject_id: int = 0
    subject_name: str = ""
    subject_code: str = ""
    section: str = ""
    schedule: str = ""
    faculty_id: int = 0
    faculty_name: str = ""
    semester: str = ""
    school_year: str = ""


@dataclass
class Enrollment:
    id: Optional[int] = None
    student_id: int = 0
    student_name: str = ""
    student_number: str = ""
    status: str = "Pending"
    date: str = ""
    items: list = field(default_factory=list)


@dataclass
class EnrollmentItem:
    id: Optional[int] = None
    enrollment_id: int = 0
    offering_id: int = 0
    subject_name: str = ""
    subject_code: str = ""


@dataclass
class AttendanceRecord:
    id: Optional[int] = None
    offering_id: int = 0
    student_id: int = 0
    student_name: str = ""
    date: str = ""
    status: str = "Present"


@dataclass
class GradeRecord:
    id: Optional[int] = None
    offering_id: int = 0
    student_id: int = 0
    student_name: str = ""
    subject_name: str = ""
    prelim: float = 0
    midterm: float = 0
    final: float = 0
    final_grade: float = 0
    grade_status: str = ""


@dataclass
class Announcement:
    id: Optional[int] = None
    title: str = ""
    body: str = ""
    author: str = ""
    date: str = ""


@dataclass
class AuditLog:
    id: Optional[int] = None
    user: str = ""
    action: str = ""
    timestamp: str = ""
