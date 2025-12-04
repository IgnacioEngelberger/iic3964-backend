from typing import List, Optional

from pydantic import BaseModel


class UserListItem(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    role: str
    is_deleted: bool


class UserListResponse(BaseModel):
    count: int
    total: int
    page: int
    page_size: int
    results: List[UserListItem]
