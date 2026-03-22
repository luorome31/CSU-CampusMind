# Testing

## Frontend Testing (Vitest + React Testing Library)

### Framework Details

- **Framework**: Vitest with jsdom environment
- **Setup**: `src/test/setup.ts` imports `@testing-library/jest-dom`
- **Test files**: `src/**/*.{test,spec}.{ts,tsx}`
- **Location**: Test file next to source file (e.g., `Button.test.tsx` alongside `Button.tsx`)

### Commands

```bash
npm run test              # Run tests in watch mode
npm run test:run         # Run tests once
npm run test:coverage     # Run tests with coverage report
```

### What to Test

| Priority | Area | What to Test |
|----------|------|-------------|
| High | `api/client.ts` | Token injection, 401 auto-logout, error parsing |
| High | `api/chat.ts` | SSE stream parsing, `X-Dialog-ID` extraction |
| High | `chatStore` | SSE message appending, `dialogId` management |
| High | `authStore` | Login/logout state machine, token restoration |
| Medium | `knowledgeListStore` | KB list fetch, file list fetch |
| Medium | `buildStore` | Crawl task creation, batch URL handling |
| Low | Utility functions | `parseSSELines`, error response parsers |

### What NOT to Test

| Skip | Reason |
|------|--------|
| Pure UI components (Button, Card, Input) | Too simple, no business logic |
| CSS/styling | Only test behavior, not appearance |
| Layout components | Integration test only |

---

## Backend Testing (pytest)

### Test Markers

Defined in `backend/pytest.ini`:

| Marker | Purpose |
|--------|---------|
| `unit` | Unit tests |
| `integration` | Integration tests |
| `api` | API tests |
| `e2e` | End-to-end tests |
| `auth_required` | Tests requiring authentication |
| `public_tools` | Tests for public tools |
| `auth_tools` | Tests for authenticated tools |
| `slow` | Slow-running tests |

### Commands

```bash
uv run pytest tests/ -v                    # All tests
uv run pytest tests/api/ -v                # API tests only
uv run pytest -m "not e2e"                # Skip e2e tests
uv run pytest -k "test_name"               # Specific test
```

---

## TDD Workflow (Frontend)

1. **Write the test first** - Before implementing, write test defining expected behavior
2. **Run test to verify failure** - Confirm test fails before writing code
3. **Implement minimum code** - Write only enough to make test pass
4. **Refactor if needed** - Improve while keeping tests green

```bash
npm run test:run  # Verify new test fails
# ... implement feature ...
npm run test:run  # Verify test passes
```
