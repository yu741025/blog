
from fastapi import APIRouter, Depends

from src.dependencies.auth import get_current_user
from src.routers.private import auth, user, blog, comment, tag
from src.schemas import blog as schemas

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["認證"])
router.include_router(user.router, prefix="/users", tags=["使用者"])
router.include_router(blog.router, prefix="/blogs", tags=["部落格"])
router.include_router(comment.router, prefix="/comments", tags=["評論"])
router.include_router(tag.router, prefix="/tags", tags=["標籤"])