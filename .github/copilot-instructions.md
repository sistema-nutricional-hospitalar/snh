# SNH - Sistema Nutricional Hospitalar - AI Coding Agent Instructions

## Project Overview
**SNH** is a FastAPI-based hospital nutrition management system designed to optimize diet prescription workflows for hospital patients. It handles patient tracking, diet management, and multi-channel notifications.

**Tech Stack**: Python 3.11+, FastAPI, SQLAlchemy ORM, SQLite

## Architecture

### Core Layers
1. **Controllers** (`src/snh_project/controllers/`) - HTTP request handlers (report_controller.py)
2. **Core Domain** (`src/snh_project/core/`) - Business logic entities:
   - `diet.py` - Diet classes (`DietaOral`, `DietaEnteral`, `ItemCardapio`)
   - `patient.py` - Patient entities (`Paciente`, `SetorClinico`)
   - `prescription.py` - Prescription management
   - `base.py` - Base abstractions (`AuditoriaMixin`, `Dieta` ABC)
3. **Services** (`src/snh_project/services/`) - Cross-cutting concerns:
   - `factory.py` - `DietaFactory` for diet instantiation pattern
   - `strategies.py` - Strategy pattern for notifications (`EstrategiaNotificacao`, `NotificacaoPush`, `NotificacaoEmail`)
   - `notifier.py` - `NotificadorService` orchestrates multi-channel notifications
4. **Models** (`src/snh_project/models/`) - Data models (`Paciente` ORM, `Notificacao`)
5. **Database** (`database.py`) - SQLAlchemy setup with SQLite backend

### Key Design Patterns
- **Strategy Pattern**: Notification strategies in `services/strategies.py` allow pluggable notification channels
- **Factory Pattern**: `DietaFactory` encapsulates diet object creation logic
- **Service Layer**: `NotificadorService` coordinates business operations above controllers
- **Mixin Pattern**: `AuditoriaMixin` in `core/base.py` for cross-cutting audit concerns

## Data Flow
```
Patient Prescription Request 
  → Controller (report_controller.py)
    → Core Domain (diet.py, patient.py, prescription.py)
      → Services (DietaFactory, NotificadorService)
        → Strategy Selection (strategies.py)
          → Multi-channel Notifications (Email, Push)
```

## Development Workflows

### Setup & Installation
```bash
poetry install              # Install dependencies (pytest included)
```

### Testing
```bash
pytest                      # Run all tests in tests/
pytest -v                   # Verbose output
```

### Running the Application
```bash
# Direct execution (main.py is entry point stub)
python -m uvicorn src.snh_project.app:app --reload
```

## Project Conventions

### Code Organization
- **Domain logic** always lives in `core/` - never mix business rules into controllers or services
- **ORM models** separate from domain classes: `models/` for database schema, `core/` for business entities
- **Factory creation**: New diet types must extend `DietaFactory` for centralized instantiation

### Naming Conventions
- Portuguese domain terminology: `Paciente`, `Dieta`, `Setor`, `Leito` (Bed), `Cardápio` (Menu)
- Classes: PascalCase (`DietaOral`, `NotificadorService`)
- Attributes: camelCase for domain (`dataNasc`, `factory_year`), snake_case for Python convention where applicable

### Import Paths
- Local imports use relative paths when needed: `from database import Base`
- Absolute imports for installed packages preferred

## Critical Files for Common Tasks

| Task | Key Files |
|------|-----------|
| Add new diet type | `core/diet.py`, `services/factory.py` |
| Add notification channel | `services/strategies.py`, `services/notifier.py` |
| Add patient workflow | `core/patient.py`, `models/models.py` |
| Add API endpoint | `controllers/report_controller.py`, `app.py` |
| Schema changes | `models.py`, ensure `core/` domain logic updates |

## Integration Points

### Notification System
- **Consumer**: `NotificadorService` accepts strategy instances
- **Strategies**: Extend `EstrategiaNotificacao` abstract class
- **New channels**: Implement `NotificacaoPush`, `NotificacaoEmail` pattern in `strategies.py`

### Database
- **ORM Base**: All models inherit from `Base` defined in `database.py`
- **Session Management**: Use `get_session()` dependency injection in controllers
- **Schema Registration**: Add new tables to models.py and import in database.py initialization

## Common Pitfalls to Avoid
- ❌ Don't add business logic to controllers - use services
- ❌ Don't create domain entities that bypass the factory pattern
- ❌ Don't hardcode notification channels - always use strategy pattern
- ❌ Don't modify ORM models without updating domain classes in `core/`

## Next Steps for Agents
1. Review `core/` for domain requirements before implementing
2. Check `services/` for existing patterns before adding cross-cutting functionality
3. Validate factory/strategy patterns are followed for extensibility
4. Run `pytest` to ensure changes don't break existing tests
