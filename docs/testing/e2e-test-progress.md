# E2E 测试进度

> 最后更新: 2026-03-19

## 总体进度

| 类别 | 总数 | 已完成 | 通过率 |
|------|------|--------|--------|
| public_tools | 10 | 10 | 100% |
| auth_required | 5 | 5 | 100% |
| auth_tools | 9 | 9 | 100% |
| multi_tool | 11 | 9 | 82% |
| **总计** | **35** | **33** | **94%** |

---

## public_tools ✅

| 用例 | 状态 | 运行时间 | 备注 |
|------|------|----------|------|
| `test_library_search_called_for_book_query` | ✅ PASS | 14s | |
| `test_career_teachin_called_for_recruitment_event_query` | ✅ PASS | 37s | |
| `test_career_campus_recruit_called_for_job_query` | ✅ PASS | 16s | |
| `test_career_campus_intern_called_for_internship_query` | ✅ PASS | 24s | |
| `test_career_jobfair_called_for_job_fair_query` | ✅ PASS | 39s | |
| `test_anonymous_user_can_access_all_public_tools` | ✅ PASS | 49s | |
| `test_library_search_returns_results` | ✅ PASS | - | |
| `test_teachin_with_zone_filter` | ✅ PASS | - | |
| `test_campus_recruit_with_keyword` | ✅ PASS | - | |
| `test_campus_intern_with_keyword` | ✅ PASS | - | |

**运行时间**: 282.17s (4m 42s)

---

## auth_required ✅ 全部通过

| 用例 | 状态 | 依赖 |
|------|------|------|
| `test_login_with_valid_credentials_succeeds` | ✅ PASS | |
| `test_login_with_invalid_credentials_fails` | ✅ PASS | |
| `test_login_rate_limiting` | ✅ PASS | |
| `test_logout_with_valid_token_succeeds` | ✅ PASS | |
| `test_logout_without_token_fails` | ✅ PASS | |

---

## auth_tools ✅ 9/9 全部通过

| 用例 | 状态 | 备注 |
|------|------|------|
| `test_authenticated_user_can_query_grades` | ✅ PASS | |
| `test_authenticated_user_can_query_schedule` | ✅ PASS | |
| `test_authenticated_user_can_query_rank` | ✅ PASS | |
| `test_authenticated_user_can_query_level_exam` | ✅ PASS | |
| `test_jwc_schedule_with_term_parameter` | ✅ PASS | |
| `test_anonymous_user_cannot_query_grades` | ✅ PASS | |
| `test_authenticated_user_can_query_notifications` | ✅ PASS | |
| `test_notification_query_with_department_filter` | ✅ PASS | |
| `test_notification_query_with_date_range` | ✅ PASS | |
| `test_jwc_session_expired_handling` | ✅ PASS | |

---

## multi_tool ✅ 9/11 通过

| 用例 | 状态 | 备注 |
|------|------|------|
| `test_multiple_public_tools_in_sequence` | ✅ PASS | |
| `test_multiple_authenticated_tools_in_sequence` | ✅ PASS | |
| `test_rag_combined_with_authenticated_tool` | ✅ PASS | |
| `test_multi_tool_error_recovery` | ✅ PASS | |
| `test_complex_multi_step_query` | ✅ PASS | |
| `test_tool_call_order_verification` | ✅ PASS | |
| `test_library_search_with_pagination` | ✅ PASS | |
| `test_career_tool_with_zone_and_keyword` | ✅ PASS | |
| `test_query_that_triggers_no_tools` | ✅ PASS | |
| `test_oas_notification_with_multiple_filters` | ⏳ SKIP | |
| `test_rapid_sequential_requests` | ⏳ SKIP | |

---

## streaming_completion ⏳ 待运行

| 用例 | 状态 | 备注 |
|------|------|------|
| `test_anonymous_basic_chat` | ⏳ | |
| `test_anonymous_career_tools` | ⏳ | |
| `test_authenticated_user_chat` | ⏳ | |
| `test_rag_with_knowledge_ids` | ⏳ | |
| `test_multi_turn_conversation` | ⏳ | |
| `test_sse_event_format` | ⏳ | |
| `test_completion_requires_message` | ⏳ | |
| `test_rag_requires_knowledge_ids` | ⏳ | |

---

## 已修复的问题

| 日期 | 问题 | 修复 | 详情 |
|------|------|------|------|
| 2026-03-19 | HTTPBearer auto_error=True 导致 401 | `HTTPBearer(auto_error=False)` | [#001](./e2e-debug-log.md#问题-001-httpbearer-导致-401-unauthorized) |
| 2026-03-19 | gpt-3.5-turbo 模型不存在 | 使用 `settings.openai_model` | [#002](./e2e-debug-log.md#问题-002-模型名称不匹配) |
| 2026-03-19 | loguru 日志不显示 | 配置 `sink=sys.stdout` | [#003](./e2e-debug-log.md#问题-003-loguru-日志不显示) |
| 2026-03-19 | get_current_user 在 credentials 为 None 时返回 500 | 检查 credentials 为 None 并返回 401 | [#005](./e2e-debug-log.md#问题-005-get_current_user-在-credentials-为-none-时返回-500) |
| 2026-03-19 | oa_notification_list 缺少 ctx 参数 | 通过闭包捕获 ctx | [#007](./e2e-debug-log.md#问题-007-oa_notification_list-缺少-ctx-参数) |

详细排查日志: [e2e-debug-log.md](./e2e-debug-log.md)

---

## 下一步

1. 运行 `streaming_completion` 测试（可选）
2. 修复 OA 通知查询失败问题（需要更详细的日志定位）
3. 调查 2 个跳过的 multi_tool 测试
3. 运行 `auth_tools` 测试
4. 运行 `multi_tool` 测试
5. 运行 `streaming_completion` 测试

---

## 运行命令

```bash
cd /home/luorome/software/CampusMind/backend

# 启动后端
uv run uvicorn app.main:app --reload --port 8000 &

# 运行各类测试
uv run pytest tests/e2e/ -m public_tools -v          # 已完成
uv run pytest tests/e2e/ -m auth_required -v         # 待运行
uv run pytest tests/e2e/ -m auth_tools -v          # 待运行
uv run pytest tests/e2e/ -m multi_tool -v           # 待运行
uv run pytest tests/e2e/ -m e2e -v                   # 全部
```
