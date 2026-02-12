#!/bin/bash
# Setup strict linting and pre-commit hooks for ALGORITHMIC ARTS platform

set -e

echo "Setting up strict linting and pre-commit hooks..."

# Install pre-commit
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit
fi

# Install node dependencies for frontend
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Install Python dependencies for linting
echo "Installing Python linting dependencies..."
pip install mypy black isort flake8 pylint bandit darglint pydocstyle

# Set up pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install

# Create git hooks directory if it doesn't exist
mkdir -p .git/hooks

# Add commit message validation hook
cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash
# Validate commit message format (Conventional Commits)
MESSAGE=$(cat "$1")

# Check for conventional commit format: <type>(<scope>): <subject>
if ! [[ $MESSAGE =~ ^((feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]*\))?|Merge): ]]; then
    echo "Commit message must follow Conventional Commits format:"
    echo "  <type>(<scope>): <subject>"
    echo "  Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert"
    echo "  Example: feat(auth): add JWT token refresh endpoint"
    exit 1
fi

# Check for empty subject
if [[ $MESSAGE =~ ^[^:]*:$ ]]; then
    echo "Commit message must have a subject after the colon"
    exit 1
fi

exit 0
EOF

chmod +x .git/hooks/commit-msg

echo "Linting setup completed successfully!"
echo "To run all checks:"
echo "  - npm run check (frontend)"
echo "  - make lint (backend)"
echo "  - pre-commit run --all-files (run all pre-commit hooks)"