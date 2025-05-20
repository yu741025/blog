# 部落格後端系統

這是一個基於FastAPI和MySQL構建的完整部落格後端系統，支持用戶管理、文章發布、評論互動、標籤分類等功能，並集成了S3/CloudFront進行圖片存儲。

## 目錄

- [功能概覽](#功能概覽)
- [系統架構](#系統架構)
- [安裝與設置](#安裝與設置)
- [功能詳解與使用方法](#功能詳解與使用方法)
  - [用戶管理](#用戶管理)
  - [部落格文章管理](#部落格文章管理)
  - [評論系統](#評論系統)
  - [標籤和分類](#標籤和分類)
  - [圖片上傳](#圖片上傳)
- [API文檔](#api文檔)
- [資料庫模型](#資料庫模型)
- [開發指南](#開發指南)
- [部署指南](#部署指南)
- [問題排解](#問題排解)

## 功能概覽

本系統提供以下核心功能：

1. **用戶管理**
   - 用戶註冊與登入
   - JWT身份驗證
   - 個人資料管理
   - 頭像上傳

2. **部落格文章管理**
   - 創建、編輯、刪除、查看文章
   - 草稿模式
   - 封面圖片上傳
   - 文章搜索與分頁

3. **評論系統**
   - 發表評論
   - 回覆評論
   - 刪除評論

4. **標籤和分類**
   - 創建標籤
   - 管理文章分類
   - 按標籤/分類篩選文章

5. **圖片上傳**
   - S3/CloudFront集成
   - 頭像上傳
   - 文章封面上傳

## 系統架構

- **後端框架**: FastAPI
- **資料庫**: MySQL
- **ORM**: SQLAlchemy
- **認證**: JWT (JSON Web Tokens)
- **文件存儲**: AWS S3 + CloudFront
- **容器化**: Docker & Docker Compose

## 安裝與設置

### 前置需求

- Docker和Docker Compose
- 可選: AWS帳戶(用於S3和CloudFront)

### 安裝步驟

1. Clone或下載本專案

2. 創建環境配置文件:
   ```bash
   cp .env.example .env
   ```

3. 編輯`.env`文件，設置必要的環境變量:
   ```
   # 資料庫設置
   DB_HOST=
   DB_USER=
   DB_PASS=
   DB_PORT=
   DB_NAME=

   # 文件上傳設置
   # 選項1: AWS S3 (雲端儲存)
   AWS_ACCESS_KEY_ID=你的AWS存取金鑰
   AWS_SECRET_ACCESS_KEY=你的AWS秘密金鑰
   AWS_REGION=ap-southeast-1
   AWS_S3_BUCKET=你的S3存儲桶名稱
   CLOUDFRONT_DOMAIN=你的CloudFront域名

   # 選項2: 本地存儲 (開發模式)
   USE_LOCAL_STORAGE=true
   LOCAL_STORAGE_PATH=./uploads
   ```

4. 啟動服務:
   ```bash
   docker-compose up -d
   ```

5. 初始化資料庫:
   訪問 `http://localhost:8000/renewDB`

6. 訪問API文檔:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 功能詳解與使用方法

### 用戶管理

#### 用戶註冊

**API路徑**: `POST /public/auth/register`

**請求格式**:
```json
{
  "name": "用戶名稱",
  "username": "登入用戶名",
  "password": "密碼"
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/public/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "王小明", "username": "xiaoming", "password": "secure_password"}'
```

#### 用戶登入

**API路徑**: `POST /public/auth/login`

**請求格式**:
```
username=登入用戶名&password=密碼
```

**示例**:
```bash
curl -X POST "http://localhost:8000/public/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=xiaoming&password=secure_password"
```

**返回格式**:
```json
{
  "access_token": "JWT令牌",
  "token_type": "bearer"
}
```

#### 獲取當前用戶資訊

**API路徑**: `GET /private/auth/me`

**請求頭**: 需要包含 `Authorization: Bearer JWT令牌`

**示例**:
```bash
curl -X GET "http://localhost:8000/private/auth/me" \
  -H "Authorization: Bearer 你的JWT令牌"
```

#### 更新用戶資料

**API路徑**: `PUT /private/users/me`

**請求格式**:
```json
{
  "name": "新的名稱",
  "bio": "個人簡介"
}
```

**示例**:
```bash
curl -X PUT "http://localhost:8000/private/users/me" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 你的JWT令牌" \
  -d '{"name": "新名字", "bio": "這是我的個人簡介"}'
```

#### 上傳頭像

**API路徑**: `POST /private/users/me/avatar`

**請求格式**: 表單資料，包含一個名為 `file` 的文件字段

**示例**:
```bash
curl -X POST "http://localhost:8000/private/users/me/avatar" \
  -H "Authorization: Bearer 你的JWT令牌" \
  -F "file=@/路徑/到/你的頭像.jpg"
```

### 部落格文章管理

#### 獲取所有文章

**API路徑**: `GET /public/blogs`

**查詢參數**:
- `skip`: 跳過前幾篇文章(用於分頁)
- `limit`: 返回最多幾篇文章
- `tag_id`: 按標籤過濾
- `category_id`: 按分類過濾
- `search`: 搜索關鍵詞

**示例**:
```bash
curl -X GET "http://localhost:8000/public/blogs?skip=0&limit=10"
```

#### 獲取我的全部文章

**API路徑**: `GET /private/blogs/me`

**請求頭**: 需要包含 `Authorization: Bearer JWT令牌`

**查詢參數**: 與 `GET /public/blogs` 相同，但會返回包括草稿在內的所有文章

**示例**:
```bash
curl -X GET "http://localhost:8000/private/blogs/me" \
  -H "Authorization: Bearer 你的JWT令牌"
```

#### 獲取單篇文章

**API路徑**: `GET /public/blogs/{blog_id}`

**示例**:
```bash
curl -X GET "http://localhost:8000/public/blogs/01JVM21FC7XGAZG26NVM5JWEJN"
```

#### 創建文章

**API路徑**: `POST /private/blogs`

**請求格式**:
```json
{
  "title": "文章標題",
  "content": "文章內容（支持Markdown）",
  "summary": "文章摘要",
  "cover_image_url": "封面圖片URL（可選）",
  "is_draft": false,
  "tag_ids": ["標籤ID1", "標籤ID2"],
  "category_ids": ["分類ID1", "分類ID2"]
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/private/blogs" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 你的JWT令牌" \
  -d '{
    "title": "我的第一篇文章",
    "content": "# 這是我的第一篇文章\n\n這裡是正文內容。",
    "summary": "這是一篇關於..的文章",
    "is_draft": false,
    "tag_ids": [],
    "category_ids": []
  }'
```

#### 更新文章

**API路徑**: `PUT /private/blogs/{blog_id}`

**請求格式**:
```json
{
  "title": "新標題",
  "content": "新內容",
  "summary": "新摘要",
  "cover_image_url": "新封面圖片URL",
  "is_draft": false,
  "tag_ids": ["標籤ID1", "標籤ID2"],
  "category_ids": ["分類ID1", "分類ID2"]
}
```

**示例**:
```bash
curl -X PUT "http://localhost:8000/private/blogs/01JVM21FC7XGAZG26NVM5JWEJN" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 你的JWT令牌" \
  -d '{
    "title": "更新後的標題",
    "content": "更新後的內容",
    "is_draft": false
  }'
```

#### 刪除文章

**API路徑**: `DELETE /private/blogs/{blog_id}`

**示例**:
```bash
curl -X DELETE "http://localhost:8000/private/blogs/01JVM21FC7XGAZG26NVM5JWEJN" \
  -H "Authorization: Bearer 你的JWT令牌"
```

#### 上傳文章封面圖片

**API路徑**: `POST /private/blogs/upload-cover`

**請求格式**: 表單資料，包含一個名為 `file` 的文件字段

**示例**:
```bash
curl -X POST "http://localhost:8000/private/blogs/upload-cover" \
  -H "Authorization: Bearer 你的JWT令牌" \
  -F "file=@/路徑/到/封面圖片.jpg"
```

#### 點讚文章

**API路徑**: `POST /private/blogs/{blog_id}/like`

**示例**:
```bash
curl -X POST "http://localhost:8000/private/blogs/01JVM21FC7XGAZG26NVM5JWEJN/like" \
  -H "Authorization: Bearer 你的JWT令牌"
```

### 評論系統

#### 創建評論

**API路徑**: `POST /private/comments`

**請求格式**:
```json
{
  "content": "評論內容",
  "blog_id": "文章ID",
  "parent_id": "父評論ID（可選，用於回覆）"
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/private/comments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 你的JWT令牌" \
  -d '{
    "content": "這是一條評論",
    "blog_id": "01JVM21FC7XGAZG26NVM5JWEJN",
    "parent_id": null
  }'
```

#### 獲取文章評論

**API路徑**: `GET /private/comments/blog/{blog_id}`

**示例**:
```bash
curl -X GET "http://localhost:8000/private/comments/blog/01JVM21FC7XGAZG26NVM5JWEJN" \
  -H "Authorization: Bearer 你的JWT令牌"
```

#### 刪除評論

**API路徑**: `DELETE /private/comments/{comment_id}`

**示例**:
```bash
curl -X DELETE "http://localhost:8000/private/comments/01JVP7NT9XWTE5NZKA1SK8GVH7" \
  -H "Authorization: Bearer 你的JWT令牌"
```

### 標籤和分類

#### 獲取所有標籤

**API路徑**: `GET /public/tags`

**示例**:
```bash
curl -X GET "http://localhost:8000/public/tags"
```

#### 創建標籤

**API路徑**: `POST /private/tags`

**請求格式**:
```json
{
  "name": "標籤名稱"
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/private/tags" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 你的JWT令牌" \
  -d '{"name": "技術"}'
```

#### 獲取所有分類

**API路徑**: `GET /public/categories`

**示例**:
```bash
curl -X GET "http://localhost:8000/public/categories"
```

#### 創建分類(僅管理員)

**API路徑**: `POST /root/categories`

**請求格式**:
```json
{
  "name": "分類名稱",
  "description": "分類描述"
}
```

**示例**:
```bash
curl -X POST "http://localhost:8000/root/categories" \
  -H "Content-Type: application/json" \
  -H "X-ADMIN-TOKEN: admin" \
  -d '{
    "name": "技術文章",
    "description": "關於技術的文章"
  }'
```

### 圖片上傳

系統支持兩種圖片上傳方式：

1. **AWS S3 + CloudFront**（生產環境）：圖片存儲在S3，通過CloudFront加速訪問
2. **本地存儲**（開發環境）：圖片存儲在服務器本地

#### 配置選項

在`.env`文件中設置:

**選項1: AWS S3 + CloudFront**
```
AWS_ACCESS_KEY_ID=你的AWS存取金鑰
AWS_SECRET_ACCESS_KEY=你的AWS秘密金鑰
AWS_REGION=ap-southeast-1
AWS_S3_BUCKET=你的S3存儲桶名稱
CLOUDFRONT_DOMAIN=你的CloudFront域名
USE_LOCAL_STORAGE=false
```

**選項2: 本地存儲**
```
USE_LOCAL_STORAGE=true
LOCAL_STORAGE_PATH=./uploads
```

## API文檔

系統提供了三種API文檔格式:

1. **Swagger UI**: `http://localhost:8000/docs`
   - 交互式文檔
   - 可直接測試API
   - 包含詳細的參數說明

2. **ReDoc**: `http://localhost:8000/redoc`
   - 更加整潔的閱讀體驗
   - 不支持直接測試API

3. **Stoplight Elements**: `http://localhost:8000/elements`
   - 現代化的UI
   - 更好的導航體驗

## 資料庫模型

系統使用以下主要資料模型:

1. **User**: 用戶模型
   - `id`: 用戶唯一識別碼
   - `name`: 用戶名稱
   - `bio`: 用戶簡介
   - `avatar_url`: 用戶頭像URL
   - `created_at`: 註冊時間
   - `updated_at`: 資料更新時間

2. **UserAccount**: 用戶帳號模型
   - `id`: 帳號唯一識別碼
   - `username`: 登入用戶名
   - `password`: 密碼（雜湊存儲）
   - `user_id`: 關聯用戶ID

3. **Blog**: 部落格文章模型
   - `id`: 文章唯一識別碼
   - `title`: 文章標題
   - `content`: 文章內容
   - `summary`: 文章摘要
   - `cover_image_url`: 封面圖片URL
   - `is_draft`: 是否為草稿
   - `view_count`: 瀏覽次數
   - `like_count`: 喜歡次數
   - `author_id`: 作者ID
   - `created_at`: 創建時間
   - `updated_at`: 更新時間

4. **Comment**: 評論模型
   - `id`: 評論唯一識別碼
   - `content`: 評論內容
   - `blog_id`: 文章ID
   - `user_id`: 用戶ID
   - `parent_id`: 父評論ID
   - `created_at`: 創建時間
   - `updated_at`: 更新時間

5. **Tag**: 標籤模型
   - `id`: 標籤唯一識別碼
   - `name`: 標籤名稱

6. **Category**: 分類模型
   - `id`: 分類唯一識別碼
   - `name`: 分類名稱
   - `description`: 分類描述

## 開發指南

### 項目結構

```
└── src/
    ├── crud/           # 資料庫操作函數
    ├── database/       # 資料庫連接和模型
    ├── dependencies/   # 依賴項（認證等）
    ├── routers/        # API路由
    │   ├── db/         # 資料庫管理路由
    │   ├── private/    # 需要認證的API
    │   ├── public/     # 公開API
    │   └── root/       # 管理員API
    ├── schemas/        # 請求/響應模型
    ├── utils/          # 工具函數
    └── server.py       # 主服務器入口
```

### 添加新功能

1. **新增資料模型**:
   - 在 `src/database/models.py` 中添加新的模型類

2. **實現CRUD操作**:
   - 在 `src/crud/` 目錄下創建新文件
   - 實現創建、讀取、更新、刪除等操作

3. **定義Schema**:
   - 在 `src/schemas/` 目錄下定義請求/響應模型

4. **添加API路由**:
   - 在 `src/routers/` 下的適當目錄中添加路由

### 運行測試

```bash
docker-compose exec backend pytest
```

## 部署指南

### 使用Docker Compose部署

1. 修改 `.env` 文件，設置生產環境配置
2. 運行 `docker-compose up -d`
3. 初始化資料庫 `http://your-domain/renewDB`

### 使用Nginx作為反向代理

參考 `NGINX.md` 文件設置Nginx反向代理，啟用HTTPS。

## 問題排解

### 常見問題

1. **無法連接資料庫**
   - 檢查 `.env` 文件中的資料庫配置
   - 確保MySQL容器已啟動

2. **圖片上傳失敗**
   - 如使用S3，檢查AWS憑證
   - 如使用本地存儲，確保路徑存在且可寫

3. **JWT認證失敗**
   - 檢查令牌是否過期（默認30分鐘）
   - 確保使用正確的格式：`Authorization: Bearer 你的令牌`

### 查看日誌

```bash
# 查看所有容器日誌
docker-compose logs

# 只查看後端日誌
docker-compose logs backend

# 實時跟蹤日誌
docker-compose logs -f backend
```

### 重置系統

如需完全重置系統：

```bash
# 停止所有容器
docker-compose down

# 刪除資料卷
docker volume rm fastapi-template_mysql_data

# 重新啟動
docker-compose up -d

# 初始化資料庫
訪問 http://localhost:8000/renewDB
```
