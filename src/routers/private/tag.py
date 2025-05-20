from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import taxonomy as taxonomy_crud
from src.database import models
from src.dependencies.auth import get_current_user
from src.dependencies.basic import get_db
from src.schemas import blog as schemas

router = APIRouter()


@router.get("", response_model=List[schemas.TagDetail])
async def get_tags(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    # 獲取所有標籤
    tags = taxonomy_crud.get_tags(db, skip=skip, limit=limit)
    
    # 構建響應
    return [
        schemas.TagDetail(
            id=tag.id,
            name=tag.name
        )
        for tag in tags
    ]


@router.post("", response_model=schemas.TagDetail, status_code=status.HTTP_201_CREATED)
async def create_tag(
        tag_data: schemas.TagCreate,
        current_user: Annotated[models.User, Depends(get_current_user)],
        db: Session = Depends(get_db)
):
    # 檢查標籤名稱是否已存在
    try:
        existing_tag = taxonomy_crud.get_tag_by_name(db, tag_data.name)
        if existing_tag:
            return schemas.TagDetail(id=existing_tag.id, name=existing_tag.name)
    except HTTPException as e:
        if e.status_code != 404:  # 如果錯誤不是 "找不到標籤"，則重新拋出異常
            raise
    
    # 創建新標籤
    new_tag = taxonomy_crud.create_tag(
        db=db,
        name=tag_data.name
    )
    
    # 構建響應
    return schemas.TagDetail(
        id=new_tag.id,
        name=new_tag.name
    )
