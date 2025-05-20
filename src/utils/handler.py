from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def handle_none_value(item_name='Item'):
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result is None:
                raise HTTPException(status_code=404, detail=f"{item_name} Not found")
            return result

        return wrapper

    return decorator


def handle_error(func: Callable[..., Any]):
    """
    first argument should be the database session
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 檢查是否有任何參數
        if len(args) == 0 and 'db' not in kwargs:
            raise ValueError("Database session is required as first argument or 'db' keyword argument")
        
        # 檢查第一個參數是否是數據庫連接，或者是否有db關鍵字參數
        db = args[0] if len(args) > 0 else kwargs.get('db')
        
        # 確保db是Session類型
        if not isinstance(db, Session):
            raise ValueError("First argument or 'db' keyword should be a database session")
        
        try:
            return func(*args, **kwargs)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return wrapper


def handle_jwt_error(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return wrapper