# Contributing to RiskZen

Thank you for your interest in contributing to RiskZen. This document provides guidelines and information for contributors.

---

## How to Contribute

### Reporting Bugs

If you find a bug, please open a [GitHub Issue](https://github.com/ARUNAGIRINATHAN-K/riskzen-ai/issues) with:

- A clear, descriptive title.
- Steps to reproduce the issue.
- Expected behavior vs actual behavior.
- Your environment (OS, Docker version, Python version, Node version).
- Relevant logs or screenshots.

### Suggesting Features

Feature suggestions are welcome. Please open a [GitHub Issue](https://github.com/ARUNAGIRINATHAN-K/riskzen-ai/issues) with:

- A clear description of the proposed feature.
- The problem it solves or the use case it enables.
- Any relevant examples or references.

Before suggesting, please check the [PRD](docs/PRD.md) to see if the feature is already planned or explicitly out of MVP scope.

### Submitting Changes

1. **Fork** the repository.
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the coding standards below.
4. **Write or update tests** for your changes.
5. **Run the test suite** and ensure all tests pass:
   ```bash
   # Backend
   cd backend && pytest

   # Frontend
   cd frontend && npm test
   ```
6. **Commit** with a clear message:
   ```bash
   git commit -m "feat: add dependency concentration risk rule"
   ```
7. **Push** your branch and open a **Pull Request** against `main`.

---

## Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short description>

[optional body]
```

### Types

| Type | Use for |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `chore` | Build process, tooling, dependency updates |
| `style` | Formatting, whitespace (no logic change) |

### Examples

```
feat: add milestone slippage risk rule
fix: correct cycle time calculation for reopened items
docs: update API endpoint documentation
refactor: extract risk scoring into separate module
test: add integration tests for GitHub connector
chore: update FastAPI to 0.115
```

---

## Coding Standards

### Python (Backend)

- **Python 3.11+**
- **Formatter/Linter:** `ruff`
- **Type hints** on all function signatures.
- **Docstrings** on all public functions and classes.
- **Tests** for all business logic in `tests/`.

### TypeScript (Frontend)

- **TypeScript strict mode.**
- **Formatter/Linter:** `eslint` + `prettier`
- **No `any` types** unless absolutely necessary.
- **Components** use descriptive prop interfaces.

### General

- Keep functions focused and small.
- Prefer clarity over cleverness.
- Comment the *why*, not the *what*.
- All new API endpoints must have Pydantic schemas for request and response.
- All new risk rules must have unit tests with fixture data.

---

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/ARUNAGIRINATHAN-K/riskzen-ai.git
cd riskzen-ai

# Copy environment template
cp .env.example .env

# Start all services
docker compose up -d

# Backend is at http://localhost:8000
# Frontend is at http://localhost:3000
# API docs at http://localhost:8000/docs
```

---

## Project Structure

Refer to [ARCHITECTURE.md](docs/ARCHITECTURE.md) for the complete project structure and technical decisions.

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## Questions?

If you have questions about contributing, open a [Discussion](https://github.com/ARUNAGIRINATHAN-K/riskzen-ai/discussions) or reach out through GitHub Issues.
