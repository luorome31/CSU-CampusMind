# 就业指导中心 (Career) 模块开发指南

**创建日期**: 2026-03-19
**模块**: `app.core.tools.career`
**状态**: 已完成

---

## 1. 概述

`career` 模块提供中南大学就业信息网 (career.csu.edu.cn) 的公开数据查询功能，无需认证即可使用。

### 1.1 功能列表

| 工具名 | 功能 | API 端点 | 参数 |
|--------|------|----------|------|
| `career_teachin` | 宣讲会信息 | `/teachin` | `zone` (可选) |
| `career_campus_recruit` | 校园招聘 | `/campus/index/category/1` | `keyword` (可选) |
| `career_campus_intern` | 实习岗位 | `/campus/index/category/2` | `keyword` (可选) |
| `career_jobfair` | 大型招聘会 | `/jobfair` | 无 |

### 1.2 技术栈

- **HTTP**: `requests`
- **HTML 解析**: `beautifulsoup4`
- **工具框架**: `langchain_core.tools.StructuredTool`
- **数据验证**: `pydantic`

---

## 2. 项目结构

```
backend/app/core/tools/career/
├── __init__.py      # 模块导出
├── client.py        # HTTP 请求 + HTML 解析
├── service.py       # 业务逻辑 + Markdown 格式化
└── tools.py         # LangChain StructuredTool 定义

backend/tests/core/tools/career/
├── test_client.py       # HTML 解析测试
├── test_service.py       # 格式化测试
├── test_tools.py         # 工具定义测试
└── test_integration.py   # 集成测试（需网络）
```

### 2.1 层级职责

| 文件 | 职责 |
|------|------|
| `client.py` | 发起 HTTP 请求，使用 BeautifulSoup 解析 HTML，返回 dataclass 数据结构 |
| `service.py` | 调用 client，将数据格式化为 Markdown 表格，处理异常 |
| `tools.py` | 定义 LangChain StructuredTool，提供给 Agent 调用 |

---

## 3. 集成到 Agent

### 3.1 当前 Agent 工具配置

在 `app/core/agents/factory.py` 的 `AgentFactory.create_agent()` 中：

```python
# 图书馆工具（始终可用）
tools.extend(create_library_tools(ctx))

# RAG 工具（始终可用）
if knowledge_ids:
    for kid in knowledge_ids:
        tools.append(create_rag_tool(knowledge_ids=[kid]))

# JWC 工具（需要登录）
if ctx.is_authenticated:
    tools.extend(create_jwc_tools(ctx))
```

### 3.2 添加 Career 工具（建议）

Career 工具应像 Library/RAG 一样，**无需认证即可使用**。建议在 `factory.py` 中添加：

```python
# Career 工具（始终可用，无需认证）
from app.core.tools.career import CAREER_TOOLS
tools.extend(CAREER_TOOLS)
```

同时更新 `_build_system_prompt()` 中的游客模式提示：

```python
base_prompt += """

当前为游客模式，你可以使用以下公开工具：
- library_search: 搜索图书馆馆藏
- library_get_book_location: 查询图书位置
- rag_search: 搜索知识库
- career_teachin: 查询宣讲会信息
- career_campus_recruit: 查询校园招聘信息
- career_campus_intern: 查询实习岗位信息
- career_jobfair: 查询招聘会信息"""
```

---

## 4. 使用方式

### 4.1 直接使用

```python
from app.core.tools.career import CareerService

service = CareerService()

# 查询宣讲会
result = service.get_teachin(zone="岳麓山校区")

# 查询校园招聘
result = service.get_campus_recruit(keyword="软件")

# 查询实习
result = service.get_campus_intern(keyword="字节跳动")

# 查询招聘会
result = service.get_jobfair()
```

### 4.2 在 Agent 中使用

