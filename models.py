from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    username: str
    name: str
    email: str
    password: str
    bio: str = ""
    role: str = "Administrator"
    join_date: str = ""


@dataclass
class Student:
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    course: str = ""
    year: int = 1


@dataclass
class GradeRecord:
    student_id: int
    name: str = ""
    grades: dict = field(default_factory=lambda: {
        "Math": 0, "English": 0, "Science": 0, "History": 0, "PE": 0
    })


@dataclass
class Attendance:
    student_id: int
    name: str = ""
    records: list = field(default_factory=lambda: ["Present"] * 5)


@dataclass
class Announcement:
    id: Optional[int] = None
    title: str = ""
    body: str = ""
    author: str = ""
    date: str = ""
