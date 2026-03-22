# Git Hooks (Lefthook)

This project uses [lefthook](https://github.com/evilmartians/lefthook) for local Git hooks.

## Hook Configuration

Hooks are configured in `lefthook.yml` at project root.

| Hook | Trigger | Actions |
|------|---------|---------|
| `pre-commit` | `git commit` | backend: `ruff check` / frontend: `npm run build` |
| `pre-push` | `git push` | backend: `uv run pytest -m "not e2e"` / frontend: `npm run test:run` |
| `pre-merge` | `git merge` | backend: `uv run pytest -m "not e2e"` / frontend: `npm run test:run` |
| `pre-rebase` | `git rebase` | backend: `uv run pytest -m "not e2e"` / frontend: `npm run test:run` |

## Behavior

- Hooks run in parallel when possible
- `pre-commit` only checks staged files (skips if none)
- Install hooks: `cd frontend && npm run prepare -- --force`

## Troubleshooting

If hooks don't run:
1. Ensure lefthook is installed: `npm install -g lefthook`
2. Reinstall hooks: `npx lefthook install`
3. Check lefthook.yml syntax is valid YAML
