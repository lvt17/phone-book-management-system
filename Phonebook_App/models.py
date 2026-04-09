from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    userid: Optional[int]
    user_name: str
    password: str  # stored as SHA-256 hash


@dataclass
class Category:
    cate_id: Optional[int]
    cate_name: str
    userid: int


@dataclass
class Contact:
    contact_id: Optional[int]
    contact_name: str
    phone: str
    email: str
    address: str
    userid: int
    cate_id: Optional[int] = None
    cate_name: Optional[str] = None  # populated via JOIN, not stored
