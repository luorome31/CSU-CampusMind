# 知识库模型

## 知识库表 (KnowledgeBase)

### 表结构

```sql
CREATE TABLE knowledge (
    id TEXT PRIMARY KEY,           -- 知识库ID (前缀 t_)
    name TEXT UNIQUE NOT NULL,     -- 知识库名称
    description TEXT,             -- 描述
    user_id TEXT NOT NULL,        -- 创建者用户ID
    create_time DATETIME,         -- 创建时间
    update_time DATETIME          -- 更新时间
);
```

### 字段说明

| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | string | PK | 知识库 ID，前缀 `t_` |
| name | string | Unique, Index | 知识库名称 |
| description | string | 可选 | 知识库描述 |
| user_id | string | Index | 创建者用户 ID |
| create_time | datetime | 自动 | 创建时间 |
| update_time | datetime | 自动 | 更新时间 |

### Python 模型

```python
class KnowledgeBase(SQLModel, table=True):
    __tablename__ = "knowledge"

    id: str = Field(default=None, primary_key=True, description="Knowledge base ID (prefix: t_)")
    name: str = Field(default=None, unique=True, index=True, description="Knowledge base name")
    description: Optional[str] = Field(default="", description="Knowledge base description")
    user_id: str = Field(index=True, description="Creator user ID")
    create_time: datetime = Field(default_factory=datetime.now, description="Create time")
    update_time: datetime = Field(default_factory=datetime.now, description="Update time")
```

---

## 知识文件表 (KnowledgeFile)

### 表结构

```sql
CREATE TABLE knowledge_file (
    id TEXT PRIMARY KEY,           -- 文件ID
    file_name TEXT NOT NULL,      -- 文件名
    knowledge_id TEXT NOT NULL,    -- 所属知识库ID
    user_id TEXT,                 -- 上传用户ID
    status TEXT,                  -- 处理状态: process/success/fail
    oss_url TEXT,                 -- OSS存储URL
    file_size INTEGER,            -- 文件大小(字节)
    create_time DATETIME,         -- 创建时间
    update_time DATETIME          -- 更新时间
);
```

### 字段说明

| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | string | PK | 文件 ID |
| file_name | string | 必填 | 文件名 |
| knowledge_id | string | 必填 | 所属知识库 ID |
| user_id | string | 可选 | 上传用户 ID，默认为 "system" |
| status | string | 可选 | 处理状态：`process`/`success`/`fail`/`pending_verify`/`verified`/`indexing`/`indexed` |
| oss_url | string | 可选 | OSS/MinIO 存储 URL |
| file_size | int | 可选 | 文件大小（字节） |
| create_time | datetime | 自动 | 创建时间 |
| update_time | datetime | 自动 | 更新时间 |

### 状态流转

```
[后台爬取完成] --> pending_verify (待人工校验)
                    └--> fail (爬取失败)

[人工校验提交] --> verified (已校验)
                    │
[触发构建索引] --> indexing (索引中)
                    └--> indexed / success (索引完成)
                    └--> fail (索引失败)

* 注：普通上传可能直接进入 process -> success，批量导入和爬取触发 verify 流程。
```

### Python 模型

```python
class KnowledgeFile(SQLModel, table=True):
    __tablename__ = "knowledge_file"

    id: str = Field(primary_key=True, description="File ID")
    file_name: str = Field(description="File name")
    knowledge_id: str = Field(description="Knowledge base ID")
    user_id: str = Field(default="system", description="User ID")
    status: str = Field(default="process", description="Status: process/success/fail")
    oss_url: str = Field(description="OSS URL")
    file_size: int = Field(default=0, description="File size in bytes")
    create_time: Optional[datetime] = Field(default_factory=datetime.now)
    update_time: Optional[datetime] = Field(default_factory=datetime.now)
```

## 关系

```
User (1) ──────< (N) KnowledgeBase
KnowledgeBase (1) ──────< (N) KnowledgeFile
```
