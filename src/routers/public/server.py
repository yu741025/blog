from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import blog as blog_crud, taxonomy as taxonomy_crud
from src.dependencies.basic import get_db
from src.routers.public import auth
from src.schemas import blog as schemas

router = APIRouter()

# 正確引入認證路由
router.include_router(auth.router, prefix="/auth", tags=["認證"])


@router.get("/blogs", response_model=List[schemas.BlogSummary], tags=["部落格"])
async def get_public_blogs(
        skip: int = 0,
        limit: int = 10,
        tag_id: str = None,
        category_id: str = None,
        search: str = None,
        db: Session = Depends(get_db)
):
    try:
        # 獲取公開部落格文章列表 (不包括草稿)
        blogs = blog_crud.get_blogs(
            db=db,
            skip=skip,
            limit=limit,
            tag_id=tag_id,
            category_id=category_id,
            search_term=search,
            show_drafts=False
        )
        
        # 構建響應
        return [convert_blog_to_summary(blog) for blog in blogs]
    except Exception as e:
        import traceback
        print(f"獲取部落格列表錯誤: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取部落格列表失敗: {str(e)}"
        )


@router.get("/blogs/{blog_id}", response_model=schemas.BlogDetail, tags=["部落格"])
async def get_public_blog(
        blog_id: str,
        db: Session = Depends(get_db)
):
    try:
        # 獲取公開部落格文章詳情 (同時增加瀏覽次數)
        blog = blog_crud.get_blog_by_id(db, blog_id, increment_view=True)
        
        # 檢查是否為草稿
        if blog.is_draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="找不到該文章或文章尚未發布"
            )
        
        # 構建響應
        return convert_blog_to_detail(blog)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"獲取部落格詳情錯誤: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取部落格詳情失敗: {str(e)}"
        )


@router.get("/categories", response_model=List[schemas.CategoryDetail], tags=["分類"])
async def get_public_categories(
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


@router.get("/tags", response_model=List[schemas.TagDetail], tags=["標籤"])
async def get_public_tags(
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


# 輔助函數，將Blog模型轉換為BlogDetail
def convert_blog_to_detail(blog: object) -> schemas.BlogDetail:
    # 處理作者資訊 - 修正以處理InstrumentedList
    author = blog.author
    if isinstance(author, list) and author:
        # 如果author是一個列表（InstrumentedList），取第一個元素
        author = author[0]
    
    author_detail = schemas.UserDetail(
        id=author.id,
        name=author.name,
        username=author.account[0].username if hasattr(author, 'account') and author.account else "",
        bio=getattr(author, 'bio', None),
        avatar_url=getattr(author, 'avatar_url', None),
        created_at=author.created_at.isoformat()
    )
    
    return schemas.BlogDetail(
        id=blog.id,
        title=blog.title,
        content=blog.content,
        summary=blog.summary,
        cover_image_url=blog.cover_image_url,
        is_draft=blog.is_draft,
        view_count=blog.view_count,
        like_count=blog.like_count,
        created_at=blog.created_at.isoformat(),
        updated_at=blog.updated_at.isoformat(),
        author=author_detail,
        tags=[
            schemas.TagDetail(id=tag.id, name=tag.name)
            for tag in blog.tags
        ],
        categories=[
            schemas.CategoryDetail(
                id=category.id,
                name=category.name,
                description=category.description
            )
            for category in blog.categories
        ]
    )


# 輔助函數，將Blog模型轉換為BlogSummary
def convert_blog_to_summary(blog: object) -> schemas.BlogSummary:
    # 處理作者資訊 - 修正以處理InstrumentedList
    author = blog.author
    if isinstance(author, list) and author:
        # 如果author是一個列表（InstrumentedList），取第一個元素
        author = author[0]
    
    return schemas.BlogSummary(
        id=blog.id,
        title=blog.title,
        summary=blog.summary,
        cover_image_url=blog.cover_image_url,
        created_at=blog.created_at.isoformat(),
        view_count=blog.view_count,
        like_count=blog.like_count,
        author_name=author.name,
        tags=[tag.name for tag in blog.tags],
        categories=[category.name for category in blog.categories]
    )