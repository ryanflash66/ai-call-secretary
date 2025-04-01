#!/bin/bash
# Script to run tests for the AI Call Secretary system

# Set up colored output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AI Call Secretary Test Runner ===${NC}"
echo -e "${BLUE}====================================${NC}"

# Check if virtual environment exists, create if not
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv .venv
    source .venv/bin/activate
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
    pip install pytest pytest-asyncio pytest-cov pytest-xvfb playwright
    playwright install chromium
else
    source .venv/bin/activate
fi

# Function to run tests and report
run_tests() {
    local test_type=$1
    local test_path=$2
    local extra_args=$3
    
    echo -e "${BLUE}Running ${test_type} tests...${NC}"
    
    if [ "$test_type" = "UI" ]; then
        # Start the application server in the background for UI tests
        echo -e "${YELLOW}Starting application server for UI tests...${NC}"
        python -m src.app --port 8080 &
        APP_PID=$!
        
        # Give the server time to start
        sleep 5
    fi
    
    # Run the tests
    pytest $test_path -v $extra_args
    TEST_EXIT_CODE=$?
    
    if [ "$test_type" = "UI" ]; then
        # Shutdown the server
        echo -e "${YELLOW}Stopping application server...${NC}"
        kill $APP_PID
    fi
    
    if [ $TEST_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✓ ${test_type} tests passed!${NC}"
    else
        echo -e "${RED}✗ ${test_type} tests failed!${NC}"
        FAILURE=1
    fi
    
    echo ""
}

# Default to running all tests
TEST_TYPE=${1:-"all"}
FAILURE=0

case $TEST_TYPE in
    "unit")
        run_tests "Unit" "tests/test_*.py" ""
        ;;
    "integration")
        run_tests "Integration" "tests/integration" "-m integration"
        ;;
    "e2e")
        run_tests "End-to-End" "tests/end_to_end" "-m e2e"
        ;;
    "ui")
        run_tests "UI" "tests/ui" "-m ui"
        ;;
    "coverage")
        echo -e "${BLUE}Running tests with coverage...${NC}"
        
        # Run all tests with coverage
        pytest tests/ --cov=src --cov-report=term --cov-report=html -v
        TEST_EXIT_CODE=$?
        
        if [ $TEST_EXIT_CODE -eq 0 ]; then
            echo -e "${GREEN}✓ All tests passed with coverage!${NC}"
            echo -e "${YELLOW}Coverage report available in htmlcov/index.html${NC}"
        else
            echo -e "${RED}✗ Tests failed during coverage run!${NC}"
            FAILURE=1
        fi
        ;;
    "all")
        # Run all test types in sequence
        run_tests "Unit" "tests/test_*.py" ""
        run_tests "Integration" "tests/integration" "-m integration"
        run_tests "End-to-End" "tests/end_to_end" "-m e2e"
        run_tests "UI" "tests/ui" "-m ui"
        ;;
    *)
        echo -e "${RED}Unknown test type: ${TEST_TYPE}${NC}"
        echo "Usage: ./run_tests.sh [unit|integration|e2e|ui|coverage|all]"
        exit 1
        ;;
esac

# Report overall status
if [ $FAILURE -eq 0 ]; then
    echo -e "${GREEN}All tests completed successfully!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi