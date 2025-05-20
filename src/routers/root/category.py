from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import taxonomy as taxonomy_crud
from src.database import models
from src.dependencies.auth import get_admin_user
from src.dependencies.basic import get_db
from src.schemas import blog as schemas

router = APIRouter()


@router.get("", response_model=List[schemas.CategoryDetail])
async def get_categories(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    # 獲取所有分類
    categories = taxonomy_crud.get_categories(db, skip=skip, limit=limit)
    
    # 構建響應
    return [
        schemas.CategoryDetail(
            id=category.id,
            name=category.name,
            description=category.description
        )
        for category in categories
    ]


@router.post("", response_model=schemas.CategoryDetail, status_code=status.HTTP_201_CREATED)
async def create_category(
        category_data: schemas.CategoryCreate,
        _: Annotated[None, Depends(get_admin_user)],
        db: Session = Depends(get_db)
):
    # 檢查分類名稱是否已存在
    try:
        existing_category = taxonomy_crud.get_category_by_name(db, category_data.name)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"分類名稱 '{category_data.name}' 已存在"
            )
    except HTTPException as e:
        if e.status_code != 404:  # 如果錯誤不是 "找不到分類"，則重新拋出異常
            raise
    
    # 創建新分類
    new_category = taxonomy_crud.create_category(
        db=db,
        name=category_data.name,
        description=category_data.description
    )
    
    # 構建響應
    return schemas.CategoryDetail(
        id=new_category.id,
        name=new_category.name,
        description=new_category.description
    )


@router.put("/{category_id}", response_model=schemas.CategoryDetail)
async def update_category(
        category_id: str,
        category_data: schemas.CategoryCreate,
        _: Annotated[None, Depends(get_admin_user)],
        db: Session = Depends(get_db)
):
    # 檢查分類是否存在
    taxonomy_crud.get_category_by_id(db, category_id)
    
    # 檢查更新後的名稱是否與其他分類衝突
    if category_data.name:
        try:
            existing_category = taxonomy_crud.get_category_by_name(db, category_data.name)
            if existing_category and existing_category.id != category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"分類名稱 '{category_data.name}' 已被使用"
                )
        except HTTPException as e:
            if e.status_code != 404:  # 如果錯誤不是 "找不到分類"，則重新拋出異常
                raise
    
    # 更新分類
    updated_category = taxonomy_crud.update_category(
        db=db,
        category_id=category_id,
        name=category_data.name,
        description=category_data.description
    )
    
    # 構建響應
    return schemas.CategoryDetail(
        id=updated_category.id,
        name=updated_category.name,
        description=updated_category.description
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
        category_id: str,
        _: Annotated[None, Depends(get_admin_user)],
        db: Session = Depends(get_db)
):
    # 刪除分類
    taxonomy_crud.delete_category(db, category_id)
    
    return
