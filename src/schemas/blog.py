from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr


class TokenData(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None


class UserRegister(BaseModel):
    name: str = Field(..., description="User's name")
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="Password")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, description="User's name")
    bio: Optional[str] = Field(None, description="User's biography")


class UserDetail(BaseModel):
    id: str = Field(..., description="User ID")
    name: str = Field(..., description="User Name")
    username: str = Field(..., description="User Account Username")
    bio: Optional[str] = Field(None, description="User's biography")
    avatar_url: Optional[str] = Field(None, description="User's avatar URL")
    created_at: str = Field(..., description="User creation date")


class BlogCreate(BaseModel):
    title: str = Field(..., description="Blog title")
    content: str = Field(..., description="Blog content")
    summary: Optional[str] = Field(None, description="Blog summary")
    cover_image_url: Optional[str] = Field(None, description="Cover image URL")
    is_draft: bool = Field(True, description="Is this a draft")
    tag_ids: Optional[List[str]] = Field(None, description="Tag IDs")
    category_ids: Optional[List[str]] = Field(None, description="Category IDs")


class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Blog title")
    content: Optional[str] = Field(None, description="Blog content")
    summary: Optional[str] = Field(None, description="Blog summary")
    cover_image_url: Optional[str] = Field(None, description="Cover image URL")
    is_draft: Optional[bool] = Field(None, description="Is this a draft")
    tag_ids: Optional[List[str]] = Field(None, description="Tag IDs")
    category_ids: Optional[List[str]] = Field(None, description="Category IDs")


class BlogDetail(BaseModel):
    id: str = Field(..., description="Blog ID")
    title: str = Field(..., description="Blog title")
    content: str = Field(..., description="Blog content")
    summary: Optional[str] = Field(None, description="Blog summary")
    cover_image_url: Optional[str] = Field(None, description="Cover image URL")
    is_draft: bool = Field(..., description="Is this a draft")
    view_count: int = Field(..., description="View count")
    like_count: int = Field(..., description="Like count")
    created_at: str = Field(..., description="Creation date")
    updated_at: str = Field(..., description="Last update date")
    author: UserDetail = Field(..., description="Blog author")
    tags: List["TagDetail"] = Field(default=[], description="Blog tags")
    categories: List["CategoryDetail"] = Field(default=[], description="Blog categories")


class BlogSummary(BaseModel):
    id: str = Field(..., description="Blog ID")
    title: str = Field(..., description="Blog title")
    summary: Optional[str] = Field(None, description="Blog summary")
    cover_image_url: Optional[str] = Field(None, description="Cover image URL")
    created_at: str = Field(..., description="Creation date")
    view_count: int = Field(..., description="View count")
    like_count: int = Field(..., description="Like count")
    author_name: str = Field(..., description="Author name")
    tags: List[str] = Field(default=[], description="Tag names")
    categories: List[str] = Field(default=[], description="Category names")


class CommentCreate(BaseModel):
    content: str = Field(..., description="Comment content")
    blog_id: str = Field(..., description="Blog ID")
    parent_id: Optional[str] = Field(None, description="Parent comment ID for replies")


class CommentDetail(BaseModel):
    id: str = Field(..., description="Comment ID")
    content: str = Field(..., description="Comment content")
    created_at: str = Field(..., description="Creation date")
    user: UserDetail = Field(..., description="Comment author")
    replies: List["CommentDetail"] = Field(default=[], description="Replies to this comment")


class TagCreate(BaseModel):
    name: str = Field(..., description="Tag name")


class TagDetail(BaseModel):
    id: str = Field(..., description="Tag ID")
    name: str = Field(..., description="Tag name")


class CategoryCreate(BaseModel):
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")


class CategoryDetail(BaseModel):
    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")


# Resolve forward references
BlogDetail.update_forward_refs()
CommentDetail.update_forward_refs()
