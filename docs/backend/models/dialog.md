# 对话模型

## 对话表 (Dialog)

存储对话会话元数据。

### 表结构

```sql
CREATE TABLE dialog (
    id TEXT PRIMARY KEY,           -- 对话ID (UUID)
    user_id TEXT,                  -- 用户ID (NULL表示匿名)
    agent_id TEXT,                 -- Agent模板ID
    updated_at DATETIME            -- 最后更新时间
);
```

### 字段说明

| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | string | PK | 对话 ID，使用 UUID |
| user_id | string | Index, 可选 | 用户 ID，匿名对话为 NULL |
| agent_id | string | Index, 可选 | 使用的 Agent 模板 ID |
| updated_at | datetime | 自动 | 最后更新时间 |

### Python 模型

```python
class Dialog(SQLModel, table=True):
    __tablename__ = "dialog"

    id: str = Field(default=None, primary_key=True, description="Dialog ID (UUID)")
    user_id: Optional[str] = Field(default=None, index=True, description="User ID (NULL for anonymous)")
    agent_id: Optional[str] = Field(default=None, index=True, description="Agent template ID")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
```

---

## 聊天历史表 (ChatHistory)

存储对话中的每条消息。

### 表结构

```sql
CREATE TABLE chat_history (
    id TEXT PRIMARY KEY,           -- 消息ID
    dialog_id TEXT NOT NULL,       -- 所属对话ID
    role TEXT NOT NULL,            -- 角色: user/assistant
    content TEXT NOT NULL,          -- 消息内容
    events TEXT,                    -- 工具调用事件JSON
    extra TEXT,                     -- 额外信息JSON
    created_at DATETIME             -- 创建时间
);
```

### 字段说明

| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | string | PK | 消息 ID，格式 `{timestamp}_user` 或 `{timestamp}_assistant` |
| dialog_id | string | 必填 | 所属对话 ID |
| role | string | 必填 | 角色：`user` 或 `assistant` |
| content | string | 必填 | 消息内容 |
| events | json | 可选 | 工具调用事件记录 |
| extra | json | 可选 | 额外信息（如模型名、耗时等） |
| created_at | datetime | 自动 | 创建时间 |

### 事件记录格式 (events)

```json
[
  {
    "type": "tool_call",
    "timestamp": 1234567890,
    "tool": "jwc_grade",
    "args": {"term": "2024-2025-1"},
    "result": "成绩查询结果..."
  }
]
```

### 额外信息格式 (extra)

```json
{
  "model": "gpt-3.5-turbo",
  "duration": 2.5,
  "knowledge_ids": ["t_abc123"],
  "sources": [...]
}
```

---

## 关系

```
User (1) ──────< (N) Dialog
Dialog (1) ──────< (N) ChatHistory
```

---

## 缓存策略

聊天历史同时存储在 Redis 缓存中以提高读取性能：

- **Key 格式**: `history:{dialog_id}`
- **TTL**: 1 小时
- **一致性**: 采用双写策略（DB + Cache 并行写入）
- **缓存未命中**: 从 DB 回填缓存
