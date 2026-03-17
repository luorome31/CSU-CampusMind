# 图书馆搜索工具 - 设计文档

**日期**: 2026-03-17
**状态**: Pending Approval

## 1. 概述

将中南大学图书馆检索接口封装为 Agent 可调用的工具，使用户在与 Agent 交互时可以搜索图书馆馆藏。

## 2. 工具设计

### 2.1 工具一: 图书馆搜索 (library_search)

根据关键词搜索图书馆馆藏图书。

**输入参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| keywords | str | 搜索关键词，建议 3 字以内的领域关键词 |

**输出**: 图书列表，每本书包含 `record_id`（用于查询复本位置）

### 2.2 工具二: 图书位置查询 (library_get_book_location)

根据 record_id 查询图书的复本位置信息。

**输入参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| record_id | int | 搜索结果中的 recordId |

**输出**: 该书的复本位置列表（馆藏地点、可借状态、架位号等）

### 2.3 recordId 传递机制

Agent 维护对话上下文，典型流程：
1. 用户搜索 "Vue" → Agent 调用 `library_search` → 返回包含 `record_id` 的结果列表
2. 用户问 "第三本书在哪里" → Agent 提取第三项的 `record_id` → 调用 `library_get_book_location(record_id=xxx)`

## 3. 文件结构

```
backend/app/core/tools/
├── __init__.py              # 导出 tools（更新）
├── library/                 # 新建目录
│   ├── __init__.py
│   ├── service.py           # 封装图书馆 API 调用
│   └── tools.py             # LangChain Tools 定义
```

## 4. 响应字段映射

### 4.1 搜索结果 (LibraryBookSearchResult)

| API 字段 | TS 字段 | 说明 |
|----------|---------|------|
| `recordId` | `RecordId` | 用于查询位置 |
| `title` | `Title` | 书名 |
| `author` | `Author` | 作者 |
| `publisher` | `Publisher` | 出版社 |
| `isbns` | `ISBNs` | ISBN 数组 |
| `publishYear` | `PublishYear` | 出版年 |
| `callNo` | `CallNo` | 索书号数组 |
| `docName` | `DocName` | 文献类型 |
| `physicalCount` | `PhysicalCount` | 馆藏册数 |
| `onShelfCountI` | `OnShelfCount` | 在架册数 |
| `langCode` | `Language` | 语言 |
| `subjectWord` | `Subjects` | 主题词 |
| `adstract` | `Abstract` | 摘要 |

### 4.2 复本位置 (LibraryBookItemCopiesResult)

| API 字段 | TS 字段 | 说明 |
|----------|---------|------|
| `itemId` | `ItemId` | 复本ID |
| `callNo` | `CallNo` | 索书号 |
| `barcode` | `Barcode` | 条码号 |
| `libName` | `LibName` | 馆名称 |
| `locationName` | `LocationName` | 位置名称 |
| `curLocationName` | `CurLocationName` | 当前所在位置 |
| `processType` | `ProcessType` | 借阅状态（在架/借出）|
| `shelfNo` | `ShelfNo` | 架位号 |

## 5. API 接口信息

### 5.1 搜索 API

- **URL**: `https://opac.lib.csu.edu.cn/find/unify/advancedSearch`
- **Method**: POST
- **Content-Type**: application/json

### 5.2 复本位置 API

- **URL**: `https://opac.lib.csu.edu.cn/find/physical/groupitems`
- **Method**: POST
- **Content-Type**: application/json

## 6. 依赖管理

- **项目依赖管理**: uv
- **运行代码**: 使用 `uv run`（如 `uv run python ...`）
- **依赖**: requests（已安装）

## 7. 实现步骤

1. 创建 `backend/app/core/tools/library/` 目录
2. 在 `service.py` 中封装 API 调用逻辑
3. 在 `tools.py` 中定义 LangChain Tools
4. 更新 `backend/app/core/tools/__init__.py` 导出新工具
