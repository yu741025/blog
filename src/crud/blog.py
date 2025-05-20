from typing import Type, List, Optional, Dict, Any

from sqlalchemy import func, desc
from sqlalchemy.orm import Session, joinedload
from ulid import ULID

from src.database import models
from src.utils.handler import handle_error, handle_none_value


@handle_error
def create_blog(
        db: Session,
        author_id: str,
        title: str,
        content: str,
        summary: Optional[str] = None,
        cover_image_url: Optional[str] = None,
        is_draft: bool = True,
        tag_ids: Optional[List[str]] = None,
        category_ids: Optional[List[str]] = None,
        blog_id: str = str(ULID())
) -> models.Blog:
    blog = models.Blog(
        id=blog_id,
        title=title,
        content=content,
        summary=summary,
        cover_image_url=cover_image_url,
        is_draft=is_draft,
        author_id=author_id
    )
    
    db.add(blog)
    db.commit()
    
    # 添加標籤
    if tag_ids:
        tags = db.query(models.Tag).filter(models.Tag.id.in_(tag_ids)).all()
        blog.tags = tags
    
    # 添加分類
    if category_ids:
        categories = db.query(models.Category).filter(models.Category.id.in_(category_ids)).all()
        blog.categories = categories
    
    db.commit()
    db.refresh(blog)
    
    return blog


@handle_none_value("Blog")
@handle_error
def get_blog_by_id(db: Session, blog_id: str, increment_view: bool = False) -> models.Blog:
    # 使用joinedload預先載入相關數據，減少數據庫查詢次數
    blog = db.query(models.Blog).options(
        joinedload(models.Blog.author),
        joinedload(models.Blog.tags),
        joinedload(models.Blog.categories)
    ).filter(models.Blog.id == blog_id).first()
    
    if blog and increment_view:
        blog.view_count += 1
        db.commit()
    
    return blog


@handle_error
def get_blogs(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        tag_id: Optional[str] = None,
        category_id: Optional[str] = None,
        author_id: Optional[str] = None,
        search_term: Optional[str] = None,
        show_drafts: bool = False
) -> List[models.Blog]:
    query = db.query(models.Blog).join(models.User)
    
    # 根據查詢參數過濾
    if tag_id:
        query = query.join(models.Blog.tags).filter(models.Tag.id == tag_id)
    
    if category_id:
        query = query.join(models.Blog.categories).filter(models.Category.id == category_id)
    
    if author_id:
        query = query.filter(models.Blog.author_id == author_id)
    
    if search_term:
        search = f"%{search_term}%"
        query = query.filter(
            (models.Blog.title.ilike(search)) | 
            (models.Blog.content.ilike(search)) |
            (models.Blog.summary.ilike(search))
        )
    
    # 僅顯示已發布的文章，除非指定顯示草稿
    if not show_drafts:
        query = query.filter(models.Blog.is_draft == False)
    
    # 按創建時間降序排序
    query = query.order_by(desc(models.Blog.created_at))
    
    # 分頁
    blogs = query.offset(skip).limit(limit).all()
    
    return blogs


@handle_error
def update_blog(
        db: Session,
        blog_id: str,
        author_id: str,
        data: Dict[str, Any]
) -> Optional[models.Blog]:
    blog = get_blog_by_id(db, blog_id)
    
    # 確保只有作者才能更新文章
    if blog.author_id != author_id:
        return None
    
    # 更新文章屬性
    for key, value in data.items():
        if key in ['title', 'content', 'summary', 'cover_image_url', 'is_draft']:
            setattr(blog, key, value)
    
    # 更新標籤
    if 'tag_ids' in data and data['tag_ids'] is not None:
        tags = db.query(models.Tag).filter(models.Tag.id.in_(data['tag_ids'])).all()
        blog.tags = tags
    
    # 更新分類
    if 'category_ids' in data and data['category_ids'] is not None:
        categories = db.query(models.Category).filter(models.Category.id.in_(data['category_ids'])).all()
        blog.categories = categories
    
    db.commit()
    db.refresh(blog)
    
    return blog


@handle_error
def delete_blog(db: Session, blog_id: str, author_id: str) -> bool:
    blog = get_blog_by_id(db, blog_id)
    
    # 確保只有作者才能刪除文章
    if blog.author_id != author_id:
        return False
    
    # 刪除文章
    db.delete(blog)
    db.commit()
    
    return True


@handle_error
def like_blog(db: Session, blog_id: str) -> models.Blog:
    blog = get_blog_by_id(db, blog_id)
    
    blog.like_count += 1
    db.commit()
    db.refresh(blog)
    
    return blog
