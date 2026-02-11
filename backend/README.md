# Backend - E-Pharmacy Platform

[![Django](https://img.shields.io/badge/Django-5.0.4-092E20?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14.5-316192?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen?style=flat-square)](https://pytest.org)

> **Production-ready Django REST API with multitenancy, JWT authentication, and comprehensive testing**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)

---

## 🎯 Overview

The backend is a Django REST Framework application providing:

- **Multi-tenant architecture** with row-based data segregation
- **JWT authentication** with refresh token rotation
- **RESTful API** for products, orders, cart, and user management
- **Auto-generated API documentation** with drf-spectacular
- **Comprehensive test suite** using pytest
- **Production-ready** with structured logging, caching, and health checks

---

## 🏗️ Architecture

### Multi-Tenant System

```
Request Flow:
  ↓
Subdomain: tenantone.example.com
  ↓
TenantAwareMiddleware extracts "tenantone"
  ↓
Sets tenant context (thread-local)
  ↓
All queries filtered by tenant_id automatically
  ↓
Response
```

### Apps Structure

```
src/
├── config/           # Project settings, URLs
├── tenants/          # Multi-tenant logic, middleware
├── users/            # User model, auth, serializers
├── products/         # Product catalog, CRUD
├── tests/            # Pytest fixtures and tests
└── utils/            # Shared utilities
```

### Key Features

- **Tenant Middleware**: Automatically filters all database queries by tenant
- **Custom User Model**: Extended Django user with tenant relationships
- **JWT Authentication**: Token-based auth with refresh rotation
- **Structured Logging**: JSON logs with django-structlog
- **Health Checks**: Built-in health check endpoints

---

## 🛠 Technology Stack

| Package | Version | Purpose |
|---------|---------|---------|
| Django | 5.2.1 | Web framework |
| djangorestframework | Latest | API framework |
| djangorestframework-simplejwt | Latest | JWT authentication |
| djoser | Latest | User management endpoints |
| drf-spectacular | Latest | OpenAPI schema generation |
| django-cors-headers | Latest | CORS handling |
| django-structlog | Latest | Structured logging |
| PostgreSQL | 14+ | Database (production) |
| SQLite | 3 | Database (development) |
| pytest | Latest | Testing framework |
| pytest-django | Latest | Django test utilities |
| pytest-cov | Latest | Test coverage |
| gunicorn | Latest | WSGI server (production) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 14+ (for production) or SQLite (for development)
- uv or poetry for dependency management

### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate  # Windows

# Install uv (fast package manager)
pip install uv

# Install dependencies
uv sync --group dev

# Set up environment variables (optional for development)
export DJANGO_DEBUG_FALSE=0  # Keep debug on for dev
```

### Database Setup

```bash
# Run migrations
python src/manage.py migrate

# Create superuser
python src/manage.py createsuperuser

# Load sample data (optional)
python src/manage.py loaddata fixtures/sample_data.json
```

### Running the Server

```bash
# Development server
make run
# OR
python src/manage.py runserver

# Server will be available at http://localhost:8000
```

### Common Commands

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Run migrations
python src/manage.py migrate

# Create new migration
python src/manage.py makemigrations

# Collect static files
python src/manage.py collectstatic
```

---

## 📚 API Documentation

### Interactive Docs

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Authentication

The API uses JWT authentication. To authenticate:

1. **Obtain tokens**:
   ```bash
   POST /api/auth/jwt/create/
   {
     "email": "user@example.com",
     "password": "password123"
   }
   ```

2. **Use access token** in subsequent requests:
   ```bash
   Authorization: Bearer <access_token>
   ```

3. **Refresh token** when expired:
   ```bash
   POST /api/auth/jwt/refresh/
   {
     "refresh": "<refresh_token>"
   }
   ```

### Key Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/jwt/create/` | POST | No | Obtain JWT tokens |
| `/api/auth/jwt/refresh/` | POST | No | Refresh access token |
| `/api/auth/users/` | POST | No | Register new user |
| `/api/products/` | GET | Yes | List products |
| `/api/products/{id}/` | GET | Yes | Product details |
| `/api/cart/` | GET/POST | Yes | Cart operations |
| `/api/orders/` | GET/POST | Yes | Order management |

---

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest -v

# Specific test file
pytest src/tests/users/test_models.py -v

# With coverage
pytest --cov=src --cov-report=html --cov-report=term

# Fast fail (stop on first failure)
pytest -x

# Run specific test
pytest src/tests/users/test_models.py::TestCustomUser::test_user_creation -v
```

### Test Structure

```
tests/
├── conftest.py              # Pytest fixtures
├── tenants/
│   ├── test_middleware.py   # Tenant middleware tests
│   ├── test_models.py       # Tenant model tests
│   └── ...
├── users/
│   ├── test_auth.py         # Authentication tests
│   ├── test_models.py       # User model tests
│   └── ...
└── products/
    ├── test_api.py          # Product API tests
    └── ...
```

### Coverage

Current test coverage: **~85%**

View HTML coverage report:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## 🌐 Deployment

### Production Settings

Set the following environment variables:

```bash
# Required
export DJANGO_SECRET_KEY="<strong-random-secret-key>"
export DJANGO_DEBUG_FALSE=1
export DJANGO_ALLOWED_HOST="yourdomain.com,www.yourdomain.com"

# Database (RDS)
export DATABASE_URL="postgresql://user:password@rds-host:5432/dbname"

# Optional
export DJANGO_LOG_LEVEL="INFO"
```

### Using Gunicorn

```bash
# Install gunicorn (included in dependencies)
uv sync

# Run with gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Docker (Optional)

```bash
# Build image
docker build -t e-pharmacy-backend .

# Run container
docker run -p 8000:8000 \
  -e DJANGO_SECRET_KEY="secret" \
  -e DJANGO_DEBUG_FALSE=1 \
  e-pharmacy-backend
```

### Migrations in Production

```bash
# Apply migrations
python src/manage.py migrate

# Collect static files
python src/manage.py collectstatic --noinput
```

---

## 🔒 Security Considerations

- **Environment Variables**: Never commit secrets; use environment variables
- **CORS**: Configure `CORS_ALLOWED_ORIGINS` for your frontend domains
- **ALLOWED_HOSTS**: Restrict to your production domains
- **DATABASE**: Use PostgreSQL in production, not SQLite
- **HTTPS**: Always use HTTPS in production
- **Token Rotation**: Consider enabling `ROTATE_REFRESH_TOKENS` in production

---

## 📝 Project Structure

```
backend/
├── src/
│   ├── config/              # Django settings and root URLs
│   ├── tenants/             # Multi-tenant app
│   ├── users/               # User management
│   ├── products/            # Product catalog
│   ├── tests/               # All tests
│   ├── utils/               # Shared utilities
│   └── manage.py            # Django management script
├── infrastructure/          # Deployment configs
├── logs/                    # Application logs
├── media/                   # User uploads (dev)
├── staticfiles/             # Collected static files
├── Dockerfile               # Docker configuration
├── Makefile                 # Common commands
├── pyproject.toml           # Python dependencies
└── uv.lock                  # Lock file
```

---

## 🤝 Contributing

1. Follow Django best practices
2. Write tests for new features
3. Run `make format` before committing
4. Ensure all tests pass: `make test`

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.
