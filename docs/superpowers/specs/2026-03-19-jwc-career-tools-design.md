# 就业指导中心 Tool Calling 设计方案

**日期**: 2026-03-19
**模块**: 就业指导中心 (JWC Career Center)
**类型**: LangGraph Tool Calling

---

## 1. 概述

为中南大学就业信息网 (career.csu.edu.cn) 开发 4 个无需认证的 Tool Calling，供 LangGraph Agent 在处理就业相关咨询时调用。

### 1.1 接口列表

| 接口 | URL | 参数 | 说明 |
|------|-----|------|------|
| 宣讲会信息 | `http://career.csu.edu.cn/teachin` | `zone` (可选) | 校区筛选 |
| 校园招聘 | `http://career.csu.edu.cn/campus/index/category/1` | `keyword` (可选) | 搜索关键字 |
| 实习岗位 | `http://career.csu.edu.cn/campus/index/category/2` | `keyword` (可选) | 搜索关键字 |
| 大型招聘会 | `http://career.csu.edu.cn/jobfair` | 无 | - |

### 1.2 设计原则

- **高内聚低耦合**: 每个工具独立职责，工具间无依赖
- **无需认证**: 不依赖 SessionManager，与 RAG 工具同级别
- **统一错误处理**: 对外隐藏内部错误细节
- **复用现有模式**: 遵循 `client.py → service.py → tools.py` 结构

---

## 2. 项目结构

```
backend/app/core/tools/jwc_career/
├── __init__.py      # 模块导出
├── client.py        # HTTP请求 + BeautifulSoup解析
├── service.py       # 业务逻辑，数据模型
└── tools.py         # 4个 LangChain StructuredTool 定义
```

---

## 3. 数据模型

### TeachinEntry (宣讲会)
| 字段 | 类型 | 说明 |
|------|------|------|
| company | str | 企业名称 |
| location | str | 举办地点 |
| time | str | 举办时间 |

### CampusRecruitEntry (校园招聘)
| 字段 | 类型 | 说明 |
|------|------|------|
| title | str | 招聘公告标题 |
| city | str | 工作城市 |
| publish_time | str | 发布时间 |

### CampusInternEntry (实习信息)
| 字段 | 类型 | 说明 |
|------|------|------|
| title | str | 实习公告标题 |
| city | str | 工作城市 |
| publish_time | str | 发布时间 |

### JobfairEntry (招聘会)
| 字段 | 类型 | 说明 |
|------|------|------|
| name | str | 招聘会名称 |
| city | str | 举办城市 |
| address | str | 举办地址 |
| fair_type | str | 招聘会类型 |
| time | str | 举办时间 |

---

## 4. 工具定义

### 4.1 jwc_teachin

```python
class TeachinInput(BaseModel):
    zone: str = Field(
        default="",
        description="校区名称，可选值：岳麓山校区、杏林校区、天心校区、潇湘校区，空值查询全部"
    )
```

### 4.2 jwc_campus_recruit

```python
class CampusRecruitInput(BaseModel):
    keyword: str = Field(default="", description="搜索关键字")
```

### 4.3 jwc_campus_intern

```python
class CampusInternInput(BaseModel):
    keyword: str = Field(default="", description="搜索关键字")
```

### 4.4 jwc_jobfair

```python
class JobfairInput(BaseModel):
    pass  # 无参数
```

---

## 5. 返回格式

所有工具返回 markdown 表格格式的纯文本字符串。

### 宣讲会示例
```
## 宣讲会查询结果

| 名称 | 举办地点 | 举办时间 |
|------|----------|----------|
| 贝斯（无锡）信息系统有限公司 | 线上宣讲 | 2026-03-19 14:00-15:00(周四) |
| 中建三局基础设施建设投资有限公司 | 岳麓山校区 科教南楼507 | 2026-03-19 14:00-16:00(周四) |
...
```

### 招聘会示例
```
## 招聘会查询结果

| 招聘会名称 | 举办城市 | 举办地址 | 类型 | 举办时间 |
|------------|----------|----------|------|----------|
| 中南大学2026届春季第二场大型综合双选会... | 湖南省 - 长沙市 | 中南大学潇湘校区体育场副场 | 校园招聘会 | 2026-04-19 14:00-18:00(周日) |
...
```

---

## 6. 错误处理

| 场景 | 返回内容 |
|------|----------|
| 网络超时/连接失败 | `"{功能}查询失败，请稍后重试"` |
| HTML解析失败 | `"{功能}查询失败，请稍后重试"` |
| 无数据 | `"{功能}查询结果为空"` |

**原则**: 不暴露外部系统错误细节，保持与现有工具一致的用户体验。

---

## 7. HTTP 请求配置

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "http://career.csu.edu.cn/",
}
timeout = 10  # 秒
```

---

## 8. 与现有代码的关系

### 8.1 独立性
- 不依赖 `SessionManager`（无需认证）
- 不依赖用户 ID
- 独立于 `app/core/tools/jwc/` 模块

### 8.2 集成方式
- 在 `app/core/tools/__init__.py` 中导出，供 Agent 按需引用
- 可与 RAG 工具并列，作为通用无认证工具

### 8.3 依赖
- `requests`: HTTP 请求
- `beautifulsoup4`: HTML 解析

---

## 9. 实现检查清单

- [ ] `client.py`: 实现 4 个接口的 HTTP 请求和 HTML 解析
- [ ] `service.py`: 定义数据模型和业务逻辑
- [ ] `tools.py`: 定义 4 个 LangChain StructuredTool
- [ ] `__init__.py`: 导出所有公共接口
- [ ] `tests/`: 单元测试和集成测试
- [ ] 更新 `app/core/tools/__init__.py`（如需要）

---

## 10. 参考

- 接口文档: `docs/development_doc/就业指导中心接口说明.md`
- HTML 示例: `docs/development_doc/宣讲会信息.txt`, `公司招聘信息.txt`, `公司实习信息.txt`, `招聘会信息.txt`
- 现有工具模式: `app/core/tools/jwc/`
