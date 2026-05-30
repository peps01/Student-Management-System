from abc import ABC, abstractmethod
from typing import Optional


class Repository(ABC):

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

    @abstractmethod
    def list_grades(self) -> list[dict]:
        ...

    @abstractmethod
    def update_grade(self, student_id: int, subject: str, score: float) -> bool:
        ...

    @abstractmethod
    def list_attendance(self) -> list[dict]:
        ...

    @abstractmethod
    def toggle_attendance(self, student_id: int, day_index: int) -> bool:
        ...

    @abstractmethod
    def list_announcements(self) -> list[dict]:
        ...

    @abstractmethod
    def add_announcement(self, data: dict) -> dict:
        ...
