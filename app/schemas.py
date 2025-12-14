from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

    @validator("username")
    def username_valid(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, hyphens and underscores")
        return v


class UserCreate(UserBase):
    password: str

    @validator("password")
    def password_valid(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    profile_text: Optional[str] = None
    avatar_path: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    profile_text: Optional[str] = None
    avatar_path: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserWithStats(UserResponse):
    posts_count: int = 0
    followers_count: int = 0
    following_count: int = 0


# Post schemas
class PostBase(BaseModel):
    post_title: str
    post_content: str
    is_published: bool = True

    @validator("post_title")
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        if len(v) > 300:
            raise ValueError("Title too long (max 300 characters)")
        return v.strip()

    @validator("post_content")
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class PostCreate(PostBase):
    tag_names: Optional[List[str]] = []


class PostUpdate(BaseModel):
    post_title: Optional[str] = None
    post_content: Optional[str] = None
    is_published: Optional[bool] = None
    tag_names: Optional[List[str]] = None


class TagResponse(BaseModel):
    id: int
    tag_name: str
    tag_description: Optional[str] = None
    
    class Config:
        from_attributes = True


class PostResponse(PostBase):
    id: int
    user_id: int
    created_at: datetime
    modified_at: datetime
    view_counter: int
    author: UserResponse
    tags: List[TagResponse] = []
    likes_count: int = 0
    comments_count: int = 0
    
    class Config:
        from_attributes = True


# Comment schemas
class CommentBase(BaseModel):
    comment_text: str

    @validator("comment_text")
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Comment cannot be empty")
        return v.strip()


class CommentCreate(CommentBase):
    parent_comment_id: Optional[int] = None


class CommentUpdate(BaseModel):
    comment_text: str


class CommentResponse(CommentBase):
    id: int
    post_id: int
    user_id: int
    parent_comment_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    was_edited: bool
    user: UserResponse
    
    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Tag schemas
class TagCreate(BaseModel):
    tag_name: str
    tag_description: Optional[str] = None

    @validator("tag_name")
    def tag_name_valid(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Tag name cannot be empty")
        if len(v) > 50:
            raise ValueError("Tag name too long (max 50 characters)")
        return v.strip().lower()


# Search and pagination
class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20

    @validator("page")
    def page_valid(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Page must be >= 1")
        return v

    @validator("page_size")
    def page_size_valid(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError("Page size must be between 1 and 100")
        return v
