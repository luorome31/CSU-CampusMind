# API Refactor Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor CampusMind backend API to eliminate redundant endpoints, improve REST naming consistency, and optimize batch crawling with parallel execution.

**Architecture:** 4 independent refactoring tasks that can be executed in any order. Each task modifies a specific API router file without affecting others.

**Tech Stack:** FastAPI, crawl4ai (AsyncWebCrawler, SemaphoreDispatcher), asyncio.gather

---

## Chunk 1: Delete Chat Endpoints

**Files:**
- Modify: `app/api/v1/completion.py:439-559`

- [ ] **Step 1: Review current chat endpoint implementations**

Read `app/api/v1/completion.py` lines 439-559 to confirm exact code to remove:
- `ChatRequest` class (lines 439-446)
- `@router.post("/chat/stream")` endpoint (lines 449-488)
- `@router.post("/chat")` endpoint (lines 491-559)

- [ ] **Step 2: Remove ChatRequest class**

Delete lines 439-446:
```python
class ChatRequest(BaseModel):
    """Simple chat request"""
    query: str = Field(..., description="User query")
    knowledge_id: str = Field(..., description="Single knowledge base ID")
    dialog_id: Optional[str] = Field(default=None, description="Dialog ID")
    user_id: str = Field(default="system", description="User ID")
    use_rag: bool = Field(default=True, description="Use RAG")
    model: str = Field(default=settings.openai_model, description="LLM model to use")
```

- [ ] **Step 3: Remove /chat/stream endpoint**

Delete lines 449-488:
```python
@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db_session),
):
    """..."""
    # (entire function body)
```

- [ ] **Step 4: Remove /chat endpoint**

Delete lines 491-559:
```python
@router.post("/chat", response_model=CompletionResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db_session),
):
    """..."""
    # (entire function body)
```

- [ ] **Step 5: Verify the file still imports correctly**

Run: `python -c "from app.api.v1.completion import router; print('OK')"`
Expected: No import errors

- [ ] **Step 6: Commit**

```bash
git add app/api/v1/completion.py
git commit -m "refactor(api): remove redundant chat endpoints"
```

---

## Chunk 2: Rename /knowledge_file/status to PATCH /knowledge_file/{file_id}

**Files:**
- Modify: `app/api/v1/knowledge_file.py`

- [ ] **Step 1: Review current status endpoint**

Read `app/api/v1/knowledge_file.py` lines 36-82 to confirm:
- `UpdateStatusRequest` class (lines 36-39)
- `@router.post("/knowledge_file/status")` endpoint (lines 76-82)

- [ ] **Step 2: Change route decorator from POST to PATCH and update path**

Change line 76:
```python
# Before
@router.post("/knowledge_file/status")

# After
@router.patch("/knowledge_file/{file_id}")
```

- [ ] **Step 3: Update endpoint function signature and remove UpdateStatusRequest usage**

Change lines 77-82 to:
```python
async def update_knowledge_file_status(
    file_id: str,
    request: UpdateStatusRequest,
):
    """Update file processing status"""
    success = KnowledgeFileService.update_file_status(file_id, request.status)
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge file not found")
    return {"success": True}
```

- [ ] **Step 4: Verify OpenAPI schema is correct**

Run: `python -c "from app.api.v1.knowledge_file import router; print([r.path for r in router.routes])"`
Expected: Shows `/knowledge_file/{file_id}` with PATCH method

- [ ] **Step 5: Commit**

```bash
git add app/api/v1/knowledge_file.py
git commit -m "refactor(api): rename /knowledge_file/status to PATCH /knowledge_file/{file_id}"
```

---

## Chunk 3: Rename knowledge list endpoints for REST consistency

**Files:**
- Modify: `app/api/v1/knowledge.py` - Rename `/knowledge/list/{user_id}` to `/users/{user_id}/knowledge`
- Modify: `app/api/v1/knowledge_file.py` - Rename `/knowledge_file/list/{knowledge_id}` to `/knowledge/{knowledge_id}/files`

- [ ] **Step 1: Review knowledge list endpoint**

Read `app/api/v1/knowledge.py` lines 56-60:
```python
@router.get("/knowledge/list/{user_id}", response_model=List[KnowledgeResponse])
async def list_knowledge(user_id: str):
```

- [ ] **Step 2: Rename knowledge list endpoint to /users/{user_id}/knowledge**

Change lines 56-60 to:
```python
@router.get("/users/{user_id}/knowledge", response_model=List[KnowledgeResponse])
async def list_user_knowledge(user_id: str):
    """List all knowledge bases for a user"""
    knowledge_list = KnowledgeService.list_knowledge_by_user(user_id)
    return [KnowledgeResponse(**k.to_dict()) for k in knowledge_list]
```

Note: Function renamed to `list_user_knowledge` to avoid confusion with generic `list_knowledge`.

- [ ] **Step 3: Review knowledge_file list endpoint**

