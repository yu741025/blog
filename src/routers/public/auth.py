from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import traceback

from src.crud import user as user_crud
from src.database import models
from src.dependencies.auth import authenticate_user
from src.dependencies.basic import get_db
from src.schemas import blog as schemas
from src.schemas.basic import Token
from src.utils.credentials import create_access_token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(get_db),
):
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        token = create_access_token({"sub": user.account[0].username})
        return Token(access_token=token, token_type="bearer")
    except Exception as e:
        print(f"登入失敗: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶名或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", response_model=schemas.UserDetail, status_code=status.HTTP_201_CREATED)
async def register(
        user_data: schemas.UserRegister,
        db: Session = Depends(get_db)
):
    try:
        # 檢查使用者名稱是否已存在
        existing_account = db.query(models.UserAccount).filter(
            models.UserAccount.username == user_data.username
        ).first()
        if existing_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"使用者名稱 '{user_data.username}' 已被使用"
            )
        
        # 創建新使用者 - 確保db是第一個參數！
        new_user = user_crud.create_user(
            db=db,  # 確保db是第一個參數
            name=user_data.name,
            username=user_data.username,
            password=user_data.password
        )
        
        # 檢查返回的user對象是否有所有需要的屬性
        bio = getattr(new_user, 'bio', None)
        avatar_url = getattr(new_user, 'avatar_url', None)
        
        return schemas.UserDetail(
            id=new_user.id,
            name=new_user.name,
            username=new_user.account[0].username if hasattr(new_user, 'account') and new_user.account else "",
            bio=bio,
            avatar_url=avatar_url,
            created_at=new_user.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"註冊失敗: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"註冊失敗: {str(e)}"
        )