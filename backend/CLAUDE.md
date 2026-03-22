# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CampusMind is an AI-powered campus assistant backend. It provides:
- **RAG (Retrieval-Augmented Generation)**: Knowledge base search with ChromaDB (vector) + Elasticsearch (keyword)
- **LangGraph ReAct Agent**: Tool-augmented AI agent for handling user queries
- **University System Integration**: CAS single sign-on for JWC (教务处), Library, ECard, and OA (办公自动化)
- **Streaming API**: SSE-based streaming responses for real-time agent interactions

## Common Commands

```bash
# Install dependencies
uv sync

# Run the backend server in tmux
tmux new-session -d -s campusmind-server 'cd /home/luorome/software/CampusMind/backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000'
tmux attach -t campusmind-server  # Attach to view logs

# Run tests in tmux
tmux new-session -d -s campusmind-tests 'cd /home/luorome/software/CampusMind/backend && uv run pytest --tb=short -v'
tmux attach -t campusmind-tests  # Attach to view logs

# Run specific tests
uv run pytest tests/ -v                                    # All tests
uv run pytest tests/api/ -v                                # API tests only
uv run pytest tests/core/tools/jwc/ -v                     # Specific test folder
uv run pytest -m "not e2e"                               # Skip e2e tests
uv run pytest -k "test_name"                              # Run specific test by name
uv run pytest --ignore=tests/core/tools/jwc/test_integration.py --ignore=tests/services/history/test_cache.py  # Skip conflicting tests

# Run with test database
DATABASE_URL=sqlite:///./test_campusmind.db uv run pytest tests/
```

## Architecture

### Key Components

**`app/api/v1/`** - FastAPI routers organized by feature:
- `completion.py` - Main streaming chat endpoint with RAG integration
- `index.py` - Offline content indexing (chunking → vector/keyword storage)
- `crawl.py` - Web scraping endpoints (crawl4ai)
- `knowledge.py`, `knowledge_file.py` - Knowledge base management
- `auth.py` - Authentication endpoints

**`app/core/agents/react_agent.py`** - LangGraph ReAct agent:
- StateGraph with `call_model` and `execute_tool` nodes
- Streams custom events for tool execution status
- Handles tool calls from LLM decisions

**`app/core/tools/`** - Tool implementations:
- `rag_tool.py` - RAG search tool
- `jwc/` - JWC (教务处) integration: grades, schedule, exam info
- `library/` - Library book search
- `career/` - Career center integration
- `oa/` - Office automation notifications

**`app/services/rag/`** - RAG pipeline:
- `handler.py` - Main orchestration
- `embedding.py` - OpenAI embeddings
- `chunker.py` - Text splitting
- `vector_db.py` - ChromaDB interface
- `es_client.py` - Elasticsearch interface
- `retrieval.py` - Hybrid retrieval (vector + keyword fusion)

**`app/core/session/`** - Session management:
- `manager.py` - UnifiedSessionManager for CAS login across subsystems
- `providers/` - Subsystem-specific session providers (JWC, Library, ECard, OA)
- `cache.py` - Redis-based caching
- `persistence.py` - Session persistence

### Database Models (SQLModel)
- `KnowledgeBase`, `KnowledgeFile` - RAG knowledge storage
- `Dialog`, `ChatHistory` - Conversation history
- `User` - User accounts
- `ToolDefinition`, `ToolCallLog` - Tool registry and logging

### Configuration
All settings via environment variables (`.env`):
- `DATABASE_URL` - SQLite (dev) or PostgreSQL (prod)
- `REDIS_URL` - Redis for caching
- `OPENAI_API_KEY` / `EMBEDDING_API_KEY` - LLM credentials
- `CHROMA_PERSIST_PATH` - Vector DB storage
- `ELASTICSEARCH_HOSTS` - Keyword search
- `CAS_USERNAME`, `CAS_PASSWORD` - University system credentials

## Testing Strategy
- `tests/api/` - API endpoint tests
- `tests/core/` - Core component tests (session, tools, agents)
- `tests/services/` - Service layer tests (RAG, storage)
- `tests/e2e/` - End-to-end integration tests

Pytest markers: `unit`, `integration`, `api`, `e2e`, `auth_required`, `public_tools`, `auth_tools`, `slow`
