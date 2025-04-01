# Makefile for AI Call Secretary

# Variables
PYTHON = python3
PYTEST = pytest
PIP = pip
SRC_DIR = src
TEST_DIR = tests
CONFIG_DIR = config
VENV_DIR = .venv
SCRIPT_DIR = scripts
COVERAGE_DIR = coverage_report

.PHONY: all setup clean test lint format check-encoding fix-encoding

# Default target
all: setup test

# Setup the development environment
setup:
	@echo "Setting up development environment..."
	$(PYTHON) -m $(PIP) install --upgrade pip
	$(PYTHON) -m $(PIP) install -r requirements.txt
	@echo "Setup complete!"

# Run code formatting
format:
	@echo "Formatting code..."
	black $(SRC_DIR) $(TEST_DIR)
	isort $(SRC_DIR) $(TEST_DIR)
	@echo "Formatting complete!"

# Run linting
lint:
	@echo "Linting code..."
	flake8 $(SRC_DIR) $(TEST_DIR)
	mypy $(SRC_DIR)
	@echo "Linting complete!"

# Check for encoding issues
check-encoding:
	@echo "Checking for encoding issues..."
	find $(SRC_DIR) -type f -name "*.py" -exec grep -l "$$(\printf '\0')" {} \; 2>/dev/null || echo "No encoding issues found."

# Fix encoding issues
fix-encoding:
	@echo "Fixing encoding issues..."
	$(PYTHON) $(SCRIPT_DIR)/fix_encoding.py $(SRC_DIR)

# Run all tests
test: 
	@echo "Running all tests..."
	PYTHONPATH=. $(PYTEST) $(TEST_DIR)

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	PYTHONPATH=. $(PYTEST) --cov=$(SRC_DIR) --cov-report=html:$(COVERAGE_DIR) $(TEST_DIR)
	@echo "Coverage report generated in $(COVERAGE_DIR)"

# Run specific test module
test-module:
	@echo "Running tests for module: $(MODULE)"
	PYTHONPATH=. $(PYTEST) $(TEST_DIR)/test_$(MODULE).py -v

# Run LLM module tests
test-llm:
	@echo "Running LLM module tests..."
	PYTHONPATH=. $(PYTEST) $(TEST_DIR)/test_llm.py -v

# Run voice module tests
test-voice:
	@echo "Running voice module tests..."
	PYTHONPATH=. $(PYTEST) $(TEST_DIR)/test_voice.py -v

# Run telephony module tests
test-telephony:
	@echo "Running telephony module tests..."
	PYTHONPATH=. $(PYTEST) $(TEST_DIR)/test_telephony.py -v

# Run workflow module tests
test-workflow:
	@echo "Running workflow module tests..."
	PYTHONPATH=. $(PYTEST) $(TEST_DIR)/test_workflow.py -v

# Clean build artifacts
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf $(COVERAGE_DIR)
	rm -rf .pytest_cache
	rm -rf .coverage
	@echo "Cleanup complete!"