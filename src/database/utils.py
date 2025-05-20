from sqlalchemy.orm import Session
from ulid import ULID

from src.crud.user import create_user
from src.crud.taxonomy import create_category, create_tag
from src.crud.blog import create_blog
from src.crud.comment import create_comment
from src.database.database import SessionLocal

def add_test_data():
    db: Session = SessionLocal()
    try:
        # 創建測試使用者
        test_user = create_user(db, "測試使用者", "test-username", "test-password", "test-user-id")
        admin_user = create_user(db, "管理員", "admin-username", "admin-password", "admin-user-id")
        
        # 調用 create_blog，傳遞 db 作為第一個參數，author_id 為第二個參數
        blog1 = create_blog(
            db=db,  # 必須是第一個參數
            author_id=test_user.id,  # 必須是第二個參數，使用剛創建的測試用戶ID
            title="測試1",
            content="這是測試1的內容"
            # 其他參數可以按需添加
        )
        
        print("Test users and blogs created successfully.")
    finally:
        db.close()  # 關閉數據庫連接
    