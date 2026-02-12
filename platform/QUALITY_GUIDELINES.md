# Code Quality Guidelines for ALGORITHMIC ARTS Platform

## Python Code Quality

### Type Safety
- All functions must have type hints
- Use `mypy` with strict mode (`strict = true`)
- Return types must be explicitly specified
- Use `TypedDict` for complex dictionary structures

### Code Style
- Follow PEP 8 guidelines
- Use `black` for code formatting (88 character line length)
- Use `isort` for import sorting
- Use `flake8` for style enforcement

### Security
- Use `bandit` for security vulnerability scanning
- Avoid hardcoded secrets
- Validate all user input
- Use parameterized queries for database operations

## TypeScript/Next.js Code Quality

### Type Safety
- Use strict TypeScript mode (`"strict": true`)
- Enable all strict options in tsconfig.json
- Use explicit return types for functions
- Avoid `any` type - use `unknown` instead

### Code Style
- Follow ESLint rules with `@typescript-eslint/strict`
- Use `import/order` for consistent import ordering
- Use `unused-imports` to detect unused imports
- Follow Next.js best practices

## Pre-commit Hooks

The following checks run automatically before commits:
1. Code formatting (black, isort)
2. Type checking (mypy, TypeScript compiler)
3. Style checking (flake8, ESLint)
4. Security scanning (bandit)
5. Commit message validation (Conventional Commits)

## Running Quality Checks

```bash
# Run all linting checks
make lint

# Run full quality check (linting + type checking)
make check

# Run pre-commit hooks manually
pre-commit run --all-files
```

## Common Issues and Fixes

### Missing Type Hints
**Issue**: `error: Function is missing a return type annotation`
**Fix**: Add explicit return type: `def function() -> ReturnType:`

### CORS Security
**Issue**: `allow_origins=["*"]` in production
**Fix**: Restrict to known origins: `allow_origins=["https://platform.algorithmic-arts.ru"]`

### Unused Imports
**Issue**: `error: Unused import 'module'`
**Fix**: Remove unused imports or use `# noqa` if necessary

### Security Vulnerabilities
**Issue**: `B106: Hardcoded password string`
**Fix**: Use environment variables for secrets