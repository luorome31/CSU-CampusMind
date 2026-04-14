# CLAUDE.md

This file provides essential guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CampusMind is a full-stack AI-powered campus assistant application with a React web frontend, a React Native mobile client, and a FastAPI backend. The system uses a LangGraph ReAct agent to answer user queries by combining RAG (Retrieval-Augmented Generation) with direct integration into university systems (JWC, Library, Career Center, OA).

```
CampusMind/
├── frontend/                    # React + Vite + TypeScript SPA
│   └── src/
│       ├── api/               # API client modules
│       ├── components/        # Reusable UI components (ui/, chat/, layout/)
│       ├── features/         # Feature modules (auth/, chat/)
│       ├── styles/           # CSS tokens (colors, spacing, typography, elevation)
│       ├── utils/            # Utilities
│       └── playground/       # Playground mode entry
│
├── mobile/                      # React Native mobile client
│   └── docs/
│       ├── progress-log.md    # Mobile development progress log
│       └── problems-log.md    # Issues and solutions encountered
│
├── backend/                    # FastAPI + Python backend
│   ├── app/
│   │   ├── api/v1/          # API routers
│   │   ├── core/             # Core modules (agents/, session/, tools/)
│   │   ├── services/        # Service layer
│   │   └── schema/           # Pydantic schemas
│   └── tests/                # Backend tests
│
└── docs/                      # Project documentation
```

## Test-Driven Development (TDD) Requirement

**Mobile development MUST follow TDD workflow:**

### Mobile (React Native)
1. **Write the test first** - Before implementing any feature, fix, or refactor, write the test that defines the expected behavior
2. **Run test to verify failure** - Confirm the test fails before writing implementation code
3. **Implement the minimum code** - Write only enough code to make the test pass
4. **Refactor if needed** - Improve code while keeping tests green

- All new components, hooks, and utility functions require tests
- Test file location: next to the source file (e.g., `Button.test.tsx` alongside `Button.tsx`)
- Use Jest + React Native Testing Library for component tests
- Use Jest for testing hooks and utilities
- Platform-specific tests: use `*.native.test.tsx` for shared code, `*.ios.test.tsx` / `*.android.test.tsx` for platform-specific
- **Test authenticity**: Do not cheat on tests. When a test fails, the implementation should be fixed to pass the test, not the test modified to pass (unless the test itself is outdated or inaccurate)

## Commit Message Format

使用中文撰写 commit，格式为 `type(domain): action`。

**action 规范**：action 应该简练指出具体实现了什么，而不是泛泛地说"完成Task1"或"修复问题"。

| 良好示例 | 不良示例 |
|----------|----------|
| `feat(chat): 添加流式输出动画` | `feat(chat): 完成了聊天功能` |
| `fix(auth): 修复 Token 过期后未自动登出` | `fix(auth): 修复登录问题` |
| `refactor(mobile): 抽取通用 Button 组件` | `refactor(mobile): 重构组件` |
| `docs(backend): 补充登录 API 接口文档` | `docs(backend): 更新文档` |

## Mobile (React Native) Development Workflow

When working on `mobile/` directory, follow this workflow:

### 1. 阅读项目文档

开始任何移动端任务前，先阅读以下文档：

| 文档 | 用途 |
|------|------|
| `mobile/docs/campusmind-mobile-prd.md` | 架构设计、Tab 结构、功能模块说明 |
| `mobile/docs/progress-log.md` | 项目进度、已完成模块追踪 |
| `mobile/docs/problems-log.md` | 遇到的问题与解决方案，避免重复踩坑 |
| `mobile/docs/feature-list.json` | 所有功能任务清单及状态 |

### 2. 领取任务模块

从 `feature-list.json` 的 `moduleGroups` 中领取任务：

- 查看 `moduleGroups[].features` 和 `moduleGroups[].status`
- 选择 `status: "pending"` 的模块领取
- 领取后在 `feature-list.json` 中将该任务 `status` 改为 `"in_progress"`

### 3. 创建功能分支

```bash
# 基于 main 创建功能分支，分支名体现功能模块
git checkout main
git pull origin main
git checkout -b feat/mobile/<module-name>
# 例如：feat/mobile/auth-login-screen
```

### 4. 使用 Superpowers 工作流开发

遵循以下步骤（顺序不可跳过的环节用 ⚠️ 标注）：

1. ⚠️ **brainstorming** - 理解需求，明确设计决策
2. **writing-plans** - 制定实现计划
3. **executing-plans** - 执行开发
4. ⚠️ **requesting-code-review** - 代码审查

> 详细工作流见 `superpowers:*` 相关 skill

---

## Compact Instructions

Retention Priorities:
1. Architectural decisions, do not summarize
2. Modified files and key changes
3. Verification state, pass/fail
4. Unresolved TODOs and rollback notes
5. Tool outputs, can be deleted, retaining only the pass/fail conclusion
