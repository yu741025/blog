from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


def lazy_relationship(*args, **kwargs):
    return relationship(*args, uselist=True, **kwargs)


# 文章與標籤的多對多關聯表
blog_tag_association = Table(
    'blog_tag_association',
    Base.metadata,
    Column('blog_id', String(36), ForeignKey('blogs.id')),
    Column('tag_id', String(36), ForeignKey('tags.id'))
)

# 文章與分類的多對多關聯表
blog_category_association = Table(
    'blog_category_association',
    Base.metadata,
    Column('blog_id', String(36), ForeignKey('blogs.id')),
    Column('category_id', String(36), ForeignKey('categories.id'))
)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    name = Column(String(16), unique=True, index=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(512), nullable=True)

    account = lazy_relationship("UserAccount", back_populates="user")
    blogs = lazy_relationship("Blog", back_populates="author")
    comments = lazy_relationship("Comment", back_populates="user")


class UserAccount(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    username = Column(String(16), unique=True, index=True)
    password = Column(String(256))

    user_id = Column(String(36), ForeignKey("users.id"))
    user = lazy_relationship("User", back_populates="account")


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    title = Column(String(256), index=True)
    content = Column(Text)
    summary = Column(String(512), nullable=True)
    cover_image_url = Column(String(512), nullable=True)
    is_draft = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)

    author_id = Column(String(36), ForeignKey("users.id"))
    author = lazy_relationship("User", back_populates="blogs")
    
    comments = lazy_relationship("Comment", back_populates="blog")
    tags = relationship("Tag", secondary=blog_tag_association, back_populates="blogs")
    categories = relationship("Category", secondary=blog_category_association, back_populates="blogs")


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    name = Column(String(64), unique=True, index=True)
    description = Column(String(256), nullable=True)
    
    blogs = relationship("Blog", secondary=blog_category_association, back_populates="categories")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    name = Column(String(64), unique=True, index=True)
    
    blogs = relationship("Blog", secondary=blog_tag_association, back_populates="tags")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    content = Column(Text)
    
    blog_id = Column(String(36), ForeignKey("blogs.id"))
    blog = lazy_relationship("Blog", back_populates="comments")
    
    user_id = Column(String(36), ForeignKey("users.id"))
    user = lazy_relationship("User", back_populates="comments")
    
    parent_id = Column(String(36), ForeignKey("comments.id"), nullable=True)
    replies = lazy_relationship("Comment", backref="parent", remote_side=[id])
