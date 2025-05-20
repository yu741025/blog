from typing import Type, List, Optional

from sqlalchemy.orm import Session
from ulid import ULID

from src.database import models
from src.utils.credentials import hash_password
from src.utils.handler import handle_error, handle_none_value


@handle_none_value("User")
@handle_error
def get_user_by_id(db: Session, user_id: str) -> Type[models.User] | models.User | None:
    user = db.query(models.User).filter_by(id=user_id).first()
    return user


@handle_none_value("User")
@handle_error
def get_user_by_username(db: Session, username: str) -> models.User | None:
    user = db.query(models.User).join(models.UserAccount).filter(models.UserAccount.username == username).first()
    return user


@handle_error
def create_user(
        db: Session,
        name: str,
        username: str,
        password: str,
        user_id: str = str(ULID())
) -> Type[models.User] | models.User | None:
    user = models.User(
        id=user_id,
        name=name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    account = models.UserAccount(
        id=str(ULID()),
        username=username,
        password=hash_password(password),
        user_id=user.id
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    db.refresh(user)

    return user


@handle_error
def update_user(
        db: Session,
        user_id: str,
        name: Optional[str] = None,
        bio: Optional[str] = None
) -> models.User:
    user = get_user_by_id(db, user_id)
    
    if name is not None:
        user.name = name
    
    if bio is not None:
        user.bio = bio
    
    db.commit()
    db.refresh(user)
    
    return user


@handle_error
def update_user_avatar(
        db: Session,
        user_id: str,
        avatar_url: str
) -> models.User:
    user = get_user_by_id(db, user_id)
    
    user.avatar_url = avatar_url
    
    db.commit()
    db.refresh(user)
    
    return user