Read `app/api/v1/knowledge_file.py` lines 69-73:
```python
@router.get("/knowledge_file/list/{knowledge_id}", response_model=List[KnowledgeFileResponse])
async def list_knowledge_files(knowledge_id: str):
```

- [ ] **Step 4: Rename knowledge_file list endpoint to /knowledge/{knowledge_id}/files**

Change lines 69-73 to:
```python
@router.get("/knowledge/{knowledge_id}/files", response_model=List[KnowledgeFileResponse])
async def list_knowledge_files(knowledge_id: str):
    """List all files in a knowledge base"""
    files = KnowledgeFileService.list_knowledge_files(knowledge_id)
    return [KnowledgeFileResponse(**f.to_dict()) for f in files]
```

- [ ] **Step 5: Verify routes are correct**

Run: `python -c "from app.api.v1.knowledge import router as kr; from app.api.v1.knowledge_file import router as kfr; print('knowledge:', [r.path for r in kr.routes]); print('knowledge_file:', [r.path for r in kfr.routes])"`
Expected: Shows `/users/{user_id}/knowledge` and `/knowledge/{knowledge_id}/files`

- [ ] **Step 6: Commit**

```bash
git add app/api/v1/knowledge.py app/api/v1/knowledge_file.py
git commit -m "refactor(api): rename list endpoints to RESTful paths"
```

---

## Chunk 4: Remove /retrieve/simple endpoint

**Files:**
- Modify: `app/api/v1/retrieve.py`

- [ ] **Step 1: Review simple endpoint**

Read `app/api/v1/retrieve.py` lines 66-97 to confirm:
- `RetrieveSimpleRequest` class (lines 66-70)
- `@router.post("/retrieve/simple")` endpoint (lines 73-97)

- [ ] **Step 2: Remove RetrieveSimpleRequest class**

Delete lines 66-70:
```python
class RetrieveSimpleRequest(BaseModel):
    """Simple request for retrieval (single knowledge base)"""
    query: str = Field(..., description="User query")
    knowledge_id: str = Field(..., description="Single knowledge base ID")
    top_k: int = Field(default=5, description="Number of results")
```

- [ ] **Step 3: Remove /retrieve/simple endpoint**

Delete lines 73-97:
```python
@router.post("/retrieve/simple", response_model=RetrieveResponse)
async def retrieve_simple(
    request: RetrieveSimpleRequest,
):
    """..."""
    # (entire function body)
```

- [ ] **Step 4: Verify remaining routes**

Run: `python -c "from app.api.v1.retrieve import router; print([r.path for r in router.routes])"`
Expected: Only shows `/retrieve`

- [ ] **Step 5: Commit**

```bash
git add app/api/v1/retrieve.py
git commit -m "refactor(api): remove redundant /retrieve/simple endpoint"
```

---

## Chunk 5: Parallel Batch Crawling with crawl4ai

**Files:**
- Modify: `app/api/v1/crawl.py`
- Reference: `reference_code/crawl4ai-examples/dispatcher_example.py`

- [ ] **Step 1: Review current batch implementation**

Read `app/api/v1/crawl.py` lines 160-267 to understand:
- `crawl_batch` endpoint (lines 160-195)
- `crawl_batch_with_knowledge` endpoint (lines 198-267)
- Current loop-based serial processing

- [ ] **Step 2: Review dispatcher_example.py for SemaphoreDispatcher pattern**

Read `reference_code/crawl4ai-examples/dispatcher_example.py` lines 58-72:
```python
async def semaphore(urls, browser_config, run_config):
    """Basic semaphore crawler"""
    start = time.perf_counter()
    async with AsyncWebCrawler(config=browser_config) as crawler:
        dispatcher = SemaphoreDispatcher(
            semaphore_count=5,
            monitor=CrawlerMonitor(
                max_visible_rows=15, display_mode=DisplayMode.DETAILED
            ),
        )
        results = await crawler.arun_many(
            urls, config=run_config, dispatcher=dispatcher
        )
    duration = time.perf_counter() - start
    return len(results), duration
```

Note: `CrawlerMonitor` is optional for production; focus on `SemaphoreDispatcher`.

- [ ] **Step 3: Import SemaphoreDispatcher**

Add to imports in `app/api/v1/crawl.py`:
```python
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
    SemaphoreDispatcher,  # Add this
)
```

- [ ] **Step 4: Refactor crawl_batch to use arun_many with SemaphoreDispatcher**

Replace the `crawl_batch` function body (lines 160-195) with:

