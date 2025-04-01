# CLAUDE.md - Guidelines for AI-Assisted Development

## Build & Test Commands
- **Python Backend**: `pytest tests/` (run all tests), `pytest tests/test_llm.py` (single test)
- **Lint**: `flake8 src/ tests/` (Python linting), `black src/ tests/` (code formatting)
- **Voice Training**: `python scripts/train_voice.sh` (voice cloning)

## Code Style Guidelines
- **Python**: Follow PEP 8 conventions, 4-space indentation
- **JavaScript**: 2-space indentation, semicolons, modular organization
- **Imports**: Group imports (standard lib, third-party, local), alphabetize within groups
- **Naming**: snake_case for Python variables/functions, CamelCase for classes
- **Error Handling**: Use try/except with specific exceptions, log errors appropriately
- **Documentation**: Docstrings for Python modules/functions (''' triple quotes ''')
- **Testing**: Pytest for Python, maintain test fixtures in tests/fixtures/

## Project Structure 
- Modular architecture with separation of concerns (API, LLM, telephony, voice)
- Configuration via YAML files in config/ directory
- Web interface using standard HTML/CSS/JS

## Implementation Plan

### Phase 1: Core Infrastructure
1. **Telephony Setup**
   - Complete FreeSwitch configuration in `src/telephony/freeswitch/`
   - Implement call handler (`src/telephony/call_handler.py`)
   - Set up SIP trunk connections

2. **Voice Processing Pipeline**
   - Finalize STT implementation with Whisper (`src/voice/stt.py`)
   - Complete TTS with Sesame CSM (`src/voice/tts.py`)
   - Test voice cloning capabilities (`scripts/train_voice.sh`)

### Phase 2: Intelligence Layer
1. **LLM Integration**
   - Finish Ollama client implementation (`src/llm/ollama_client.py`)
   - Develop context manager for conversation state (`src/llm/context.py`)
   - Create domain-specific prompts (`src/llm/prompts.py`)

2. **Workflow Engine**
   - Implement action handlers (`src/workflow/actions.py`)
   - Create conversation flows (`src/workflow/flows/`)
   - Add decision logic for call routing

### Phase 3: User Interface & Deployment
1. **Web Dashboard**
   - Develop call monitoring interface (`web/index.html`, `web/js/main.js`)
   - Add configuration management
   - Implement call history and analytics

2. **Production Readiness**
   - Complete Docker configuration (`docker-compose.yml`)
   - Add security hardening
   - Write deployment documentation