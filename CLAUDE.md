# AGENTS Governance

This repository uses `.agents/AGENTS.md` as the authoritative runtime workflow entry.

## Branching
- Default collaboration branches: `main` and `dev`.
- Keep regular development off `main`.

## Commits
- Use Angular/Conventional Commit format: `type(scope): subject`.
- Allowed types: feat, fix, docs, style, refactor, test, chore, build, ci, perf, revert.

## Commenting and Documentation
- English is the default language for code comments and docs unless explicitly requested.
- Use concise Doxygen-style comments for public APIs where applicable.

## Architecture
- Prefer high cohesion and low coupling.
- Keep rule sources centralized and reusable.