```python
@router.post("/crawl/batch", response_model=List[CrawlResponse])
async def crawl_batch(
    request: CrawlBatchRequest,
):
    """
    Crawl multiple URLs concurrently using SemaphoreDispatcher

    Returns per-URL status with partial success handling.
    """
    try:
        browser_config = BrowserConfig(headless=True, verbose=False)
        run_config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter()
            ),
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            dispatcher = SemaphoreDispatcher(semaphore_count=5)
            results = await crawler.arun_many(
                urls=request.urls,
                config=run_config,
                dispatcher=dispatcher,
            )

        responses = []
        for i, result in enumerate(results):
            url = request.urls[i]
            if result.success:
                # Store to OSS if requested
                oss_url = None
                if request.store_to_oss:
                    storage_key = crawl_service.generate_storage_key(url)
                    content = result.markdown.raw_markdown.encode("utf-8")
                    oss_url = storage_client.upload_content(storage_key, content)

                responses.append(CrawlResponse(
                    success=True,
                    url=url,
                    oss_url=oss_url,
                    title=result.metadata.get("title", "") if result.metadata else "",
                ))
            else:
                responses.append(CrawlResponse(
                    success=False,
                    url=url,
                    error=result.error_message or "Unknown error",
                ))

        return responses

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

- [ ] **Step 5: Refactor crawl_batch_with_knowledge to use arun_many**

Replace the `crawl_batch_with_knowledge` function body (lines 198-267) with:

```python
@router.post("/crawl/batch-with-knowledge", response_model=List[CrawlResponse])
async def crawl_batch_with_knowledge(
    request: CrawlBatchWithKnowledgeRequest,
):
    """
    Crawl multiple URLs and create knowledge_file records for each

    End-to-end flow for multiple URLs: crawl -> OSS -> knowledge_file -> index
    Uses parallel crawling with SemaphoreDispatcher for performance.
    """
    from app.services.rag.indexer import indexer

    try:
        browser_config = BrowserConfig(headless=True, verbose=False)
        run_config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter()
            ),
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            dispatcher = SemaphoreDispatcher(semaphore_count=5)
            results = await crawler.arun_many(
                urls=request.urls,
                config=run_config,
                dispatcher=dispatcher,
            )

        responses = []
        for i, result in enumerate(results):
            url = request.urls[i]

            if not result.success:
                responses.append(CrawlResponse(
                    success=False,
                    url=url,
                    error=result.error_message or "Unknown error",
                ))
                continue

            try:
                # Store to OSS
                storage_key = crawl_service.generate_storage_key(url)
                content = result.markdown.raw_markdown.encode("utf-8")
                oss_url = storage_client.upload_content(storage_key, content)

                # Create knowledge_file
                file_name = storage_key.split("/")[-1]
                knowledge_file = KnowledgeFileService.create_knowledge_file(
                    file_name=file_name,
                    knowledge_id=request.knowledge_id,
                    user_id=request.user_id,
                    oss_url=oss_url,
                    file_size=len(content),
                )

                # Index to vector/keyword DB
                index_result = await indexer.index_content(
                    content=result.markdown.raw_markdown,
                    knowledge_id=request.knowledge_id,
                    source_name=file_name,
                    metadata={
                        "file_id": knowledge_file.id,
                        "enable_vector": request.enable_vector,
                        "enable_keyword": request.enable_keyword,
                    }
                )

                # Update file status
                if index_result.get("success"):
                    KnowledgeFileService.update_file_status(knowledge_file.id, "success")
                else:
                    KnowledgeFileService.update_file_status(knowledge_file.id, "fail")

                responses.append(CrawlResponse(
                    success=True,
                    url=url,
                    oss_url=oss_url,
                    title=result.metadata.get("title", "") if result.metadata else "",
                    file_id=knowledge_file.id,
                ))

            except Exception as e:
                responses.append(CrawlResponse(
                    success=False,
                    url=url,
                    error=str(e),
                ))

        return responses

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

- [ ] **Step 6: Verify imports are correct**

Run: `python -c "from app.api.v1.crawl import router; print('OK')"`
Expected: No import errors

- [ ] **Step 7: Commit**

```bash
git add app/api/v1/crawl.py
git commit -m "feat(crawl): parallel batch crawling with SemaphoreDispatcher"
```

---

## Final Verification

- [ ] **Step 1: Run all API route tests (if exist)**

Run: `pytest tests/ -v -k "api or completion or knowledge or crawl or retrieve" 2>/dev/null || echo "No tests found or tests passed"`

- [ ] **Step 2: Verify all routes are registered correctly**

Run:
```python
python -c "
from app.main import app
for route in app.routes:
    if hasattr(route, 'path') and '/api/v1' in route.path:
        methods = getattr(route, 'methods', {'GET'})
        print(f'{list(methods)[0]:6} {route.path}')
"
```

Expected output shows all updated endpoints:
- `POST   /api/v1/completion/stream` (no chat)
- `POST   /api/v1/completion`
- `PATCH  /api/v1/knowledge_file/{file_id}`
- `GET    /api/v1/users/{user_id}/knowledge`
- `GET    /api/v1/knowledge/{knowledge_id}/files`
- `POST   /api/v1/retrieve` (no simple)
- `POST   /api/v1/crawl/batch`
- `POST   /api/v1/crawl/batch-with-knowledge`

---

## Rollback Plan (if needed)

If issues arise, revert each commit individually:
```bash
git revert <commit_hash>  # For each chunk's commit
```
