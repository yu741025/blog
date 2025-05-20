from typing import List, Optional

from sqlalchemy.orm import Session, joinedload
from ulid import ULID

from src.database import models
from src.utils.handler import handle_error, handle_none_value


@handle_error
def create_comment(
        db: Session,
        user_id: str,
        blog_id: str,
        content: str,
        parent_id: Optional[str] = None,
        comment_id: str = str(ULID())
) -> models.Comment:
    comment = models.Comment(
        id=comment_id,
        content=content,
        blog_id=blog_id,
        user_id=user_id,
        parent_id=parent_id
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return comment


@handle_none_value("Comment")
@handle_error
def get_comment_by_id(db: Session, comment_id: str) -> models.Comment:
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()


@handle_error
def get_comments_by_blog_id(
        db: Session,
        blog_id: str,
        skip: int = 0,
        limit: int = 100
) -> List[models.Comment]:
    # 只獲取頂級評論（沒有父評論的評論）
    comments = db.query(models.Comment).options(
        joinedload(models.Comment.user),
        joinedload(models.Comment.replies).joinedload(models.Comment.user)
    ).filter(
        models.Comment.blog_id == blog_id,
        models.Comment.parent_id == None
    ).order_by(models.Comment.created_at.desc()).offset(skip).limit(limit).all()
    
    return comments


@handle_error
def delete_comment(db: Session, comment_id: str, user_id: str) -> bool:
    comment = get_comment_by_id(db, comment_id)
    
    # 確保只有評論作者才能刪除評論
    if comment.user_id != user_id:
        return False
    
    # 遞迴刪除所有回覆
    replies = db.query(models.Comment).filter(models.Comment.parent_id == comment_id).all()
    for reply in replies:
        delete_comment(db, reply.id, user_id)
    
    db.delete(comment)
    db.commit()
    
    return True
