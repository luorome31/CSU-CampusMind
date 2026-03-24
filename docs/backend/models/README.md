# 数据模型

CampusMind 使用 SQLModel (SQLAlchemy + Pydantic) 作为 ORM。

## 概览

```
┌─────────────┐
│    User     │  用户表
├─────────────┤
│  Knowledge  │  知识库表
├─────────────┤
│KnowledgeFile│  知识文件表
├─────────────┤
│   Dialog    │  对话表
├─────────────┤
│ ChatHistory │  聊天历史表
├─────────────┤
│ ToolCallLog │  工具调用日志
├─────────────┤
│  CrawlTask  │  批量爬取任务记录
└─────────────┘
```

---

## 目录结构

- [用户模型](./user.md) - User 表
- [知识库模型](./knowledge.md) - Knowledge/KnowledgeFile/CrawlTask 表
- [对话模型](./dialog.md) - Dialog/ChatHistory 表
