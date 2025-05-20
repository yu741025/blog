from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import comment as comment_crud
from src.database import models
from src.dependencies.auth import get_current_user
from src.dependencies.basic import get_db
from src.schemas import blog as schemas

router = APIRouter()


@router.post("", response_model=schemas.CommentDetail, status_code=status.HTTP_201_CREATED)
async def create_comment(
        comment_data: schemas.CommentCreate,
        current_user: Annotated[models.User, Depends(get_current_user)],
        db: Session = Depends(get_db)
):
    try:
        # 創建新評論，讓系統自動生成ID
        new_comment = comment_crud.create_comment(
            db=db,
            user_id=current_user.id,
            blog_id=comment_data.blog_id,
            content=comment_data.content,
            parent_id=comment_data.parent_id
            # 不傳遞comment_id參數，讓函數自動生成
        )
        
        # 構建響應
        return convert_comment_to_detail(new_comment)
    except Exception as e:
        import traceback
        print(f"創建評論錯誤: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"創建評論失敗: {str(e)}"
        )


@router.get("/blog/{blog_id}", response_model=List[schemas.CommentDetail])
async def get_blog_comments(
        blog_id: str,
        skip: int = 0,
        limit: int = 50,
        db: Session = Depends(get_db)
):
    # 獲取部落格文章的評論
    comments = comment_crud.get_comments_by_blog_id(
        db=db,
        blog_id=blog_id,
        skip=skip,
        limit=limit
    )
    
    # 構建響應
    return [convert_comment_to_detail(comment) for comment in comments]


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        comment_id: str,
        current_user: Annotated[models.User, Depends(get_current_user)],
        db: Session = Depends(get_db)
):
    # 刪除評論
    success = comment_crud.delete_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您沒有權限刪除這條評論"
        )
    
    return


# 輔助函數，將Comment模型轉換為CommentDetail
def convert_comment_to_detail(comment: models.Comment) -> schemas.CommentDetail:
    # 檢查用戶是否存在
    user = comment.user
    if isinstance(user, list) and user:
        user = user[0]
    
    user_detail = schemas.UserDetail(
        id=user.id,
        name=user.name,
        username=user.account[0].username if hasattr(user, 'account') and user.account else "",
        bio=getattr(user, 'bio', None),
        avatar_url=getattr(user, 'avatar_url', None),
        created_at=user.created_at.isoformat()
    )
    
    # 檢查是否有回覆
    replies = []
    if hasattr(comment, 'replies') and comment.replies:
        replies = [convert_comment_to_detail(reply) for reply in comment.replies]
    
    return schemas.CommentDetail(
        id=comment.id,
        content=comment.content,
        created_at=comment.created_at.isoformat(),
        user=user_detail,
        replies=replies
    )