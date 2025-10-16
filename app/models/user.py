from datetime import datetime

from pydantic import BaseModel, validator


class UserBase(BaseModel):
    email: str
    login: str

    @validator("email")
    def email_valid(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v


class UserCreate(UserBase):
    password: str

    @validator("password")
    def password_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v

    @validator("login")
    def login_length(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Login must be at least 3 characters long")
        return v


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
