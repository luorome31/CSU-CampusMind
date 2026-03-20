# API Refactor Design

**Date**: 2026-03-20
**Author**: Claude
**Status**: Approved

## Overview

Refactor CampusMind backend API to eliminate redundancy, improve naming consistency, and optimize batch processing performance.

---

## 1. Delete Chat Endpoints

### Changes

Remove the following 4 endpoints from `app/api/v1/completion.py`:

| Method | Endpoint | Reason |
|--------|----------|--------|
| `POST` | `/api/v1/chat` | Duplicate of `/api/v1/completion` |
| `POST` | `/api/v1/chat/stream` | Duplicate of `/api/v1/completion/stream` |

### Rationale

- `completion` and `chat` endpoints are functionally identical
- Both call the same `generate_stream()` generator and save history the same way
- No differentiation in functionality or purpose
- Frontend should use `completion` endpoints only

### Files Affected

- `app/api/v1/completion.py`: Remove `ChatRequest` class and `/chat`, `/chat/stream` endpoints

---

## 2. Rename Endpoints for REST Consistency

### Changes

| Original | New | Method | Description |
|----------|-----|--------|-------------|
| `POST /knowledge_file/status` | `PATCH /knowledge_file/{file_id}` | `PATCH` | Update file status |
| `GET /knowledge/list/{user_id}` | `GET /users/{user_id}/knowledge` | `GET` | List user's knowledge bases |
| `GET /knowledge_file/list/{knowledge_id}` | `GET /knowledge/{knowledge_id}/files` | `GET` | List files in knowledge base |

### Rationale

- Follow RESTful resource-oriented design
- Use HTTP methods correctly (`PATCH` for partial updates)
- Nested resources under parent (`/users/{id}/knowledge`)
- No backward compatibility needed (internal API, frontend可控)

### Request Model for PATCH

```python
class UpdateStatusRequest(BaseModel):
    status: str = Field(..., description="New status: success/process/fail")
```

Moves into path parameter style: `PATCH /knowledge_file/{file_id}` with body `{status: "xxx"}`.

### Files Affected

- `app/api/v1/knowledge_file.py`: Rename `/knowledge_file/status` to `PATCH /knowledge_file/{file_id}`
- `app/api/v1/knowledge.py`: Rename `/knowledge/list/{user_id}` to `/users/{user_id}/knowledge`

---

## 3. Parallel Batch Crawling with crawl4ai

### Changes

Refactor batch crawling endpoints to use crawl4ai's native `arun_many()` with `SemaphoreDispatcher`.

**Original (串行)**:
```python
for url in request.urls:
    result = await crawl_service.crawl_and_prepare_for_storage(url)
```

**New (并发)**:
```python
dispatcher = SemaphoreDispatcher(semaphore_count=5)
results = await crawler.arun_many(urls, config=run_config, dispatcher=dispatcher)
```

### Error Handling Strategy: Partial Success

- Each URL processed independently
- Success: create knowledge_file record, index to vector/keyword DB
- Failure: log error, continue with other URLs
- Return list of per-URL status (not fail-fast)

### Reference

See `reference_code/crawl4ai-examples/dispatcher_example.py` for `SemaphoreDispatcher` usage pattern.

### Files Affected

- `app/api/v1/crawl.py`: Refactor `crawl_batch` and `crawl_batch_with_knowledge` to use `arun_many()`

---

## 4. Remove Redundant `/retrieve/simple`

### Changes

Delete `POST /api/v1/retrieve/simple` endpoint.

### Rationale

- `/api/v1/retrieve` already supports single knowledge base via `knowledge_ids: ["kb_id"]`
- No functional difference
- Reduces API surface area

### Files Affected

- `app/api/v1/retrieve.py`: Remove `retrieve_simple` endpoint and `RetrieveSimpleRequest` class

---

## Summary of Changes

| File | Changes |
|------|---------|
| `app/api/v1/completion.py` | Delete chat endpoints |
| `app/api/v1/knowledge_file.py` | Rename `/status` to `PATCH /{file_id}` |
| `app/api/v1/knowledge.py` | Rename `/list/{user_id}` to `/users/{user_id}/knowledge` |
| `app/api/v1/retrieve.py` | Delete `/simple` endpoint |
| `app/api/v1/crawl.py` | Parallel batch crawling |

---

## Migration Notes

- All changes are breaking changes (no backward compatibility)
- Frontend must update API calls to use new endpoint paths
- Test all affected endpoints after implementation
