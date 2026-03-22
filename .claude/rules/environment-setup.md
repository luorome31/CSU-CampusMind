# Environment Setup

## Frontend Setup

1. Copy environment file:
```bash
cp frontend/.env.example frontend/.env.local
```

2. Configure `frontend/.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

3. Install dependencies:
```bash
cd frontend
npm install
```

## Backend Setup

1. Copy environment file:
```bash
cp backend/.env.example backend/.env
```

2. Configure `backend/.env` with these variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Database connection (SQLite for dev, PostgreSQL for prod) |
| `REDIS_URL` | Redis connection URL |
| `OPENAI_API_KEY` | OpenAI API key for LLM |
| `EMBEDDING_API_KEY` | API key for embeddings |
| `CHROMA_PERSIST_PATH` | ChromaDB persistence path |
| `ELASTICSEARCH_HOSTS` | Elasticsearch hosts |
| `CAS_USERNAME` | University CAS username |
| `CAS_PASSWORD` | University CAS password |

3. Install dependencies:
```bash
cd backend
uv sync
```

## Verification

After setup, verify services:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs
