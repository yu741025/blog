from typing import List, Optional

from sqlalchemy.orm import Session
from ulid import ULID

from src.database import models
from src.utils.handler import handle_error, handle_none_value


# 標籤相關CRUD
@handle_error
def create_tag(db: Session, name: str, tag_id: str = str(ULID())) -> models.Tag:
    tag = models.Tag(
        id=tag_id,
        name=name
    )
    
    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    return tag


@handle_none_value("Tag")
@handle_error
def get_tag_by_id(db: Session, tag_id: str) -> models.Tag:
    return db.query(models.Tag).filter(models.Tag.id == tag_id).first()


@handle_none_value("Tag")
@handle_error
def get_tag_by_name(db: Session, name: str) -> models.Tag:
    return db.query(models.Tag).filter(models.Tag.name == name).first()


@handle_error
def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tag]:
    return db.query(models.Tag).order_by(models.Tag.name).offset(skip).limit(limit).all()


@handle_error
def update_tag(db: Session, tag_id: str, name: str) -> models.Tag:
    tag = get_tag_by_id(db, tag_id)
    
    tag.name = name
    db.commit()
    db.refresh(tag)
    
    return tag


@handle_error
def delete_tag(db: Session, tag_id: str) -> bool:
    tag = get_tag_by_id(db, tag_id)
    
    db.delete(tag)
    db.commit()
    
    return True


# 分類相關CRUD
@handle_error
def create_category(
        db: Session,
        name: str,
        description: Optional[str] = None,
        category_id: str = str(ULID())
) -> models.Category:
    category = models.Category(
        id=category_id,
        name=name,
        description=description
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category


@handle_none_value("Category")
@handle_error
def get_category_by_id(db: Session, category_id: str) -> models.Category:
    return db.query(models.Category).filter(models.Category.id == category_id).first()


@handle_none_value("Category")
@handle_error
def get_category_by_name(db: Session, name: str) -> models.Category:
    return db.query(models.Category).filter(models.Category.name == name).first()


@handle_error
def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[models.Category]:
    return db.query(models.Category).order_by(models.Category.name).offset(skip).limit(limit).all()


@handle_error
def update_category(
        db: Session,
        category_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
) -> models.Category:
    category = get_category_by_id(db, category_id)
    
    if name is not None:
        category.name = name
    
    if description is not None:
        category.description = description
    
    db.commit()
    db.refresh(category)
    
    return category


@handle_error
def delete_category(db: Session, category_id: str) -> bool:
    category = get_category_by_id(db, category_id)
    
    db.delete(category)
    db.commit()
    
    return True
