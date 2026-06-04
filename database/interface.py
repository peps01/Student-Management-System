from abc import ABC, abstractmethod
from typing import Optional


class Repository(ABC):

    @abstractmethod
    def get_user(self, username: str) -> Optional[dict]:
        ...

    @abstractmethod
    def get_dashboard_stats(self) -> dict:
        ...

    @abstractmethod
    def create_user(self, username: str, name: str, email: str, password: str, role: str) -> dict:
        ...
