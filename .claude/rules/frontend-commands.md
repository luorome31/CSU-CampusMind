# Frontend Commands (Tmux-Based)

All frontend commands should run in tmux for agent observation.

## Development Server

```bash
# Start dev server in tmux
tmux new-session -d -s campusmind-frontend 'cd /home/luorome/software/CampusMind/frontend && npm run dev'
tmux attach -t campusmind-frontend  # Attach to view logs
```

## Install Dependencies

```bash
tmux new-session -d -s campusmind-frontend-install 'cd /home/luorome/software/CampusMind/frontend && npm install'
tmux attach -t campusmind-frontend-install
```

## Build

```bash
tmux new-session -d -s campusmind-frontend-build 'cd /home/luorome/software/CampusMind/frontend && npm run build'
tmux attach -t campusmind-frontend-build
```

## Testing

```bash
# Run tests in watch mode
tmux new-session -d -s campusmind-frontend-test 'cd /home/luorome/software/CampusMind/frontend && npm run test'
tmux attach -t campusmind-frontend-test

# Run tests once
tmux new-session -d -s campusmind-frontend-test-run 'cd /home/luorome/software/CampusMind/frontend && npm run test:run'
tmux attach -t campusmind-frontend-test-run

# Run tests with coverage
tmux new-session -d -s campusmind-frontend-coverage 'cd /home/luorome/software/CampusMind/frontend && npm run test:coverage'
tmux attach -t campusmind-frontend-coverage
```

## Tmux Commands

```bash
tmux ls                          # List all tmux sessions
tmux attach -t <session-name>    # Attach to a session
tmux kill-session -t <name>      # Kill a session
```

**Dev server URL:** http://localhost:5173
