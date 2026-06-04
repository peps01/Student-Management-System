from dataclasses import dataclass


@dataclass
class User:
    username: str
    name: str
    email: str
    password: str
    bio: str = ""
    role: str = "Student"
    join_date: str = ""
