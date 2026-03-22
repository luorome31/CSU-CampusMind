# Frontend Skills and Workflows

## Required Skills for Frontend Development

### /frontend-design Skill

**MUST use** `/frontend-design` skill before any UI implementation task:

1. Invoke the skill at the start of frontend UI work
2. Follow the DFII scoring methodology
3. Use the design guidance for component styling

### Superpowers Workflow

All frontend development must follow the superpowers workflow:

1. **Brainstorming** - Use `superpowers:brainstorming` to clarify requirements
2. **Writing Plans** - Use `superpowers:writing-plans` to create implementation plan
3. **Execution** - Use `superpowers:executing-plans` to implement
4. **Code Review** - Use `superpowers:requesting-code-review` before completion

## TDD Requirement

Frontend development follows strict Test-Driven Development:

1. **Write the test first** - Define expected behavior before implementation
2. **Run test to verify failure** - Confirm test fails
3. **Implement minimum code** - Write only enough to pass
4. **Refactor if needed** - Improve while keeping tests green

```bash
npm run test:run  # Verify new test fails
# ... implement feature ...
npm run test:run  # Verify test passes
```

## When to Invoke Skills

| Task Type | Required Skill |
|-----------|----------------|
| UI/Component creation | `/frontend-design` |
| Multi-step implementation | `superpowers:brainstorming` → `superpowers:writing-plans` |
| Complex feature | `superpowers:writing-plans` |
| Bug fix | `superpowers:brainstorming` |
| Code review | `superpowers:requesting-code-review` |

## Anti-Patterns to Avoid

- Don't start implementing before reading relevant documentation
- Don't skip the brainstorming/planning phase for complex tasks
- Don't implement UI without first using `/frontend-design` skill
- Don't skip TDD workflow for new features
