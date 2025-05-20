import os
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import List, Dict, Any

import boto3
from botocore.config import Config
from fastapi import UploadFile

from src.schemas.basic import UploadedFile

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION'),
    config=Config(s3={"use_accelerate_endpoint": False})
)


def upload_file_to_s3(
        file: UploadFile,
        folder: str = "uploads",
        allowed_types: List[str] = None
) -> Dict[str, Any]:
    """
    上傳文件到S3
    folder: 存儲在S3的文件夾路徑
    allowed_types: 允許的文件類型列表，例如 ['image/jpeg', 'image/png']
    """
    if allowed_types and file.content_type not in allowed_types:
        raise ValueError(f"不支持的文件類型: {file.content_type}。允許的類型: {allowed_types}")
    
    # 獲取文件擴展名
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    # 生成唯一的文件名
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_suffix = os.urandom(4).hex()
    s3_filename = f"{folder}/{timestamp}-{random_suffix}{file_extension}"
    
    # 將文件保存到臨時目錄
    with NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        file_content = file.file.read()
        temp_file.write(file_content)
        temp_file.flush()
        
        # 上傳到S3
        s3.upload_file(
            temp_file.name,
            str(os.getenv('AWS_S3_BUCKET')),
            s3_filename,
            ExtraArgs={'ContentType': file.content_type}
        )
        
        # 刪除臨時文件
        os.unlink(temp_file.name)
    
    # 構建公共URL
    public_url = f"https://{os.getenv('AWS_S3_BUCKET')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{s3_filename}"
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "s3_path": s3_filename,
        "public_url": public_url
    }


def upload_image_to_s3(file: UploadFile, folder: str = "images") -> Dict[str, Any]:
    """上傳圖片到S3，限制只能上傳圖片類型的文件"""
    allowed_image_types = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/svg+xml'
    ]
    
    return upload_file_to_s3(file, folder, allowed_image_types)


def upload_avatar_to_s3(file: UploadFile) -> Dict[str, Any]:
    """上傳使用者頭像到S3"""
    return upload_image_to_s3(file, "avatars")


def upload_blog_cover_to_s3(file: UploadFile) -> Dict[str, Any]:
    """上傳部落格封面圖片到S3"""
    return upload_image_to_s3(file, "blog-covers")


def save_upload_files_locally(files: List[UploadFile] | UploadFile) -> List[UploadedFile]:
    """保存上傳的文件到本地臨時目錄（在開發環境中使用）"""
    entries = []

    if not isinstance(files, list):
        files = [files]

    for file in files:
        file_extension = file.filename.split(".")[-1]

        with NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            file_content = file.file.read()
            temp_file.write(file_content)
            temp_file.flush()

        entries.append(
            UploadedFile(
                path=temp_file.name,
                original_file_name=file.filename,
                extension=file_extension,
                content_type=file.content_type
            )
        )

    return entries
