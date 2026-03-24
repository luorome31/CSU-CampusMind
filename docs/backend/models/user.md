# 用户模型

## 表结构

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,           -- 用户ID (CAS用户名/学号)
    username TEXT UNIQUE NOT NULL, -- 用户名
    display_name TEXT,             -- 显示名称
    avatar_url TEXT,               -- 头像URL
    email TEXT,                    -- 邮箱
    phone TEXT,                   -- 电话
    is_active BOOLEAN DEFAULT TRUE,-- 账户状态
    created_at DATETIME,           -- 创建时间
    updated_at DATETIME           -- 更新时间
);
```

## 字段说明

| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | string | PK | 用户 ID，等于 CAS 用户名（学号） |
| username | string | Unique, Index | 用户名 |
| display_name | string | 可选 | 显示名称 |
| avatar_url | string | 可选 | 头像 URL |
| email | string | 可选 | 邮箱地址 |
| phone | string | 可选 | 电话号码 |
| is_active | bool | 默认 True | 账户是否激活 |
| created_at | datetime | 自动 | 创建时间 |
| updated_at | datetime | 自动 | 更新时间 |

## Python 模型

```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True, description="User ID (CAS username/student ID)")
    username: str = Field(unique=True, index=True, description="Unique username")
    display_name: Optional[str] = Field(default=None, description="Display name")
    avatar_url: Optional[str] = Field(default=None, description="Avatar URL")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    is_active: bool = Field(default=True, description="Account status")
    created_at: datetime = Field(default_factory=datetime.now, description="Created time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Updated time")
```

## 序列化

```python
def to_dict(self) -> Dict[str, Any]:
    return {
        "id": self.id,
        "username": self.username,
        "display_name": self.display_name,
        "avatar_url": self.avatar_url,
        "email": self.email,
        "phone": self.phone,
        "is_active": self.is_active,
        "created_at": self.created_at.isoformat() if self.created_at else None,
        "updated_at": self.updated_at.isoformat() if self.updated_at else None,
    }
```

## 特性说明

- **ID 即用户名**: 用户 ID 直接使用 CAS 用户名（学号），无需额外映射
- **自动创建**: 用户首次登录时自动创建，无需手动注册
- **UPSERT 语义**: 并发登录时使用 `INSERT ... ON CONFLICT DO NOTHING` 避免冲突