```python
from app.core.tools.career import CAREER_TOOLS

# 创建 Agent 时传入
agent = ReactAgent(
    model=llm,
    system_prompt="...",
    tools=CAREER_TOOLS  # 可与其他工具合并
)
```

---

## 5. 返回格式示例

### 5.1 宣讲会

```
## 宣讲会查询结果

| 名称 | 举办地点 | 举办时间 |
|------|----------|----------|
| 贝斯（无锡）信息系统有限公司 | 线上宣讲 | 2026-03-19 14:00-15:00(周四) |
| 中建三局基础设施建设投资有限公司 | 岳麓山校区 科教南楼507 | 2026-03-19 14:00-16:00(周四) |
```

### 5.2 招聘会

```
## 大型招聘会信息

| 招聘会名称 | 举办城市 | 举办地址 | 类型 | 举办时间 |
|------------|----------|----------|------|----------|
| 中南大学2026届春季第二场大型综合双选会... | 湖南省 - 长沙市 | 中南大学潇湘校区体育场副场 | 校园招聘会 | 2026-04-19 14:00-18:00(周日) |
```

---

## 6. 错误处理

| 场景 | 返回 |
|------|------|
| 网络超时/连接失败 | `{功能}查询失败，请稍后重试` |
| HTML 解析失败 | `{功能}查询失败，请稍后重试` |
| 无数据 | `{功能}查询结果为空` |

**原则**: 不暴露内部错误细节，保留日志记录。

---

## 7. 测试

### 7.1 运行单元测试

```bash
cd backend
uv run pytest tests/core/tools/career/test_client.py \
                       tests/core/tools/career/test_service.py \
                       tests/core/tools/career/test_tools.py -v
```

### 7.2 运行集成测试

```bash
uv run pytest tests/core/tools/career/test_integration.py -v -m integration
```

### 7.3 测试 HTML 解析

测试使用 `docs/development_doc/` 下的本地 HTML 示例文件：

- `宣讲会信息.txt` - 宣讲会 HTML
- `公司招聘信息.txt` - 校园招聘 HTML
- `公司实习信息.txt` - 实习信息 HTML
- `招聘会信息.txt` - 招聘会 HTML

---

## 8. 添加新工具指南

如需添加新的就业信息查询工具：

### 8.1 步骤

1. **确定接口**: 在 `client.py` 添加新方法，解析 HTML 返回对应 dataclass
2. **业务封装**: 在 `service.py` 添加格式化方法
3. **工具定义**: 在 `tools.py` 添加 `StructuredTool`
4. **导出**: 在 `__init__.py` 和 `app/core/tools/__init__.py` 中添加导出
5. **测试**: 添加单元测试和集成测试

### 8.2 命名规范

| 类别 | 命名规则 | 示例 |
|------|----------|------|
| 模块目录 | `career/` | `app/core/tools/career/` |
| 工具名 | `career_{功能}` | `career_teachin` |
| 类名 | `Career{功能}Tool` | `CareerTeachinTool` |
| 导出列表 | `CAREER_TOOLS` | 包含所有工具的列表 |

---

## 9. 与其他模块的关系

```
app/core/tools/
├── career/          # 就业信息（无需认证）
├── jwc/             # 教务系统（需要认证）
├── library/         # 图书馆（无需认证）
└── rag_tool.py      # 知识库（无需认证）
```

| 模块 | 认证需求 | SessionManager 依赖 |
|------|----------|-------------------|
| `career` | 无 | 否 |
| `jwc` | 是 | 是 |
| `library` | 无 | 否 |
| `rag_tool` | 无 | 否 |

---

## 10. 参考文档

- **设计文档**: `docs/superpowers/specs/2026-03-19-jwc-career-tools-design.md`
- **实现计划**: `docs/superpowers/plans/2026-03-19-jwc-career-tools-implementation.md`
- **接口说明**: `docs/development_doc/就业指导中心接口说明.md`
- **HTML 示例**: `docs/development_doc/宣讲会信息.txt` 等
