# CAREER_TOOLS 集成设计文档

**日期**: 2026-03-19
**主题**: Career 就业信息工具与 LangGraph Agent 集成
**目标**: 将 Career 工具以工厂函数模式集成到 ReactAgent，使其像 Library 一样始终可用

---

## 1. 背景

Career 模块已完成，提供 4 个无需认证的就业信息查询工具：

| 工具名 | 功能 |
|--------|------|
| `career_teachin` | 宣讲会查询 |
| `career_campus_recruit` | 校园招聘查询 |
| `career_campus_intern` | 实习信息查询 |
| `career_jobfair` | 招聘会查询 |

当前 `CAREER_TOOLS` 是静态工具列表，需要改造为工厂函数模式以符合项目规范。

---

## 2. 设计决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 集成方式 | 工厂函数模式 | 与 JWC、Library 保持一致 |
| 接口一致性 | 接收 `ctx: ToolContext` 参数 | 与 Library 保持接口统一 |
| 可用性 | 始终可用，无需认证 | 与 Library 相同 |

---

## 3. 架构

```
AgentFactory.create_agent()
    │
    ├── create_library_tools(ctx)  →  Library 工具
    ├── create_career_tools(ctx)   →  Career 工具 [NEW]
    ├── create_rag_tool(...)      →  RAG 工具
    └── create_jwc_tools(ctx)     →  JWC 工具（仅认证用户）
```

Career 工具与其他公开工具（Library、RAG）并列，始终对所有用户可用。

---

## 4. 文件变更

### 4.1 backend/app/core/tools/career/tools.py

添加 `create_career_tools(ctx)` 工厂函数：

```python
def create_career_tools(ctx: ToolContext) -> List[BaseTool]:
    """
    创建 Career 工具（不需要登录）

    Career 工具是公开的，所有用户都可以使用
    """

    def _get_teachin(zone: str = "") -> str:
        """获取宣讲会信息"""
        try:
            service = CareerService()
            return service.get_teachin(zone)
        except Exception as e:
            logger.error(f"Career teachin query failed: {e}")
            return f"宣讲会查询失败: {str(e)}"

    def _get_campus_recruit(keyword: str = "") -> str:
        """获取校园招聘信息"""
        ...

    def _get_campus_intern(keyword: str = "") -> str:
        """获取实习信息"""
        ...

    def _get_jobfair() -> str:
        """获取招聘会信息"""
        ...

    return [
        StructuredTool.from_function(
            func=_get_teachin,
            name="career_teachin",
            description="获取中南大学就业信息网站的宣讲会信息..."
        ),
        StructuredTool.from_function(
            func=_get_campus_recruit,
            name="career_campus_recruit",
            ...
        ),
        ...
    ]
```

### 4.2 backend/app/core/tools/career/__init__.py

添加导出：

```python
from .tools import (
    ...
    create_career_tools,
)
```

### 4.3 backend/app/core/tools/__init__.py

添加导出：

```python
from app.core.tools.career import create_career_tools
```

### 4.4 backend/app/core/agents/factory.py

**修改 1**：导入 `create_career_tools`

```python
from app.core.tools.career import create_career_tools
```

**修改 2**：在 `create_agent()` 中添加 Career 工具

```python
# Career 工具（始终可用，无需认证）
tools.extend(create_career_tools(ctx))
```

**修改 3**：更新 `_build_system_prompt()` 添加 Career 工具说明

```python
base_prompt += """
- career_teachin: 查询宣讲会信息
- career_campus_recruit: 查询校园招聘信息
- career_campus_intern: 查询实习岗位信息
- career_jobfair: 查询招聘会信息"""
```

---

## 5. System Prompt 更新

### 游客模式（未登录）

```python
base_prompt += """
当前为游客模式，你可以使用以下公开工具：
- library_search: 搜索图书馆馆藏
- library_get_book_location: 查询图书位置
- rag_search: 搜索知识库
- career_teachin: 查询宣讲会信息
- career_campus_recruit: 查询校园招聘信息
- career_campus_intern: 查询实习岗位信息
- career_jobfair: 查询招聘会信息

如果需要访问个人成绩、课表等信息，请提示用户先登录。"""
```

---

## 6. 测试策略

### 6.1 单元测试

新增 `tests/core/tools/career/test_factory.py`：

- `test_create_career_tools_returns_four_tools`
- `test_create_career_tools_teachin_call`
- `test_create_career_tools_campus_recruit_call`
- `test_create_career_tools_campus_intern_call`
- `test_create_career_tools_jobfair_call`

### 6.2 集成测试

修改 `tests/core/agents/test_factory.py`：

- 添加 Career 工具到 Agent 的验证

---

## 7. 实现顺序

1. 在 `career/tools.py` 添加 `create_career_tools()` 工厂函数
2. 更新 `career/__init__.py` 导出
3. 更新 `core/tools/__init__.py` 导出
4. 修改 `AgentFactory` 集成 Career 工具
5. 更新 System Prompt
6. 添加单元测试
7. 运行测试验证

---

## 8. 参考文档

- [Career 模块开发指南](../../career-module-guide.md)
- [LangGraph 工具集成设计](../specs/2026-03-17-langgraph-tool-integration-design.md)
