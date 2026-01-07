## 1. Overview

This project is a **multi-tenant e-commerce platform** built with **Django and PostgreSQL**.

Each tenant represents an **organization** with:
- its own users
- its own catalog (products, pricing)
- its own orders and customers

The system is designed to ensure **strict tenant data isolation**, predictable scalability, and long-term maintainability.

---

## 2. Architectural Goals

### Primary Goals
- **Zero tenant data leakage**
- **Clear separation of concerns**
- **Scalable to hundreds of tenants**
- **Readable, boring, maintainable code**

### Non-Goals (Explicitly Out of Scope)
- Cross-tenant analytics or reporting
- Per-tenant databases or schemas (for now)
- Marketplace / multi-vendor per tenant
- Real-time features (e.g. live inventory updates)

---

## 3. Tech Stack

### Backend
- **Django** (Core framework)
- **Django REST Framework** (API)
- **Djoser** (Authentication views)
- **Structlog** (Structured logging)

### Database
- **PostgreSQL**
- Single database
- Shared schema
- Tenant ownership enforced at the application layer

### Authentication
- JWT-based authentication (access + refresh) with `rest_framework_simplejwt`
- Authentication is global; authorization is tenant-aware

---

## 4. Configuration & Environment

The application follows the **12-Factor App** methodology. Configuration is stored in environment variables.

### Critical Environment Variables
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Django secret key | Yes | (Unsafe default) |
| `DEBUG` | Enable debug mode | No | `False` |
| `ALLOWED_HOSTS` | Comma-separated host list | Yes | `localhost` |
| `DATABASE_URL` | DB connection string | Yes | `sqlite:///db.sqlite3` |
| `DJANGO_LOG_LEVEL` | Logging level | No | `INFO` |

### Feature Flags
- `ROTATE_REFRESH_TOKENS`: Enable refresh token rotation (Recommended: `True` in prod).
- `SEND_CONFIRMATION_EMAIL`: Enable email verification (Recommended: `True` in prod).

---

## 5. High-Level System Design

```
[ Client (Browser/Mobile) ]
        |
        v
[ Load Balancer / Nginx ]  <-- SSL Termination, Header Forwarding
        |
        v
[ Django (Gunicorn/Uvicorn) ]
        |
        v
[ Middleware Layer ]       <-- Tenant Resolution happens here
        |
        v
[ API Views (DRF) ]
        |
        v
[ Services / Business Logic ]
        |
        v
[ PostgreSQL ]
```

**Key rule:**
Every request must be associated with **exactly one tenant** before any business logic is executed.

---

## 6. Tenant Model & Isolation Strategy

### Tenant Definition
A **Tenant** represents an organization. It is defined in `tenants.models.Tenant`.

### Isolation Strategy (Shared Schema)
- Single database, shared schema.
- All tenant-owned tables include a `tenant_id` foreign key.
- **Enforcement:**
    - **Middleware:** Resolves tenant from request.
    - **Context:** Stores tenant in `contextvars`.
    - **Managers:** `TenantManager` automatically filters queries.
    - **Constraints:** `UniqueTenantConstraint` enforces uniqueness within a tenant scope.

### Why This Strategy
- Operational simplicity (one DB to back up/upgrade).
- Easier migrations (no running migrations N times).
- Lower infrastructure cost.

### Consequences
- Missing tenant filters are critical bugs.
- Requires strict discipline and review.
- Authorization logic becomes central.

---

## 7. Tenant Resolution

### Mechanism
Tenant is resolved via **subdomain** by `tenants.middleware.TenantAwareMiddleware`.

1. **Extract Subdomain:** `tenant.example.com` -> `tenant`.
2. **Lookup:** Query `Tenant` model (cached).
3. **Context:** Set global tenant context via `tenants.context.set_tenant_context`.

### Middleware Order (Critical)
`TenantAwareMiddleware` must run **after** `AuthenticationMiddleware` but **before** any view logic.

```python
MIDDLEWARE = [
    ...,
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "tenants.middleware.TenantAwareMiddleware",  # <--- HERE
    ...,
]
```

### Public Exceptions
Tenant enforcement is bypassed for:
- `/admin/`
- `/health/`
- `/api/tenants/onboard/`
- Public subdomains (e.g., `signup`, `www`)

---

## 8. Backend Code Organization

```
backend
├── config              # Project settings, URLs, WSGI/ASGI
├── tenants             # Core multi-tenancy logic (middleware, context, models)
├── users               # User management (custom user model, auth)
├── products            # E-commerce domain (products, categories, inventory)
└── docs                # Documentation
```

### Design Rules
- **Apps are domain-oriented**, not technical.
- **Business logic lives in services/models**, not views.
- **Views orchestrate**; they do not contain complex logic.

---

## 9. Data Access Rules (Critical)

### Hard Rules
- ❌ **No querying tenant-owned models without a tenant context.**
- ❌ **No `.objects.all()` on tenant-owned models** (handled by `TenantManager`).
- ❌ **No cross-tenant joins.**
- ✅ **All tenant-owned models must inherit from `TenantAwareModel`.**
- ✅ **All uniqueness constraints must be scoped:** Use `UniqueTenantConstraint` instead of `unique=True`.

### Acceptable Patterns
- **Tenant-scoped querysets:** `Product.objects.filter(category__name="...")` (implicitly filters by current tenant).
- **Explicit Tenant Passing:** Services that run background tasks (outside request context) must accept `tenant` as an explicit argument.

---

## 10. Authorization & Permissions

### Authentication
- Verifies *who* the user is.
- Handled globally by `rest_framework_simplejwt`.

### Authorization
- Verifies *what* the user can do.
- **Tenant Check:** User must belong to the current tenant (or be a global admin).
- **Role Check:** User must have required permissions within that tenant.

### Guiding Principle
**Authentication is global. Authorization is tenant-scoped.**

---

## 11. Transactions & Data Integrity

- **Atomic Requests:** Use `ATOMIC_REQUESTS = True` (or explicit `transaction.atomic()`).
- **Inventory Locking:** `select_for_update()` is used when adjusting stock to prevent race conditions.
- **Audit Trails:** Critical actions (stock changes) must be logged to `StockMovement`.

---

## 12. Performance & Scalability Considerations

### Database Indexing
- Most queries will filter by `tenant_id`.
- Standard index pattern: `(tenant_id, field_name)`.
- `TenantAwareModel` automatically indexes the foreign key.

### Caching
- Tenant resolution is cached (5 minutes).
- Future: Per-tenant Redis keyspacing (e.g., `tenant:123:key`).

### Query Optimization
- Avoid N+1 queries: Use `select_related` and `prefetch_related`.
- Pagination is mandatory for list endpoints.

---

## 13. Testing Strategy

### Minimum Expectations
- **Unit tests** for business logic (models/services).
- **Integration tests** for API endpoints.
- **Tenant Isolation tests:** Explicitly attempt to access Tenant A's data with Tenant B's user.

### High-Risk Areas (Must Be Tested)
- Tenant resolution middleware.
- Cross-tenant data leakage.
- Inventory race conditions.

---

## 14. Security Considerations

### Known Risks & Mitigations
- **Data Leakage:** Mitigated by `TenantManager` and `TenantAwareMiddleware`.
- **Subdomain Takeover:** Restricted to alphanumeric + hyphens; reserved words blocked.
- **Insecure Direct Object References (IDOR):** UUIDs used for primary keys; always scoped to tenant.

---

## 15. How to Use This Document

This document is:
- A decision reference.
- An onboarding guide.
- A constraint for LLM usage.
- A review checklist.

If code violates this document:
**the code is wrong**, unless the document is intentionally updated.

---
