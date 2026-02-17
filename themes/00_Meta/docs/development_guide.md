# Development Guide

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose
- Git

### Setup

```bash
git clone https://github.com/DSL-Schema-Platform.git
cd DSL-Schema-Platform
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Development Workflow

1. Create feature branch
2. Make changes
3. Run tests
4. Submit PR

## Testing

```bash
pytest
pytest --cov=.
```

## Code Quality

```bash
black .
flake8 .
mypy .
```
