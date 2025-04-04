# AI Call Secretary

AI Call Secretary is an intelligent phone call management system that combines advanced AI with telephony to handle incoming calls, take messages, schedule appointments, and provide information to callers.

## Features

- **Automated Call Answering**: AI-powered voice assistant greets callers and handles their requests
- **Natural Conversation**: Fluid conversation with callers using advanced LLM technology
- **Call Routing**: Intelligent routing based on caller identity, time of day, and more
- **Appointment Scheduling**: Book appointments directly through phone calls
- **Message Taking**: Record detailed messages for later follow-up
- **Real-time Monitoring**: Web interface for monitoring calls in real-time
- **Call Analytics**: Detailed analytics and reporting on call volume and outcomes
- **Voice Customization**: Customize the assistant's voice to match your brand
- **Security**: Enterprise-grade security with encryption and access controls

## Architecture

The system consists of several components:

- **API Service**: FastAPI backend serving the web interface and managing system state
- **Telephony Service**: Handles phone call interactions using FreeSwitch
- **LLM Integration**: Connects to local or cloud LLM services for natural language understanding
- **Voice Processing**: Speech-to-text and text-to-speech capabilities
- **Web Interface**: React-based dashboard for monitoring and configuration
- **Database**: Stores call records, appointments, messages, and system configuration

For detailed architecture information, see [Architecture Documentation](docs/architecture.md).

## Requirements

- Python 3.10+
- Docker and Docker Compose (for production deployment)
- FreeSwitch for telephony integration
- LLM provider (local Ollama server or cloud service)
- Redis (for production caching and session management)
- 4GB+ RAM, 2+ CPU cores recommended

## Quick Start

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-call-secretary.git
   cd ai-call-secretary
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy example configuration:
   ```bash
   cp .env.example .env
   ```

5. Run the development server:
   ```bash
   python -m src.main --debug
   ```

### Production Deployment

For production deployment, we recommend using Docker Compose:

```bash
# Generate strong secrets first
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -hex 16)

# Update .env file with these secrets
# Then run:
docker-compose up -d
```

See [Deployment Guide](docs/deployment.md) for complete instructions.

## Security

The system implements multiple layers of security:

- JWT-based authentication
- Role-based access control
- Data encryption at rest
- HTTPS for all communications
- Input validation and sanitization
- Audit logging
- Intrusion detection

For detailed security information, see [Security Documentation](docs/security.md).

## Documentation

- [Setup Guide](docs/setup_guide.md)
- [Architecture](docs/architecture.md)
- [Security](docs/security.md)
- [Deployment](docs/deployment.md)
- [Contributing](docs/contributing.md)

## Development Guide

### Project Structure

- `src/` - Main source code
  - `api/` - FastAPI routes and schemas
  - `llm/` - Language model integration
  - `telephony/` - Call handling and routing
  - `voice/` - Speech processing components
  - `workflow/` - Conversation flow management
- `tests/` - Test suite
- `web/` - Web dashboard
- `config/` - Configuration files
- `scripts/` - Utility scripts

### Running Tests

We use a Makefile to standardize testing:

```bash
# Run all tests
make test

# Run specific module tests
make test-llm
make test-voice
make test-telephony
make test-workflow

# Run with coverage
make test-coverage
```

### Code Quality

Maintain code quality with:

```bash
# Format code
make format

# Lint code
make lint

# Check file encoding
make check-encoding

# Fix file encoding issues
make fix-encoding
```

### Encoding Issues

If you encounter file encoding issues, use the provided script:

```bash
python scripts/fix_encoding.py src
```

This script will detect and fix UTF-16 encoded files by converting them to UTF-8.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FreeSwitch for telephony capabilities
- FastAPI for the high-performance API framework
- Mistral AI for LLM capabilities
- Chart.js for analytics visualizations