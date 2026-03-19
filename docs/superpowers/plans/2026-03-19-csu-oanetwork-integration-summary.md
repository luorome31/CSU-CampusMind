# CSU OANetwork 校内通知工具集成 — 任务总结

**日期:** 2026-03-19
**任务状态:** 已完成

---

## 1. 任务概述

将中南大学校内办公网（OANetwork）的通知查询 API 集成为 LangGraph Tool，使认证用户可以通过校园助手 Agent 搜索校内通知。

### 1.1 认证流程

OANetwork 使用 3 步子会话激活机制，依赖预存在的 CASTGC cookie：

```
1. GET https://oa.csu.edu.cn/con/        → 从 Cookie 提取 JSESSIONID（子会话 S）
2. GET CAS登录URL?service=... (携带CASTGC) → 获取重定向地址
3. GET 重定向地址                        → 激活子会话 S
```

**注意:** CASTGC 来自用户 `/auth/login` 的已有会话，OASessionProvider 不进行用户名密码再认证。

---

## 2. 架构设计

### 2.1 组件架构

```
backend/app/
├── core/
│   ├── session/
│   │   └── providers/
│   │       └── oa.py              # OASessionProvider (NEW)
│   └── tools/
│       └── oa/
│           ├── __init__.py        # create_oa_tools() (NEW)
│           ├── notification.py    # OANotificationList Tool (NEW)
│           └── departments.py      # DepartmentEnum + build_params() (NEW)
```

### 2.2 核心设计决策

| 决策 | 说明 |
|------|------|
| 单工具设计 | 合并为 `OANotificationList`，避免 LLM 幻觉 |
| DepartmentEnum | 85 个部门，使用 `Literal` 类型严格限制 LLM 可选值 |
| tableName 硬编码 | `"ZNDX_ZHBG_GGTZ"` 不暴露给 LLM |
| 工具始终注册 | `create_oa_tools(ctx)` 无条件加入工具列表，认证检查在工具内部 |
| Session 自动刷新 | 3xx 响应时自动重新获取会话 |

---

## 3. 文件清单

### 3.1 新增文件

| 文件路径 | 说明 |
|----------|------|
| `backend/app/core/session/providers/oa.py` | OASessionProvider 实现 |
| `backend/app/core/tools/oa/departments.py` | DepartmentEnum + build_params() |
| `backend/app/core/tools/oa/notification.py` | OANotificationList Tool |
| `backend/app/core/tools/oa/__init__.py` | create_oa_tools() 工厂函数 |
| `backend/tests/core/session/test_providers_oa.py` | Provider 单元测试 (8 测试) |
| `backend/tests/core/session/test_oa_notification.py` | Tool 单元测试 (13 测试) |

### 3.2 修改文件

| 文件路径 | 修改内容 |
|----------|----------|
| `backend/app/core/session/providers/__init__.py` | 注册 OASessionProvider |
| `backend/app/core/session/manager.py` | 添加 `Subsystem.OA` + `get_oa_session()` |
| `backend/app/core/agents/factory.py` | 集成 OA 工具到 AgentFactory |

---

## 4. API 集成

### 4.1 通知查询接口

- **URL:** `https://oa.csu.edu.cn/con/xnbg/contentList`
- **Method:** POST
- **Content-Type:** `application/x-www-form-urlencoded`

### 4.2 查询参数构造

`build_params()` 函数构造 SQL WHERE 条件，base64 编码后作为 `params` 参数：

```python
def build_params(
    qssj: str = "",    # 起始时间 YYYY-MM-DD
    jssj: str = "",    # 结束时间 YYYY-MM-DD
    qcbmmc: str = "",  # 起草部门（模糊匹配）
    wjbt: str = "",    # 文件标题关键词（模糊匹配）
    qwss: str = "",    # 全文搜索（模糊匹配）
    hid_odby: str = "", # 排序字段
) -> str:
    # 构造 SQL 条件 → base64 编码 → JSON 字符串
```

### 4.3 响应格式

```json
{
  "data": [
    {
      "JLNM": "B50C40318DCC41828C0ABB437DF6F019",
      "QCZHXM": "陈维伟",
      "FWZ": "中大人字",
      "QCSJ": "2026-02-09",
      "WJBT": "关于确认戴吾蛟等同志为正高二、三级岗位聘用人员的通知",
      "YWMS": "行政发文",
      "DJSJP": "Feb 11, 2026 6:27:12 PM",
      "LLCS": 3123,
      "QCBMMC": "人事处",
      "FWN": "2026",
      "DJSJ": "2026-02-11"
    }
  ],
  "count": 2214
}
```

---

## 5. Tool Schema

