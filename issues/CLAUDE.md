# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an ERG Zone Calculator application that calculates training zones for heart rate and pace in rowing/ergometer workouts. The project consists of:

1. **FastAPI Application** (`app/`) - REST API with endpoints for HR and pace zone calculations
2. **Infrastructure** (`infra/`) - AWS CDK infrastructure as code for deployment

## Architecture

### Application Structure (`app/`)
- `src/api/` - FastAPI application and API models
- `src/domain/` - Core business logic with domain models, calculators, formatters, and configurations
- `tests/` - Comprehensive test suite

### Key Components
- **Zone Calculators**: `HRZoneCalculator` and `PaceZoneCalculator` for computing training zones
- **Domain Models**: `Zone`, `HRBenchmark`, `PaceBenchmark` classes with validation
- **Formatters**: `HRFormatter` and `PaceFormatter` for presenting results
- **Configuration**: `ZoneConfig` for loading zone definitions from files

### Infrastructure Structure (`infra/`)
- Uses AWS CDK with Python
- Separate pyproject.toml for infrastructure dependencies
- Constructs in `src/constructs/` directory

## Development Commands

### Application Development
```bash
# Install dependencies (root project)
uv sync

# Run the FastAPI application locally
cd app && uv run uvicorn src.api.app:app --reload

# Run tests
cd app && uv run pytest

# Run tests with coverage
cd app && uv run pytest --cov
```

### Infrastructure Development
```bash
# Set up infrastructure environment
cd infra && uv sync

# Synthesize CloudFormation templates
cd infra && uv run cdk synth

# Deploy infrastructure
cd infra && uv run cdk deploy

# View CDK diffs
cd infra && uv run cdk diff

# List all CDK stacks
cd infra && uv run cdk ls
```

## Project Dependencies

### Application Dependencies
- FastAPI for REST API
- Pydantic for data validation
- Uvicorn for ASGI server
- Mangum for AWS Lambda integration
- pytest for testing

### Infrastructure Dependencies
- aws-cdk-lib for CDK constructs
- constructs library

## Code Organization Patterns

- Domain models use dataclasses with validation in `__post_init__`
- Calculators follow a consistent pattern with `calculate_all_lower_bounds` and `calculate_all_upper_bounds` methods
- Formatters provide `format_value` and `format_zone_bounds` methods
- Configuration loading uses file paths for zone definitions
- API endpoints follow RESTful patterns with proper error handling

## Testing

Tests are organized by component:
- `test_domain_models.py` - Domain model validation
- `test_zone_calculators.py` - Calculator logic
- `test_zone_formatters.py` - Formatting output
- `test_zone_configs.py` - Configuration loading
- `test_api_integration.py` - API endpoint testing
- `test_models.py` - API model validation

Run tests from the `app/` directory using `uv run pytest`.