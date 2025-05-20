from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session

from src.crud import blog as blog_crud
from src.database import models
from src.dependencies.auth import get_current_user
from src.dependencies.basic import get_db
from src.schemas import blog as schemas
from src.utils import s3

router = APIRouter()


@router.post("", response_model=schemas.BlogDetail, status_code=status.HTTP_201_CREATED)
async def create_blog(
        blog_data: schemas.BlogCreate,
        current_user: Annotated[models.User, Depends(get_current_user)],
        db: Session = Depends(get_db)
):
    # 創建新部落格文章
    try:
        new_blog = blog_crud.create_blog(
            db=db,
            author_id=current_user.id,
            title=blog_data.title,
            content=blog_data.content,
            summary=blog_data.summary,
            cover_image_url=blog_data.cover_image_url,
            is_draft=blog_data.is_draft,
            tag_ids=blog_data.tag_ids,
            category_ids=blog_data.category_ids
        )
        
        # 構建響應
        return convert_blog_to_detail(new_blog)
    except Exception as e:
        print(f"創建博客文章失敗: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"創建部落格文章失敗: {str(e)}"
        )


@router.get("", response_model=List[schemas.BlogSummary])
async def get_blogs(
        skip: int = 0,
        limit: int = 10,
        tag_id: Optional[str] = None,
        category_id: Optional[str] = None,
        search: Optional[str] = None,
        author_id: Optional[str] = None,
        current_user: Annotated[models.User, Depends(get_current_user)] = None,
        db: Session = Depends(get_db)
):
    # 獲取部落格文章列表
    blogs = blog_crud.get_blogs(
        db=db,
        skip=skip,
        limit=limit,
        tag_id=tag_id,
        category_id=category_id,
        search_term=search,
        author_id=author_id,
        # 如果查看的是自己的文章，也顯示草稿
        show_drafts=author_id == current_user.id if current_user and author_id else False
    )
    
    # 構建響應
    return [convert_blog_to_summary(blog) for blog in blogs]


@router.get("/{blog_id}", response_model=schemas.BlogDetail)
async def get_blog(
        blog_id: str,
        increment_view: bool = Query(False, description="是否增加瀏覽次數"),
        db: Session = Depends(get_db)
):
    # 獲取單篇部落格文章
    blog = blog_crud.get_blog_by_id(db, blog_id, increment_view=increment_view)
    
    # 檢查是否為草稿
    if blog.is_draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到該文章或文章尚未發布"
        )
    
    # 構建響應
    return convert_blog_to_detail(blog)


@router.put("/{blog_id}", response_model=schemas.BlogDetail)
async def update_blog(
        blog_id: str,
        blog_data: schemas.BlogUpdate,
        current_user: Annotated[models.User, Depends(get_current_user)],
        db: Session = Depends(get_db)
):
    # 更新部落格文章
    updated_blog = blog_crud.update_blog(
        db=db,
        blog_id=blog_id,
        author_id=current_user.id,
        data=blog_data.dict(exclude_unset=True)
    )
    
    if not updated_blog:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您沒有權限更新這篇文章"
        )
    
    # 構建響應
    return convert_blog_to_detail(updated_blog)


@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(
        blog_id: str,
        current_user: Annotated[models.User, Depends(get_current_user)],
        db: Session = Depends(get_db)
):
    # 刪除部落格文章
    success = blog_crud.delete_blog(db, blog_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您沒有權限刪除這篇文章"
        )
    
    return


@router.post("/upload-cover", status_code=status.HTTP_200_OK)
async def upload_blog_cover(
        _: Annotated[models.User, Depends(get_current_user)],
        file: UploadFile = File(...)
):
    # 檢查文件類型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="僅支持圖片文件"
        )
    
    try:
        # 上傳封面圖片到S3
        upload_result = s3.upload_blog_cover_to_s3(file)
        
        return {
            "url": upload_result["public_url"],
            "filename": upload_result["filename"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上傳封面圖片失敗: {str(e)}"
        )


@router.post("/{blog_id}/like", response_model=schemas.BlogDetail)
async def like_blog(
        blog_id: str,
        db: Session = Depends(get_db)
):
    # 增加部落格文章喜歡次數
    blog = blog_crud.like_blog(db, blog_id)
    
    # 構建響應
    return convert_blog_to_detail(blog)


# 輔助函數，將Blog模型轉換為BlogDetail
def convert_blog_to_detail(blog: models.Blog) -> schemas.BlogDetail:
    # 檢查作者是否是列表，如果是，取第一個元素
    author = blog.author
    if isinstance(author, list) and author:
        author = author[0]
    
    # 獲取作者的帳號信息
    account = None
    if hasattr(author, 'account') and author.account:
        if isinstance(author.account, list):
            account = author.account[0]
        else:
            account = author.account
    
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
        author=schemas.UserDetail(
            id=author.id,
            name=author.name,
            username=account.username if account else "",
            bio=author.bio if hasattr(author, 'bio') else None,
            avatar_url=author.avatar_url if hasattr(author, 'avatar_url') else None,
            created_at=author.created_at.isoformat()
        ),
        tags=[
            schemas.TagDetail(id=tag.id, name=tag.name)
            for tag in blog.tags
        ] if blog.tags else [],
        categories=[
            schemas.CategoryDetail(
                id=category.id,
                name=category.name,
                description=category.description
            )
            for category in blog.categories
        ] if blog.categories else []
    )


# 輔助函數，將Blog模型轉換為BlogSummary
def convert_blog_to_summary(blog: models.Blog) -> schemas.BlogSummary:
    # 檢查作者是否是列表，如果是，取第一個元素
    author = blog.author
    if isinstance(author, list) and author:
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
        tags=[tag.name for tag in blog.tags] if blog.tags else [],
        categories=[category.name for category in blog.categories] if blog.categories else []
    )