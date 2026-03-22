# Backend Architecture Overview

## Tech Stack

- **Framework**: FastAPI (Python)
- **Agent**: LangGraph ReAct agent
- **Database**: SQLAlchemy ORM (SQLite dev, PostgreSQL prod)
- **Cache**: Redis for session management
- **Vector Search**: Elasticsearch for RAG retrieval
- **Embedding**: OpenAI embeddings

## Directory Structure

```
backend/
├── app/
│   ├── api/v1/              # API routers
│   │   ├── auth/            # Authentication endpoints
│   │   ├── completion/      # Chat completion (stream + non-stream)
│   │   ├── crawl/          # Web crawling
│   │   ├── knowledge/      # Knowledge base CRUD
│   │   └── index/          # RAG indexing
│   ├── core/
│   │   ├── agents/         # ReAct agent implementation
│   │   ├── session/        # Session management & CAS login
│   │   └── tools/          # Tool integrations (JWC, Library, Career, OA)
│   ├── services/
│   │   ├── rag/            # RAG pipeline (embedding, indexing, retrieval)
│   │   ├── knowledge/      # Knowledge base service
│   │   ├── crawl/          # Crawler service
│   │   └── dialog/         # Dialog management
│   ├── database/
│   │   └── models/         # SQLAlchemy models
│   └── schema/             # Pydantic schemas
├── tests/                  # pytest tests
└── docs/                   # Backend documentation
```

## Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | CAS login |
| `/api/v1/completion/stream` | POST | SSE streaming chat |
| `/api/v1/knowledge/{id}` | GET | Get knowledge base |
| `/api/v1/crawl/create-and-index` | POST | Crawl URL and index |
| `/api/v1/retrieve` | POST | RAG retrieval |

## Agent Tools

- **JWC Tools**: Grade lookup, schedule, exam info
- **Library Tools**: Book search, availability
- **Career Tools**: Job postings, applications
- **OA Tools**: Department info, notifications
- **RAG Tool**: Knowledge base retrieval

## Session Management

- Redis-based session caching
- CAS (Central Authentication Service) integration
- Rate limiting per user

## For Detailed Backend Docs

See `backend/docs/` directory:
- `auth/` - Authentication flow
- `api/` - API endpoint details
- `tools/` - Tool integrations
- `rag/` - RAG pipeline docs
