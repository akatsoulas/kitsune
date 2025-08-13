# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment Setup

This is **Kitsune**, the Django platform that powers SuMo (support.mozilla.org). The project uses Docker for development.

### Quick Start Commands

```bash
# Initial setup (creates .env, builds images, installs dependencies)
make init                    # Run bootstrap script, migrations, node setup
make build                  # Build Docker images

# Run the application
make start                  # Start all services via docker-compose

# Development shells
make shell                  # Bash shell in container
make runshell              # Bash shell with ports bound
make djshell               # Django shell (ipython)
make dbshell               # PostgreSQL shell
```

### Testing Commands

```bash
# Python tests
make test                   # Run Django unit tests via ./bin/run-unit-tests.sh
python manage.py test       # Direct Django test command
python manage.py test path.to.specific.test --verbosity=2

# JavaScript tests  
make test-js               # Run JS tests via npm run webpack:test

# Lint and format
make lint                  # Run pre-commit hooks (includes ruff)
make format                # Format Python code with black  
ruff format                # Format Python code with ruff (recommended)
npm run stylelint          # Lint SCSS files
```

## Application Architecture

### Core Django Apps Structure

**Primary Applications:**
- `wiki/` - Knowledge Base articles and documentation
- `questions/` - Support questions and answers (Q&A system)  
- `forums/` - Discussion forums
- `users/` - User profiles, authentication, and account management
- `search/` - Elasticsearch-powered search functionality
- `gallery/` - Media management (images, videos)
- `products/` - Mozilla product definitions and topics
- `kpi/` - Metrics and analytics dashboard

**Supporting Applications:**
- `sumo/` - Core utilities, base templates, middleware
- `flagit/` - Content moderation system
- `messages/` - Private messaging between users
- `notifications/` - Event notification system
- `tidings/` - Email notification subscription management
- `kbadge/` - Badge system for user achievements
- `groups/` - User group management
- `dashboards/` - Analytics and reporting dashboards
- `llm/` - AI/ML features (moderation, translations)

### Key Technologies

- **Backend:** Django 4.2+, Python 3.11
- **Package Management:** uv (replaced poetry in July 2025)
- **Database:** PostgreSQL
- **Search:** Elasticsearch 9.0+  
- **Cache:** Redis
- **Task Queue:** Celery with Redis broker
- **Frontend:** Webpack, SCSS, vanilla JavaScript + jQuery
- **Testing:** Django TestCase, pytest for E2E (Playwright)
- **Linting:** ruff (replaced flake8/black in July 2025)

### Environment Variables

Essential environment variables are defined in `.env-dist`. Key ones include:
- `DATABASE_URL` - PostgreSQL connection
- `ES_URLS` - Elasticsearch endpoints  
- `REDIS_*` - Redis configuration for cache and Celery
- `DEBUG`, `DEV` - Development mode flags

### Docker Services

The `docker-compose.yml` defines:
- `web` - Main Django application (port 8000)
- `postgres` - Database (port 5432)
- `elasticsearch` - Search engine (port 9200)
- `redis` - Cache and message broker
- `celery` - Background task worker
- `mailcatcher` - Email testing (port 1080)

### Package Management with uv

```bash
# Install dependencies
uv sync                    # Install all dependencies
uv sync --frozen           # Install from lockfile without updates
uv add package-name        # Add new dependency
uv pip install package     # Install package in current environment
```

### Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Elasticsearch Management

```bash
python manage.py es_init --migrate-writes --migrate-reads  # Initialize ES
python manage.py es_reindex --count 10 --verbosity 2       # Reindex content
```

### Localization (L10n)

Kitsune supports 100+ locales. Key files:
- `kitsune/lib/sumo_locales.py` - Locale definitions
- `locale/` - Translation files
- Language-specific synonyms in `search/dictionaries/synonyms/`

### Frontend Build System

```bash
# Webpack commands
npm run webpack:build      # Production build
npm run webpack:watch      # Development with file watching
npm run build:styleguide   # Generate CSS styleguide

# Browser development
npm run start             # Webpack + BrowserSync
npm run browser-sync      # Live reload server
```

### Common Development Patterns

- Models use `ModelBase` from sumo.models for common fields
- Views often use `mobile_template()` decorator for mobile templates
- Search uses custom Elasticsearch Document classes in `search/documents.py`
- All user-facing strings should be marked for translation with `_()` or `_lazy()`
- Cache keys use app-specific prefixes (defined in individual apps)

### Testing Guidelines  

- Python tests live in `tests/` directories within each app
- Use factories from `factory_boy` for test data creation
- Search tests often need `@mock.patch` for Elasticsearch
- E2E tests use Playwright and are in `playwright_tests/`
- Tests run in isolated database with `TESTING=True`

### Key Configuration Files

- `pyproject.toml` - Python dependencies and ruff configuration  
- `uv.lock` - Locked dependency versions (replaces poetry.lock)
- `package.json` - Node.js dependencies, build scripts
- `webpack.*.js` - Frontend build configuration  
- `Makefile` - Development commands wrapper
- `docker-compose.yml` - Local development stack
- `.github/dependabot.yml` - Automated dependency updates for uv and npm

### Development Best Practices

- Always format Python files after changes with `ruff format`
- Use `ruff check` for linting python files
- Run `make lint` before committing (uses pre-commit hooks)
- Do not insert trailing slashes in URLs
- Use uv for Python package management
- Dependabot automatically updates dependencies weekly
