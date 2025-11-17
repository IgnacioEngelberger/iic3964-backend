from pydantic import BaseModel, EmailStr

class UserAuth(BaseModel):
    email: EmailStr
    password: str

class UserCreate(UserAuth):
    first: str
    last: str