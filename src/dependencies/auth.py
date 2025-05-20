import os
from typing import Annotated

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError
from sqlalchemy.orm import Session

from src.database import models
from src.dependencies.basic import get_db
from src.utils.credentials import verify_password, decode_token
from src.utils.handler import handle_error, handle_none_value

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/public/auth/login", auto_error=True)

API_KEY = os.getenv("ADMIN_API_KEY", "admin")
api_key_header = APIKeyHeader(name="X-ADMIN-TOKEN", auto_error=True, scheme_name="X-ADMIN-TOKEN")
super_admin_api_key_header = APIKeyHeader(name="X-SUPER-ADMIN-TOKEN", auto_error=True, scheme_name="X-SUPER-ADMIN-TOKEN")


@handle_none_value("User")
@handle_error
def get_user_by_username(db: Session, username: str) -> models.User | None:
    user = db.query(models.User).join(models.UserAccount).filter(models.UserAccount.username == username).first()
    return user


def authenticate_user(db: Session, username: str, password: str) -> models.User:
    user = get_user_by_username(db, username)
    if not user or not user.account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶不存在或密碼錯誤"
        )
    
    account = user.account[0] if isinstance(user.account, list) and user.account else user.account
    truth_password = account.password if hasattr(account, 'password') else None
    
    if not truth_password or not verify_password(password, truth_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶不存在或密碼錯誤"
        )
    return user


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
) -> models.User:
    try:
        # 解析令牌
        payload = decode_token(token)
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials (username not found)",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 獲取用戶
        try:
            user = get_user_by_username(db, username)
            return user
        except HTTPException as e:
            if e.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            raise
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        import traceback
        print(f"認證錯誤: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_admin_user(api_key: Annotated[str, Depends(api_key_header)] = None):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid api key"
        )


async def get_super_admin_user(api_key: Annotated[str, Depends(super_admin_api_key_header)] = None):
    if api_key != "admin.root":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid api key"
        )