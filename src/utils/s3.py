import os
import time
from tempfile import NamedTemporaryFile
from typing import Dict, Any

import boto3
from botocore.config import Config
from fastapi import UploadFile

# S3客戶端
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION'),
    config=Config(s3={"use_accelerate_endpoint": False})
)

# S3 Bucket名稱
S3_BUCKET = os.getenv('AWS_S3_BUCKET', '')

# CloudFront域名
CLOUDFRONT_DOMAIN = os.getenv('CLOUDFRONT_DOMAIN', '')


def upload_file_to_s3(file: UploadFile, folder: str = "uploads") -> Dict[str, Any]:
    """
    將文件上傳到S3
    """
    try:
        # 獲取文件擴展名
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        # 生成唯一的文件名
        timestamp = int(time.time())
        s3_filename = f"{folder}/{timestamp}_{file.filename}"
        
        # 將文件保存到臨時目錄
        with NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            file_content = file.file.read()
            temp_file.write(file_content)
            temp_file.flush()
            
            # 上傳到S3
            s3.upload_file(
                temp_file.name,
                S3_BUCKET,
                s3_filename,
                ExtraArgs={'ContentType': file.content_type}
            )
            
            # 刪除臨時文件
            os.unlink(temp_file.name)
        
        # 構建URL
        if CLOUDFRONT_DOMAIN:
            # 如果設置了CloudFront域名，使用CloudFront URL
            public_url = f"https://{CLOUDFRONT_DOMAIN}/{s3_filename}"
        else:
            # 否則使用S3 URL
            public_url = f"https://{S3_BUCKET}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{s3_filename}"
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "s3_path": s3_filename,
            "public_url": public_url
        }
    
    except Exception as e:
        print(f"上傳文件錯誤: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise e


def upload_avatar_to_s3(file: UploadFile) -> Dict[str, Any]:
    """上傳使用者頭像到S3"""
    # 檢查文件類型
    if not file.content_type.startswith('image/'):
        raise ValueError(f"不支持的文件類型: {file.content_type}，僅支持圖片文件")
    
    return upload_file_to_s3(file, "avatars")


def upload_blog_cover_to_s3(file: UploadFile) -> Dict[str, Any]:
    """上傳部落格封面圖片到S3"""
    # 檢查文件類型
    if not file.content_type.startswith('image/'):
        raise ValueError(f"不支持的文件類型: {file.content_type}，僅支持圖片文件")
    
    return upload_file_to_s3(file, "blog-covers")