```python
class OANotificationListInput(BaseModel):
    qssj: Optional[str] = Field(default=None, description="起始时间，格式 YYYY-MM-DD")
    jssj: Optional[str] = Field(default=None, description="结束时间，格式 YYYY-MM-DD")
    qcbmmc: Optional[DepartmentEnum] = Field(default=None, description="起草部门")
    wjbt: Optional[str] = Field(default=None, description="文件标题关键词（模糊匹配）")
    qwss: Optional[str] = Field(default=None, description="全文搜索关键词")
    pageNo: int = Field(default=1, description="页码，从1开始")
    pageSize: int = Field(default=20, description="每页条数，建议不超过50")
```

---

## 6. Git 提交历史

| Commit | 描述 |
|--------|------|
| `5331fb0` | feat(session): add OASessionProvider for CSU OANetwork |
| `82d7316` | refactor(test): move test_oa.py to correct location |
| `d7520f9` | feat(oa): add OANotificationList tool for CSU campus notifications |
| `3c7d89e` | fix(oa): fix DepartmentEnum and remove code duplication |
| `9e7557c` | feat(agent): integrate OANotificationList tool into AgentFactory |
| `26b275d` | fix(agent): add OA tools unconditionally per spec |

---

## 7. 测试覆盖

| 测试文件 | 测试数 | 状态 |
|----------|--------|------|
| `tests/core/session/test_providers_oa.py` | 8 | ✅ 通过 |
| `tests/core/session/test_oa_notification.py` | 13 | ✅ 通过 |
| **总计** | **21** | **✅ 全部通过** |

### 7.1 测试用例清单

**OASessionProvider:**
- `test_provider_registered` — 验证自动注册到 SubsystemSessionProvider
- `test_subsystem_name_is_oa` — 验证 subsystem_name = "oa"
- `test_fetch_session_creates_session` — 验证创建新 session
- `test_fetch_session_sets_castgc` — 验证 CASTGC cookie 设置
- `test_fetch_session_first_request_to_oa` — 验证第一步请求 OA 首页
- `test_fetch_session_second_request_to_cas` — 验证第二步请求 CAS
- `test_fetch_session_returns_session` — 验证返回 session 对象
- `test_cas_service_url_encoded` — 验证 CAS SERVICE URL 编码正确

**OANotificationList:**
- `test_build_params_with_all_fields` — 验证全参数构造
- `test_build_params_empty_fields` — 验证空参数构造
- `test_build_params_partial_fields` — 验证部分参数构造
- `test_build_params_only_qcbmmc` — 验证仅部门参数
- `test_build_params_time_range_only` — 验证仅时间范围
- `test_department_enum_has_school_office` — 验证学校办公室枚举值
- `test_department_enum_has_personnel_division` — 验证人事处枚举值
- `test_department_enum_all_values_are_strings` — 验证所有枚举值为非空字符串
- `test_department_enum_has_undergraduate_college` — 验证本科生院
- `test_department_enum_has_graduate_school` — 验证研究生院
- `test_department_enum_has_library` — 验证图书馆
- `test_department_enum_has_research_division` — 验证科学研究部
- `test_department_enum_values_are_exact_chinese_strings` — 验证中文原文

---

## 8. 设计亮点与踩坑记录

### 8.1 设计亮点

1. **Enum 生成方式:** 使用 `Enum('DepartmentEnum', {...}, type=str)` 函数式 API，兼容 Python 3.11+ 的 `StrEnum` 行为
2. **Session 刷新:** 3xx 响应时自动重新获取会话，无需手动干预
3. **代码复用:** 结果格式化逻辑提取为 `_format_notification_results()` 辅助函数

### 8.2 踩坑记录

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| DepartmentEnum Pydantic 验证失败 | 动态 `type()` 创建的 enum 在 Pydantic V1 下验证异常 | 改用标准 `Enum` with `str` mixin |
| 测试文件位置不一致 | JWC 测试在 `tests/core/session/`，OA 初始放在 `tests/app/core/session/providers/` | 移动到 `tests/core/session/test_providers_oa.py` |
| 工具注册位置错误 | 初始放在 `if ctx.is_authenticated:` 内，但 spec 要求无条件注册 | 移除条件判断，认证检查在工具内部进行 |

---

## 9. 后续开发建议

### 9.1 可扩展功能

- [ ] 添加通知详情查询工具（根据 JLNM 获取完整通知内容）
- [ ] 支持更多 tableName（如 `ZNDX_ZHBG_ZXGW` 校内通知）
- [ ] 添加缓存层减少 API 调用

### 9.2 测试增强

- [ ] 集成测试（需要真实 OA 凭证）
- [ ] 3xx 重定向场景的 mock 测试
- [ ] Session 过期后的重试逻辑测试

---

## 10. 参考文档

- [设计文档](./2026-03-19-csu-oanetwork-notification-tool-design.md)
- [实现计划](./2026-03-19-csu-oanetwork-notification-tool-plan.md)
- [子系统集成指南](../subsystem-integration-guide.md)
