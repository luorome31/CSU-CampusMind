# Backend Commands (Tmux-Based)

All backend commands should run in tmux for agent observation.

## Install Dependencies

```bash
tmux new-session -d -s campusmind-backend-sync 'cd /home/luorome/software/CampusMind/backend && uv sync'
tmux attach -t campusmind-backend-sync
```

## Start Backend Server

```bash
tmux new-session -d -s campusmind-server 'cd /home/luorome/software/CampusMind/backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000'
tmux attach -t campusmind-server
```

## Run Tests

```bash
# Run all tests
tmux new-session -d -s campusmind-tests 'cd /home/luorome/software/CampusMind/backend && uv run pytest --tb=short -v'
tmux attach -t campusmind-tests

# Run API tests only
tmux new-session -d -s campusmind-tests-api 'cd /home/luorome/software/CampusMind/backend && uv run pytest tests/api/ -v'
tmux attach -t campusmind-tests-api

# Run tests excluding e2e
tmux new-session -d -s campusmind-tests-unit 'cd /home/luorome/software/CampusMind/backend && uv run pytest -m "not e2e"'
tmux attach -t campusmind-tests-unit

# Run specific test
tmux new-session -d -s campusmind-test-specific 'cd /home/luorome/software/CampusMind/backend && uv run pytest -k "test_name"'
tmux attach -t campusmind-test-specific
```

## Tmux Commands

```bash
tmux ls                          # List all tmux sessions
tmux attach -t <session-name>    # Attach to a session
tmux kill-session -t <name>      # Kill a session
```

**Backend server URL:** http://localhost:8000
