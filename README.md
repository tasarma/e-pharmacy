# E-Pharmacy Warehouse Platform

[![Django](https://img.shields.io/badge/Django-5.0.4-092E20?style=for-the-badge&logo=django&logoColor=green)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18.3.1-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14.5-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![AWS](https://img.shields.io/badge/AWS-Deployed-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **A production-grade, multitenant e-commerce platform enabling pharmaceutical warehouses to market products directly to pharmacies, with support for inter-pharmacy medicine exchange in compliance with Turkish Ministry of Health regulations.**

**🚀 Live Demo:** [Deployed on AWS](#) *(AWS infrastructure with EC2, RDS, S3, and CloudFront)*

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Demo](#demo)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Production Deployment](#production-deployment)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

---

## 🎯 Overview

This platform addresses the unique needs of pharmaceutical supply chains by providing:

- **B2B Marketplace**: Warehouses can list and sell pharmaceutical products to registered pharmacies
- **Pharmacy-to-Pharmacy Exchange**: Legal medicine exchange between pharmacies (regulated by Republic of Türkiye Ministry of Health)
- **Multi-Tenant Architecture**: Scalable row-based data segregation supporting multiple organizations
- **Production-Ready**: Deployed on AWS with comprehensive testing, authentication, and monitoring

**Built for production** with Django REST Framework, React with Redux Toolkit, JWT authentication, and PostgreSQL.

---

## ✨ Key Features

### Core Functionality
- 🏥 **Multi-tenant B2B Marketplace** - Warehouses and pharmacies operate independently
- 🔐 **JWT Authentication** - Secure token-based authentication with refresh tokens
- 🛒 **Shopping Cart & Orders** - Complete e-commerce workflow
- 📦 **Product Management** - CRUD operations with image uploads
- 👥 **User Management** - Role-based access control (Warehouse, Pharmacy, Admin)
- 🔄 **Medicine Exchange** - Compliant pharmacy-to-pharmacy transfers

### Technical Highlights
- 🏗️ **Multitenant Architecture** - Row-based data segregation with tenant middleware
- 🧪 **Comprehensive Testing** - Pytest suite with fixtures and mocking
- 📝 **API Documentation** - Auto-generated OpenAPI/Swagger docs with drf-spectacular
- 🎨 **Responsive UI** - Bootstrap-based React components
- 📊 **State Management** - Redux Toolkit with async thunks
- 🚀 **Production Deployment** - AWS infrastructure (EC2, RDS, S3, CloudFront)

---

## 🛠 Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Django | 5.0.4 | Web framework |
| Django REST Framework | Latest | API development |
| PostgreSQL | 14.5 | Primary database |
| Redis | Latest | Caching (planned) |
| JWT | Latest | Authentication |
| Pytest | Latest | Testing |
| Gunicorn | Latest | WSGI server |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3.1 | UI framework |
| TypeScript | 4.9.5 | Type safety |
| Redux Toolkit | 2.2.5 | State management |
| React Router | 6.23.0 | Routing |
| Axios | 1.6.8 | HTTP client |
| Bootstrap | 2.10.2 | UI components |

### DevOps & Tools
| Tool | Purpose |
|------|---------|
| Docker | Containerization |
| AWS EC2 | Application hosting |
| AWS RDS | Managed PostgreSQL |
| AWS S3 | Static/media file storage |
| AWS CloudFront | CDN |
| Poetry/uv | Python dependency management |
| Pre-commit | Code quality hooks |

---

## 🏛️ Architecture

### Multitenant Design

This platform employs a **row-based data segregation strategy** for efficient multi-tenancy:

```
┌─────────────────────────────────────────────┐
│         Single Database Instance            │
├─────────────────────────────────────────────┤
│  Products Table                             │
│  ┌────────┬─────────┬───────────┬─────┐   │
│  │ id     │ name    │ tenant_id │ ... │   │
│  ├────────┼─────────┼───────────┼─────┤   │
│  │ 1      │ Med A   │ tenant1   │ ... │   │
│  │ 2      │ Med B   │ tenant2   │ ... │   │
│  └────────┴─────────┴───────────┴─────┘   │
└─────────────────────────────────────────────┘
```

**Why Row-Based Segregation?**

✅ **Cost Efficiency** - Shared database reduces infrastructure costs  
✅ **Simplified Maintenance** - Single instance to manage and backup  
✅ **Dynamic Tenancy** - Add new tenants without provisioning new databases  
✅ **Customization** - Tenant-specific features via configuration flags  

**Trade-offs:** While one tenant's high load could impact others, the anticipated transaction volume makes this approach ideal for the use case.

### Request Flow

```
User Request → Subdomain Parsing → Tenant Middleware → 
  → Tenant Context Set → Query Filtering → Response
```

---

## 🎬 Demo

### Live Platform Demo

![E-Pharmacy Platform Demo](/public/demo.gif)

### Interactive API Documentation

**Swagger UI** provides interactive API exploration with the ability to test endpoints directly:

![API Schema](/public/ApiSchema.png)

**Access the API docs locally:**
- Swagger UI: `http://tenantone.example.com:8000/api/docs/`
- ReDoc: `http://tenantone.example.com:8000/api/redoc/`

### Frontend Application

**Responsive React interface** with modern UI/UX:

![Frontend Application](/public/frontend.png)

**Key Frontend Features:**
- 📱 Responsive design (mobile-first)
- 🔐 JWT-based authentication
- 🛒 Real-time cart updates
- 🎨 TailwindCSS + Bootstrap styling
- ⚡ Vite for lightning-fast HMR

### Deployment Options

The `dist/` build can be deployed to:

- **AWS S3 + CloudFront** - Static hosting with global CDN (current production)
- **Netlify/Vercel** - Zero-config deployment with automatic builds
- **Nginx** - Traditional web server with proxy to backend API

**Local Development Access:**
```bash
# Frontend
http://tenantone.example.com:5173

# Backend API
http://tenantone.example.com:8000/api/

# Admin Panel
http://tenantone.example.com:8000/admin/
```


---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** (via Anaconda, PyEnv, or system Python)
- **Node.js 16+** and npm
- **PostgreSQL 14+** (local or RDS)
- **Make** (for build automation)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/tasarma/e-pharmacy.git
   cd e-pharmacy
   ```

2. **Set up subdomain resolution**  
   Edit your hosts file:
   
   **Linux/macOS** (`/etc/hosts`):
   ```
   127.0.0.1 tenantone.example.com
   127.0.0.1 tenanttwo.example.com
   ```
   
   **Windows** (`C:\Windows\System32\drivers\etc\hosts`):
   ```
   127.0.0.1 tenantone.example.com
   127.0.0.1 tenanttwo.example.com
   ```

3. **Start backend**
   ```bash
   cd backend
   make sync        # Install dependencies
   make migrate     # Run migrations
   make run         # Start server on :8000
   ```

4. **Start frontend**
   ```bash
   cd frontend
   npm install
   npm run dev      # Start dev server on :5173
   ```

5. **Access the application**
   - Frontend: `http://tenantone.example.com:5173`
   - API Docs: `http://tenantone.example.com:8000/api/docs/`

---

## 📦 Installation

### Backend Setup

```bash
cd backend

# Create virtual environment (choose one)
conda create --name ewarehouse python=3.12
# OR
pyenv virtualenv 3.12 ewarehouse

# Activate environment
conda activate ewarehouse
# OR
pyenv activate ewarehouse

# Install uv (fast Python package manager)
pip install uv

# Install dependencies
uv sync --group dev

# Set up database
python src/manage.py migrate

# Create superuser (optional)
python src/manage.py createsuperuser

# Run development server
python src/manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Start development server
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest -v                              # All tests
pytest --cov=src --cov-report=html     # With coverage

# Frontend tests
cd frontend
npm test
```

---

## 🌐 Production Deployment

### AWS Architecture

The application is deployed on AWS with the following components:

- **EC2**: Application servers (backend + frontend static build)
- **RDS PostgreSQL**: Managed database with automated backups
- **S3**: Media file storage (product images, uploads)
- **CloudFront**: CDN for static assets and media
- **Route 53**: DNS management for custom domains
- **Application Load Balancer**: Traffic distribution and SSL termination

### Deployment Process

```bash
# 1. Build frontend
cd frontend
npm run build

# 2. Collect static files (backend)
cd backend
python src/manage.py collectstatic --noinput

# 3. Deploy to EC2 (example with systemd)
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 4. Sync media to S3
aws s3 sync media/ s3://your-bucket/media/
```

### Environment Configuration

Required environment variables for production:

```bash
# Backend
DJANGO_SECRET_KEY=<secure-random-key>
DJANGO_DEBUG_FALSE=1
DJANGO_ALLOWED_HOST=yourdomain.com,www.yourdomain.com
DJANGO_DB_PATH=/path/to/db  # or use DATABASE_URL for RDS
DATABASE_URL=postgresql://user:pass@rds-endpoint/dbname

# Frontend
VITE_API_URL=https://api.yourdomain.com
```

---

## 📚 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/jwt/create/` | POST | Obtain JWT tokens |
| `/api/auth/jwt/refresh/` | POST | Refresh access token |
| `/api/products/` | GET | List products |
| `/api/products/{id}/` | GET | Product details |
| `/api/cart/` | GET/POST | Cart operations |
| `/api/orders/` | GET/POST | Order management |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest` and `npm test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please ensure:
- Code passes all tests
- New features include tests
- Code follows project style (use `pre-commit run --all-files`)
- PR description clearly explains changes

---

## 🗺️ Roadmap

- [x] User authentication with JWT
- [x] Multi-tenant architecture
- [x] Product catalog and cart
- [x] AWS deployment
- [ ] Payment gateway integration (Stripe/PayPal)
- [ ] Email notifications
- [ ] Redis caching layer
- [ ] Real-time order tracking
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard

---

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](/public/LICENSE) file for details.

---

## 🔒 Security & Compliance

- **Data Protection**: Complies with applicable data protection regulations
- **Medical Regulations**: Designed for compliance with Republic of Türkiye Ministry of Health pharmaceutical regulations
- **Security**: JWT authentication, CORS protection, SQL injection prevention, XSS protection

**Note**: Ensure full legal and regulatory compliance when handling pharmaceutical data in production.

---

*Built with ❤️ using Django, React, and modern web technologies*
