# LLM 对话接口

支持流式 SSE 输出的智能对话接口，集成 RAG 检索能力。

## 流式对话

SSE 流式响应，包含工具调用事件和 LLM 输出块。

### 请求

```
POST /api/v1/completion/stream
```

```json
{
  "message": "帮我查询一下我的成绩",
  "knowledge_ids": ["t_abc123"],
  "agent_id": null,
  "dialog_id": "dialog_001",
  "enable_rag": true,
  "top_k": 5,
  "min_score": 0.0,
  "model": "gpt-3.5-turbo"
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| message | string | 是 | 用户消息 |
| knowledge_ids | array[string] | 否 | RAG 知识库 ID 列表 |
| agent_id | string | 否 | Agent 模板 ID |
| dialog_id | string | 否 | 对话 ID，不提供则自动生成 |
| enable_rag | bool | 否 | 启用 RAG，默认 true |
| top_k | int | 否 | RAG 检索数量，默认 5 |
| min_score | float | 否 | RAG 最低分数，默认 0.0 |
| model | string | 否 | LLM 模型名称 |

### SSE 事件流

**工具执行开始事件:**
```
data: {"type": "event", "timestamp": 1234567890, "data": {"status": "START", "title": "成绩查询", "message": "正在查询教务系统..."}}
```

**工具执行结束事件:**
```
data: {"type": "event", "timestamp": 1234567890, "data": {"status": "END", "title": "成绩查询", "message": "查询完成"}}
```

**LLM 文本块事件:**
```
data: {"type": "response_chunk", "timestamp": 1234567890, "data": {"chunk": "你的成绩是", "accumulated": "你的成绩是"}}
```

**新对话创建事件:**
```
data: {"type": "new_dialog", "newDialogId": "dialog_001"}
```

**对话标题更新事件** (首轮对话完成后 AI 精化标题):
```
data: {"type": "title_update", "data": {"title": "成绩查询"}}
```

**错误事件:**
```
data: {"type": "event", "timestamp": 1234567890, "data": {"status": "ERROR", "title": "错误", "message": "处理请求时发生错误"}}
```

### 响应头

```
X-Dialog-ID: dialog_001
```

---

## 非流式对话

标准 JSON 响应，适合需要完整回复的场景。

### 请求

```
POST /api/v1/completion
```

### 请求体

与流式接口相同。

### 响应

```json
{
  "success": true,
  "message": "帮我查询一下我的成绩",
  "context": "检索到的上下文...",
  "sources": [
    {"chunk_id": "chunk_001", "content": "...", "score": 0.95}
  ],
  "dialog_id": "dialog_001"
}
```

---

## 对话流程

```
┌─────────┐     ┌─────────────┐     ┌─────────────┐
│  用户   │────▶│   RAG       │────▶│ ReactAgent  │
│  消息   │     │   检索     │     │   工具调用  │
└─────────┘     └─────────────┘     └─────────────┘
                                          │
                                          ▼
                                   ┌─────────────┐
                                   │   LLM       │
                                   │  生成响应   │
                                   └─────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
             ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
             │   SSE       │       │   历史      │       │   事件      │
             │  流式输出   │       │   存储      │       │   记录      │
             └─────────────┘       └─────────────┘       └─────────────┘
```

---

## 对话历史

对话历史通过 `dialog_id` 关联，自动保存到数据库和 Redis 缓存。

### ChatHistory 数据结构

| 字段 | 类型 | 描述 |
|------|------|------|
| id | string | 消息 ID |
| dialog_id | string | 对话 ID |
| role | string | 角色 (user/assistant) |
| content | string | 消息内容 |
| events | json | 工具调用事件记录 |
| extra | json | 额外信息（模型、耗时等） |
| created_at | datetime | 创建时间 |

### Dialog 数据结构

| 字段 | 类型 | 描述 |
|------|------|------|
| id | string | 对话 ID (UUID) |
| user_id | string | 用户 ID（未登录为 null） |
| agent_id | string | Agent 模板 ID |
| title | string | 对话标题（自动生成或手动设置） |
| updated_at | datetime | 最后更新时间 |

### 标题生成策略

1. **立即标题**：新对话创建时，使用用户消息前 25 字符作为临时标题
2. **AI 精化**：第二轮对话时，若标题以 `...` 结尾或长度 ≥ 20，则调用 LLM 精化为 4-8 字标题
3. **实时推送**：精化完成后通过 SSE `title_update` 事件推送给前端
