from typing import Annotated, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import traceback

from src.crud import user as user_crud
from src.database import models
from src.dependencies.auth import get_current_user
from src.dependencies.basic import get_db
from src.schemas import base, blog as schemas
from src.utils import s3

router = APIRouter()


@router.post("/register", response_model=schemas.UserDetail, status_code=status.HTTP_201_CREATED)
async def register(
        user_data: schemas.UserRegister,
        db: Session = Depends(get_db)
):
    try:
        # 檢查使用者名稱是否已存在
        try:
            existing_user = user_crud.get_user_by_username(db, user_data.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"使用者名稱 '{user_data.username}' 已被使用"
                )
        except HTTPException as e:
            if e.status_code != 404:  # 如果錯誤不是 "找不到用戶"，則重新拋出異常
                raise
        
        # 創建新使用者
        new_user = user_crud.create_user(
            db=db,
            name=user_data.name,
            username=user_data.username,
            password=user_data.password
        )
        
        return schemas.UserDetail(
            id=new_user.id,
            name=new_user.name,
            username=new_user.account[0].username,
            bio=new_user.bio,
            avatar_url=new_user.avatar_url,
            created_at=new_user.created_at.isoformat()
        )
    except Exception as e:
        print(f"註冊失敗: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"註冊失敗: {str(e)}"
        )


@router.get("/me", response_model=schemas.UserDetail)
async def get_current_user_detail(
        current_user: Annotated[models.User, Depends(get_current_user)]
):
    return schemas.UserDetail(
        id=current_user.id,
        name=current_user.name,
        username=current_user.account[0].username,
        bio=current_user.bio,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at.isoformat()
    )


@router.put("/me", response_model=schemas.UserDetail)
async def update_user_info(
        user_data: schemas.UserUpdate,
        current_user: Annotated[models.User, Depends(get_current_user)],
        db: Session = Depends(get_db)
):
    updated_user = user_crud.update_user(
        db=db,
        user_id=current_user.id,
        name=user_data.name,
        bio=user_data.bio
    )
    
    return schemas.UserDetail(
        id=updated_user.id,
        name=updated_user.name,
        username=updated_user.account[0].username,
        bio=updated_user.bio,
        avatar_url=updated_user.avatar_url,
        created_at=updated_user.created_at.isoformat()
    )

@router.post("/me/avatar", response_model=schemas.UserDetail)
async def upload_avatar(
    current_user: Annotated[models.User, Depends(get_current_user)],
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 檢查文件類型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="僅支持圖片文件"
        )
    try:
        # 上傳頭像到S3
        upload_result = s3.upload_avatar_to_s3(file)
        # 更新使用者頭像URL
        updated_user = user_crud.update_user_avatar(
            db=db,
            user_id=current_user.id,
            avatar_url=upload_result["public_url"]
        )
        return schemas.UserDetail(
            id=updated_user.id,
            name=updated_user.name,
            username=updated_user.account[0].username,
            bio=updated_user.bio,
            avatar_url=updated_user.avatar_url,
            created_at=updated_user.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上傳頭像失敗: {str(e)}"
        )