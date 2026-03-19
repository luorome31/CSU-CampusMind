# E2E Test Suite

End-to-end tests for CampusMind backend API, covering authentication, streaming completion, and all tool calling flows.

## Structure

```
tests/e2e/
├── conftest.py              # Shared fixtures and configuration
├── test_auth.py             # Authentication flow tests
├── test_streaming_completion.py  # Streaming API tests
├── test_public_tools.py     # Public tools tests (no auth required)
├── test_authenticated_tools.py   # Authenticated tools tests (JWC, OA)
└── test_multi_tool_calls.py  # Multi-tool scenarios
```

## Prerequisites

1. **Backend must be running**:
   ```bash
   cd backend
   uv run uvicorn app.main:app --reload --port 8000
   ```

2. **Credentials in `.env`**:
   ```bash
   # Add to backend/.env
   CAS_USERNAME="your_student_id"
   CAS_PASSWORD="your_password"
   ```

## Running Tests

### Run all E2E tests
```bash
cd backend
uv run pytest tests/e2e/ -v
```

### Run specific test file
```bash
uv run pytest tests/e2e/test_auth.py -v
```

### Run tests by marker
```bash
# Only public tool tests (no auth required)
uv run pytest tests/e2e/ -m "public_tools" -v

# Only authenticated tool tests
uv run pytest tests/e2e/ -m "auth_required" -v
```

### Run with detailed output
```bash
# Show all print statements
uv run pytest tests/e2e/ -v -s

# Show extra test summary
uv run pytest tests/e2e/ -v --tb=short
```

## Test Categories

### Authentication (`test_auth.py`)
- `test_login_with_valid_credentials_succeeds` - Valid CAS login
- `test_login_with_invalid_credentials_fails` - Wrong password handling
- `test_login_rate_limiting` - Rate limiting on failed attempts
- `test_logout_with_valid_token_succeeds` - Logout flow
- `test_logout_without_token_fails` - Auth requirement check

### Streaming Completion (`test_streaming_completion.py`)
- `test_anonymous_basic_chat` - Anonymous user chat
- `test_anonymous_career_tools` - Career tools access
- `test_authenticated_user_chat` - Authenticated chat
- `test_rag_with_knowledge_ids` - RAG-enabled requests
- `test_multi_turn_conversation` - Dialog continuity
- `test_sse_event_format` - SSE format validation

### Public Tools (`test_public_tools.py`)
- `test_library_search_called_for_book_query`
- `test_career_teachin_called_for_recruitment_event_query`
- `test_career_campus_recruit_called_for_job_query`
- `test_career_campus_intern_called_for_internship_query`
- `test_career_jobfair_called_for_job_fair_query`

### Authenticated Tools (`test_authenticated_tools.py`)
- `test_authenticated_user_can_query_grades` (jwc_grade)
- `test_authenticated_user_can_query_schedule` (jwc_schedule)
- `test_authenticated_user_can_query_rank` (jwc_rank)
- `test_authenticated_user_can_query_level_exam` (jwc_level_exam)
- `test_authenticated_user_can_query_notifications` (oa_notification_list)

### Multi-Tool Calls (`test_multi_tool_calls.py`)
- `test_multiple_public_tools_in_sequence`
- `test_multiple_authenticated_tools_in_sequence`
- `test_rag_combined_with_authenticated_tool`
- `test_complex_multi_step_query`
- `test_tool_call_order_verification`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TEST_BASE_URL` | Backend URL | `http://localhost:8000` |
| `CAS_USERNAME` | Student ID for auth tests | (from .env) |
| `CAS_PASSWORD` | Password for auth tests | (from .env) |

## Debugging

### Enable verbose logging
```bash
uv run pytest tests/e2e/ -v -s --log-cli-level=INFO
```

### Run single test
```bash
uv run pytest tests/e2e/test_auth.py::TestAuthLogin::test_login_with_valid_credentials_succeeds -v -s
```

### Check SSE events
```python
# In test code, access StreamingResponse events:
result = self._send_completion(...)
for event in result.events:
    print(f"{event.type}: {event.data}")
```

## Troubleshooting

### "Connection refused" errors
- Ensure backend is running: `uv run uvicorn app.main:app --reload`
- Check port: default is 8000

### "Authentication failed" errors
- Verify `CAS_USERNAME` and `CAS_PASSWORD` in `.env`
- Check if credentials are valid

### "Token appears to be too short" assertion
- JWT token format may differ - this is informational only

### Tests are slow
- Streaming requests have 120s timeout
- Use `-m "not slow"` to skip slow tests during development
