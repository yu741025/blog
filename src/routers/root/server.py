from fastapi import APIRouter

from src.routers.root import category
from src.schemas import blog as schemas

router = APIRouter()

router.include_router(category.router, prefix="/categories", tags=["分類管理"])