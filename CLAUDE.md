# CLAUDE.md

This file provides essential guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CampusMind is a full-stack AI-powered campus assistant application with a React frontend and FastAPI backend. The system uses a LangGraph ReAct agent to answer user queries by combining RAG (Retrieval-Augmented Generation) with direct integration into university systems (JWC, Library, Career Center, OA).

```
CampusMind/
├── frontend/                    # React + Vite + TypeScript SPA
│   ├── src/
│   │   ├── api/               # API client modules
│   │   ├── components/        # Reusable UI components (ui/, chat/, layout/)
│   │   ├── features/           # Feature modules (auth/, chat/)
│   │   ├── styles/             # CSS tokens (colors, spacing, typography, elevation)
│   │   ├── utils/              # Utilities
│   │   ├── test/               # Test setup and utilities
│   │   └── playground/         # Playground mode entry
│   └── docs/                   # Frontend documentation
│       ├── ARCHITECTURE.md     # Frontend architecture overview
│       ├── styles/             # Design system documentation
│       ├── frontend-progress-log.md
│       ├── frontend-question-log.md
│       └── superpowers/        # Feature specs and plans
│
├── backend/                    # FastAPI + Python backend
│   ├── app/
│   │   ├── api/v1/            # API routers
│   │   ├── core/              # Core modules (agents/, session/, tools/)
│   │   ├── services/          # Service layer
│   │   └── schema/            # Pydantic schemas
│   └── tests/                 # Backend tests
```

## Rules Index

Detailed rules are organized in `.claude/rules/`. These are automatically loaded by Claude Code:

| Category | File | When to Use |
|----------|------|-------------|
| **Frontend Docs** | `frontend-docs.md` | Frontend task 开始时读取，结束时更新 |
| **Frontend Commands** | `frontend-commands.md` | 执行前端命令时 (dev/build/test) |
| **Backend Commands** | `backend-commands.md` | 执行后端命令时 (server/test) |
| **Frontend Skills** | `frontend-skills.md` | UI/组件实现前必须使用 /frontend-design skill |
| **Playwright MCP** | `playwright-mcp.md` | 前端运行时验证、UI 调试时使用 |
| **Backend Architecture** | `backend-architecture.md` | 理解后端结构或新增 API 时参考 |
| **Environment Setup** | `environment-setup.md` | 初始化项目环境时配置 |
| **Git Hooks** | `git-hooks.md` | git 操作触发 hooks 时参考 |
| **Testing** | `testing.md` | 编写测试或运行测试时参考 |

## Test-Driven Development (TDD) Requirement

**Frontend development MUST follow TDD workflow:**

1. **Write the test first** - Before implementing any feature, fix, or refactor, write the test that defines the expected behavior
2. **Run test to verify failure** - Confirm the test fails before writing implementation code
3. **Implement the minimum code** - Write only enough code to make the test pass
4. **Refactor if needed** - Improve code while keeping tests green

- All new components, hooks, stores, and utility functions require tests
- Test file location: next to the source file (e.g., `Button.test.tsx` alongside `Button.tsx`)
- Use React Testing Library for component tests (query by role, label, or text)
- Use Vitest for testing hooks and utilities

## Commit Message Format

使用中文撰写 commit，格式为 `type(domain): action`，简洁专业。

## Compact Instructions

Retention Priorities:
1. Architectural decisions, do not summarize
2. Modified files and key changes
3. Verification state, pass/fail
4. Unresolved TODOs and rollback notes
5. Tool outputs, can be deleted, retaining only the pass/fail conclusion
