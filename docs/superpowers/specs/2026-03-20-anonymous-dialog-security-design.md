# Anonymous Dialog Security & Authorization Design

> **Status:** Design Approved
> **Date:** 2026-03-20
> **Type:** Security / Architecture

---

## 1. Overview

Fix the security vulnerability in `completion.py` where `request.user_id` from the frontend was trusted blindly. Implement proper server-side authorization for dialog access, supporting both anonymous (unauthenticated) and logged-in users with proper isolation.

### Goals

1. **Fix IDOR vulnerability** — never trust `user_id` from client request body
2. **Support anonymous dialogs** — allow unauthenticated users to create/continue dialogs
3. **Prevent cross-user data leakage** — ensure users can only access their own dialogs
4. **Align with LangGraph** — use `dialog.id` as `thread_id` (frontend-generated UUID)

---

## 2. Authorization Model

### Rules

| Scenario | Condition | Access |
|----------|-----------|--------|
| Anonymous + dialog exists with NULL user_id | `dialog.user_id IS NULL AND dialog.id = provided_id` | ✅ Allow |
| Anonymous + dialog exists with non-NULL user_id | — | ❌ 403 Forbidden |
| Logged-in user + dialog belongs to them | `dialog.user_id = jwt.user_id AND dialog.id = provided_id` | ✅ Allow |
| Logged-in user + dialog belongs to another user | `dialog.user_id != jwt.user_id` | ❌ 403 Forbidden |
| Any user + dialog doesn't exist | (insert) | ✅ Allow (create new) |

### Key Principle

**Anonymous users can ONLY access dialogs with `user_id = NULL`.** Logged-in users can ONLY access dialogs with matching `user_id`.

---

## 3. Schema Changes

### 3.1 SQL Schema (`docs/database/schema.sql`)

```sql
-- Before:
user_id TEXT NOT NULL,
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE

-- After:
user_id TEXT,  -- NULL for anonymous dialogs
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
```

`ON DELETE SET NULL`: when a user account is deleted, their dialogs become anonymous (not deleted).

### 3.2 Python Model (`app/database/models/dialog.py`)

```python
# Before:
user_id: str = Field(index=True, description="User ID")

# After:
user_id: Optional[str] = Field(default=None, index=True, description="User ID (NULL for anonymous)")
```

---

## 4. New Repository Layer

### 4.1 Location

`app/repositories/dialog_repository.py`

### 4.2 `DialogRepository` Class

```python
class DialogRepository:
    @staticmethod
    async def get_or_create_dialog(
        session: AsyncSession,
        dialog_id: str,              # Frontend-provided (thread_id)
        jwt_user_id: Optional[str],  # From JWT, None if anonymous
        agent_id: Optional[str] = None,
    ) -> tuple[Dialog, bool]:
        """
        Get existing dialog with authorization check, or create new.

        Authorization rules:
        - Anonymous (jwt_user_id=None): can only access/create dialogs with user_id=NULL
        - Logged-in: can only access dialogs where user_id matches jwt_user_id

        Returns:
            (dialog, created_new): dialog instance and whether it was newly created

        Raises:
            ForbiddenError: user attempts to access another user's dialog
        """
```

### 4.3 Why Repository Pattern

- **High cohesion**: all dialog authorization logic in one place
- **Low coupling**: `completion.py` doesn't need to know authorization rules
- **Reusable**: can be used by any future endpoint that needs dialog access

---

## 5. API Changes

### 5.1 Remove `user_id` from Request Body

Remove `user_id` field from these request models in `completion.py`:

- `CompletionRequest`
- `ChatRequest`

The `user_id` is determined **server-side only** from JWT via `get_optional_user()`.

### 5.2 `dialog_id` as Thread ID

Frontend generates UUIDs for each chat window, sent as `dialog_id`. This serves as the LangGraph `thread_id`.

### 5.3 Endpoint Changes

| Endpoint | Change |
|----------|--------|
| `POST /completion/stream` | Use `DialogRepository`, remove `request.user_id` |
| `POST /completion` | Use `DialogRepository`, remove `request.user_id` |
| `POST /chat/stream` | Use `DialogRepository`, remove `request.user_id` |
| `POST /chat` | Use `DialogRepository`, remove `request.user_id` |

---

## 6. Files to Modify

| File | Change |
|------|--------|
| `docs/database/schema.sql` | `user_id` → nullable, FK `SET NULL` |
| `docs/database/database-onboarding.md` | Document the new schema |
| `app/database/models/dialog.py` | `user_id: Optional[str] = None` |
| `app/repositories/dialog_repository.py` | **New** — authorization-aware dialog access |
| `app/api/v1/completion.py` | Use repo, remove client `user_id`, fix IDOR |
| `app/services/dialog/dialog.py` | Support `Optional[user_id]` |

---

## 7. Error Handling

| Error | HTTP Status | Response |
|-------|-------------|----------|
| Attempt to access another user's dialog | 403 Forbidden | `{"detail": "Access denied to this dialog"}` |
| Anonymous accessing logged-in dialog | 403 Forbidden | `{"detail": "Access denied to this dialog"}` |
| Dialog not found | (create new) | Silently create |

---

## 8. Backward Compatibility

- Frontend must be updated to generate and persist `dialog_id` (UUID) per chat window
- Existing dialogs with `user_id=NULL` (after schema migration) will be treated as anonymous
- No existing data migration needed — existing rows already have non-NULL `user_id`

---

## 9. Testing Considerations

- Anonymous dialog creation and continuation
- Logged-in user cannot access another user's dialog (IDOR test)
- Anonymous user cannot access logged-in user's dialog
- Dialog list filters correctly by user (logged-in) or shows only NULL (anonymous)
