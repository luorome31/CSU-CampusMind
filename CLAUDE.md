# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
│       │   ├── 01-DESIGN_TOKENS_REFERENCE.md
│       │   ├── 02-COLOR_SYSTEM.md
│       │   ├── 03-TYPOGRAPHY_GUIDE.md
│       │   ├── 04-COMPONENT_GUIDELINES.md
│       │   ├── 05-SPACING_SYSTEM.md
│       │   ├── 06-ICON_GUIDELINES.md
│       │   └── 07-RESPONSIVE_DESIGN.md
│       ├── frontend-progress-log.md
│       ├── frontend-question-log.md
│       └── superpowers/        # Feature specs and plans
│
├── backend/                    # FastAPI + Python backend
│   ├── app/
│   │   ├── api/v1/            # API routers (auth/, completion/, crawl/, knowledge/, etc.)
│   │   ├── core/              # Core modules (agents/, session/, tools/)
│   │   ├── services/          # Service layer (rag/, knowledge/, crawl/, dialog/)
│   │   ├── database/          # Database models and session
│   │   └── schema/            # Pydantic schemas
│   ├── tests/                 # Backend tests
│   ├── docs/                   # Backend documentation
│   │   ├── api/               # API endpoint documentation
│   │   ├── auth/               # Authentication docs (flow, session management)
│   │   ├── models/             # Database model documentation
│   │   ├── rag/                # RAG pipeline docs (indexing, retrieval)
│   │   ├── tools/              # Tool integrations (jwc/, library/, career/, oa/)
│   │   ├── config/             # Configuration docs
│   │   ├── deploy/             # Deployment docs
│   │   └── testing/            # Testing guide and fixtures
│   └── CLAUDE.md              # Detailed backend guidance
```

## Common Commands

### Frontend
```bash
cd frontend
npm install              # Install dependencies
npm run dev              # Start dev server (http://localhost:5173)
npm run build            # Type check + production build
npm run test             # Run tests in watch mode
npm run test:run        # Run tests once
npm run test:coverage   # Run tests with coverage report
```

### Backend
```bash
cd backend
uv sync                  # Install dependencies (uv)

# Run the backend server in tmux (for agent observation)
tmux new-session -d -s campusmind-server 'cd /home/luorome/software/CampusMind/backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000'
tmux attach -t campusmind-server  # Attach to view logs

# Run tests in tmux (for agent observation)
tmux new-session -d -s campusmind-tests 'cd /home/luorome/software/CampusMind/backend && uv run pytest --tb=short -v'
tmux attach -t campusmind-tests  # Attach to view logs

# Run specific tests
uv run pytest tests/ -v                                    # All tests
uv run pytest tests/api/ -v                                # API tests only
uv run pytest -m "not e2e"                               # Skip e2e tests
uv run pytest -k "test_name"                              # Specific test
```

## Architecture

### Frontend (React + Vite)
- **State Management**: Zustand stores (`authStore`, `chatStore`)
- **Routing**: React Router 6 with protected routes
- **API Client**: Custom client in `frontend/src/api/` with SSE streaming support
- **Key Routes**:
  - `/login` - Login page
  - `/` - Chat interface (index)
  - `/knowledge` - Knowledge base list
  - `/knowledge/build` - Knowledge base builder

For detailed backend architecture, see `backend/CLAUDE.md`.

## Environment Setup

### Frontend
Copy `frontend/.env.example` to `frontend/.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Backend
Copy `backend/.env.example` to `backend/.env` and configure:
- Database: `DATABASE_URL` (SQLite for dev, PostgreSQL for prod)
- Redis: `REDIS_URL`
- LLM: `OPENAI_API_KEY` or `EMBEDDING_API_KEY`
- ChromaDB: `CHROMA_PERSIST_PATH`
- Elasticsearch: `ELASTICSEARCH_HOSTS`
- CAS credentials for university systems: `CAS_USERNAME`, `CAS_PASSWORD`

## Testing

### Frontend (Vitest + React Testing Library)
- **Framework**: Vitest with happy-dom environment
- **Setup**: `src/test/setup.ts` imports `@testing-library/jest-dom`
- **Test files**: `src/**/*.{test,spec}.{ts,tsx}`
- **Commands**: `npm run test` (watch), `npm run test:run` (single run), `npm run test:coverage`

### Backend (pytest)
Backend tests use pytest with markers defined in `backend/pytest.ini`:
- `unit`, `integration`, `api`, `e2e` - Test categories
- `auth_required`, `public_tools`, `auth_tools` - Auth-related tests
- `slow` - Slow-running tests

## Test-Driven Development (TDD) Requirement

**Frontend development MUST follow TDD workflow:**

1. **Write the test first** - Before implementing any feature, fix, or refactor, write the test that defines the expected behavior
2. **Run test to verify failure** - Confirm the test fails before writing implementation code
3. **Implement the minimum code** - Write only enough code to make the test pass
4. **Refactor if needed** - Improve code while keeping tests green

```bash
# TDD workflow example
npm run test:run              # Verify new test fails
# ... implement feature ...
npm run test:run              # Verify test passes
```

- All new components, hooks, stores, and utility functions require tests
- Test file location: next to the source file (e.g., `Button.test.tsx` alongside `Button.tsx`)
- Use React Testing Library for component tests (query by role, label, or text)
- Use Vitest for testing hooks and utilities

## Commit Message Format

使用中文撰写 commit，格式为 `type(domain): action`，简洁专业。

## Git Hooks (lefthook)

This project uses [lefthook](https://github.com/evilmartians/lefthook) for local Git hooks. Hooks are configured in `lefthook.yml` at the project root.

| Hook | Trigger | Actions |
|------|---------|---------|
| `pre-commit` | `git commit` | backend: `ruff check` / frontend: `npm run build` |
| `pre-push` | `git push` | backend: `uv run pytest -m "not e2e"` / frontend: `npm run test:run` |
| `pre-merge` | `git merge` | backend: `uv run pytest -m "not e2e"` / frontend: `npm run test:run` |
| `pre-rebase` | `git rebase` | backend: `uv run pytest -m "not e2e"` / frontend: `npm run test:run` |

- Hooks run in parallel when possible
- `pre-commit` only checks staged files (skips if none)
- Install hooks: `cd frontend && npm run prepare -- --force`

## Compact Instructions

Retention Priorities:
1. Architectural decisions, do not summarize
2. Modified files and key changes
3. Verification state, pass/fail
4. Unresolved TODOs and rollback notes
5. Tool outputs, can be deleted, retaining only the pass/fail conclusion
