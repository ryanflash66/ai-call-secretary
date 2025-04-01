# Contributing to AI Call Secretary

Thank you for your interest in contributing to the AI Call Secretary project!

## Development Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. For development-specific dependencies:
   ```bash
   pip install -r tests/requirements-test.txt
   ```

## CI/CD Pipeline

Our CI/CD pipeline runs on GitHub Actions and performs the following steps:

1. **Check Encoding**: Verifies that all source files are properly encoded as UTF-8
2. **Lint**: Runs flake8, mypy, black, and isort checks
3. **Test**: Runs pytest with coverage reporting

### Requirements for CI

For CI to pass, we use a dedicated `requirements-ci.txt` file that includes only the necessary dependencies for testing. This helps avoid compilation issues on the CI servers.

If you add new dependencies to the project:
1. Add them to `requirements.txt` for local development
2. If needed for testing, add them to `requirements-ci.txt` as well

### Troubleshooting CI Failures

Common CI issues:
- **Compilation errors**: Make sure any C-extension dependencies work on Ubuntu Linux
- **Encoding issues**: Ensure files are saved as UTF-8 without BOM
- **Dependency conflicts**: Test your changes with a fresh virtual environment

## Pull Request Process

1. Create a branch from `main`
2. Make your changes
3. Run tests locally: `pytest tests/`
4. Run linting: `flake8 src/ tests/` and `black src/ tests/`
5. Create a pull request with a clear description
6. Wait for CI checks to pass
7. Address any review comments

## Code Style

We follow PEP 8 for Python code style. Use the provided linting tools to ensure your code meets our standards.