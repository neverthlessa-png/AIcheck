# Git Commit Rules

Rules for Git commits in the AI Check project.

## Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | feat(detector): add AI-generated image detector |
| `fix` | Bug fix | fix(pipeline): resolve memory leak in batch processing |
| `docs` | Documentation | docs(api): add docstrings for DetectorBase |
| `style` | Code style | style: format code with black |
| `refactor` | Refactoring | refactor(core): simplify pipeline logic |
| `test` | Tests | test(forgery): add tests for PSDetector |
| `chore` | Maintenance | chore(deps): update dependencies |
| `perf` | Performance | perf(batch): optimize parallel processing |

## Scopes

| Scope | Description |
|-------|-------------|
| `core` | Core modules (pipeline, registry, task manager) |
| `detector` | Detector implementations |
| `forgery` | Forgery detection module |
| `duplicate` | Duplicate detection module |
| `document` | Document detection module |
| `gui` | GUI components |
| `storage` | Database, cache, vector index |
| `config` | Configuration |
| `utils` | Utility functions |
| `deps` | Dependencies |
| `build` | Build/packaging |

## Subject Rules

1. Use imperative mood: "add" not "added" or "adds"
2. Don't capitalize first letter
3. No period at the end
4. Maximum 50 characters

## Body Rules

1. Separate from subject with blank line
2. Explain WHAT and WHY, not HOW
3. Use imperative mood
4. Wrap at 72 characters

## Footer

1. Reference issues: `Closes #123` or `Fixes #456`
2. Breaking changes: `BREAKING CHANGE: description`

## Examples

### Simple Commit

```
feat(detector): add copy-move forgery detector
```

### Commit with Body

```
fix(pipeline): resolve race condition in parallel processing

When multiple threads accessed the shared result list simultaneously,
it caused data corruption. Fixed by using a thread-safe queue for
collecting results.

Fixes #456
```

### Breaking Change

```
refactor(core)!: change DetectorBase.detect signature

BREAKING CHANGE: The detect method now returns DetectionResult
instead of dict. Update all detector implementations.

Closes #789
```

### Multiple Issues

```
feat(gui): add batch processing progress dialog

- Show real-time progress bar
- Display current file being processed
- Allow cancellation

Closes #123, #456
```

## Branch Naming

| Pattern | Example |
|---------|---------|
| Feature | `feature/add-ai-detector` |
| Fix | `fix/memory-leak` |
| Refactor | `refactor/pipeline` |
| Docs | `docs/api-reference` |
| Test | `test/detector-tests` |

## PR Title

PR title should follow the same format as commit messages:

```
feat(detector): add AI-generated image detector
```

## What NOT to Do

```bash
# Bad ✗
git commit -m "fixed stuff"
git commit -m "WIP"
git commit -m "asdfasdf"

# Good ✓
git commit -m "fix(pipeline): resolve memory leak in batch processing"
```
