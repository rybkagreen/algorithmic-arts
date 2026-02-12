# Contributing to ALGORITHMIC ARTS Platform

## Code Quality and Linting

We enforce strict code quality standards to ensure maintainability and security.

### Python Linting
- **mypy**: Strict type checking with `strict = true` configuration
- **black**: Code formatting with 88 character line length
- **isort**: Import sorting with black profile
- **flake8**: Style guide enforcement
- **bandit**: Security vulnerability scanning
- **pylint**: Comprehensive code analysis

### TypeScript/Next.js Linting
- **ESLint**: Strict rules with TypeScript plugin
- **TypeScript compiler**: Strict mode enabled (`strict: true`)
- **unused-imports**: Automatic detection of unused imports
- **import/order**: Strict import ordering

### Pre-commit Hooks
We use `pre-commit` to automatically run checks before commits:
- Code formatting (black, isort)
- Type checking (mypy)
- Style checking (flake8, ESLint)
- Security scanning (bandit)
- JSON/YAML/TOML validation
- Commit message validation (Conventional Commits)

## Setup Instructions

1. Install pre-commit: `pip install pre-commit`
2. Install frontend dependencies: `cd frontend && npm install`
3. Setup linting: `make setup-linting`
4. Run all checks: `make check`

## Commit Message Guidelines

Use Conventional Commits format:
```
<type>(<scope>): <subject>

<body>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

Example: `feat(auth): add JWT token refresh endpoint`

## Running Checks

- `make lint`: Run all linting checks
- `make check`: Run linting + type checking
- `pre-commit run --all-files`: Run all pre-commit hooks manually
- `npm run check` (frontend): Run frontend checks