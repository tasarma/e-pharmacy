# Frontend - E-Pharmacy Platform

[![React](https://img.shields.io/badge/React-18.3.1-20232A?style=flat-square&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![Redux](https://img.shields.io/badge/Redux_Toolkit-2.2.5-764ABC?style=flat-square&logo=redux)](https://redux-toolkit.js.org/)
[![Vite](https://img.shields.io/badge/Vite-Latest-646CFF?style=flat-square&logo=vite)](https://vitejs.dev/)

> **Modern React application with TypeScript, Redux Toolkit, and responsive UI for pharmaceutical e-commerce**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [State Management](#state-management)
- [Development](#development)
- [Build & Deployment](#build--deployment)

---

## 🎯 Overview

The frontend is a modern React application providing:

- **TypeScript** for type safety and better developer experience
- **Redux Toolkit** for predictable state management
- **React Router** for client-side routing
- **Bootstrap** for responsive, mobile-first UI
- **Axios** for API communication with JWT authentication
- **Vite** for lightning-fast build and HMR

---

## 🛠 Technology Stack

| Package | Version | Purpose |
|---------|---------|---------|
| React | 18.3.1 | UI library |
| TypeScript | 4.9.5 | Type safety |
| Redux Toolkit | 2.2.5 | State management |
| React Router | 6.23.0 | Routing |
| Axios | 1.6.8 | HTTP client |
| React Bootstrap | 2.10.2 | UI components |
| Vite | Latest | Build tool |
| jwt-decode | 4.0.0 | JWT token parsing |
| TailwindCSS | 3.x | Utility-first CSS |

---

## 🏗️ Architecture

### Component Hierarchy

```
App
├── BrowserRouter
│   └── Routes
│       ├── Layout (Header + Footer)
│       │   ├── Home
│       │   ├── Store (Protected)
│       │   ├── Product Details (Protected)
│       │   ├── Cart (Protected)
│       │   ├── Profile (Protected)
│       │   └── Login
│       └── NoPage (404)
```

### State Management Flow

```
User Action → Dispatch Action → Async Thunk (API Call) → 
  → Reducer Updates State → Component Rerenders
```

### Key Features

- **Protected Routes**: Authentication guard with automatic redirect
- **Subdomain-based API**: Dynamic API URL based on subdomain
- **Persistent Auth**: JWT tokens stored in localStorage
- **Responsive Design**: Mobile-first with Bootstrap grid
- **Type Safety**: Full TypeScript coverage

---

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API running (see [backend README](../backend/README.md))

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
```

### Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

### Running the App

```bash
# Development server with hot reload
npm run dev

# App will be available at http://localhost:5173
```

### Building for Production

```bash
# Create optimized production build
npm run build

# Preview production build locally
npm run preview
```

---

## 📁 Project Structure

```
frontend/
├── public/               # Static assets
│   ├── ApiSchema.png
│   ├── frontend.png
│   ├── demo.gif
│   └── ...
├── src/
│   ├── api/             # API client configuration
│   ├── assets/          # Images, fonts, etc.
│   ├── components/      # Reusable UI components
│   │   └── layout/      # Header, Footer, Layout
│   ├── features/        # Redux slices
│   │   ├── auth/        # Authentication slice
│   │   ├── cart/        # Shopping cart slice
│   │   └── product/     # Product slice
│   ├── pages/           # Page components
│   ├── utils/           # Utility functions
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # Entry point
│   ├── store.ts         # Redux store configuration
│   ├── types.ts         # TypeScript type definitions
│   └── index.css        # Global styles
├── index.html           # HTML template
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies
```

---

## 🗄️ State Management

### Redux Store Structure

```typescript
{
  auth: {
    userInfo: User | null,
    loading: boolean,
    error: string | null
  },
  products: {
    items: Product[],
    loading: boolean,
    error: string | null
  },
  cart: {
    items: CartItem[],
    total: number
  }
}
```

### Key Slices

- **authSlice**: User authentication, login/logout
- **productsSlice**: Product catalog management
- **cartSlice**: Shopping cart operations

### Example Usage

```typescript
import { useAppDispatch, useAppSelector } from './hooks';
import { fetchProducts } from './features/product/productsSlice';

function Store() {
  const dispatch = useAppDispatch();
  const { items, loading } = useAppSelector(state => state.products);

  useEffect(() => {
    dispatch(fetchProducts());
  }, [dispatch]);

  // ...
}
```

---

## 🔐 Authentication Flow

1. **Login**: User enters credentials
2. **API Call**: POST to `/api/auth/jwt/create/`
3. **Token Storage**: Store access & refresh tokens in localStorage
4. **Protected Routes**: `PrivateRoute` checks for valid token
5. **API Requests**: Axios interceptor adds `Authorization: Bearer <token>`
6. **Token Refresh**: Automatic refresh when access token expires

### Protected Route Example

```tsx
import PrivateRoute from './utils/PrivateRoute';

<Route
  path="store"
  element={
    <PrivateRoute>
      <Store />
    </PrivateRoute>
  }
/>
```

---

## 🌐 API Integration

### Subdomain-based API URL

The app constructs API URLs based on the current subdomain:

```typescript
// utils/Api.ts
const hostname = window.location.hostname;
const subdomain = hostname.split(".")[0];
const url = `http://${subdomain}.example.com:8000/${endpoint}`;
```

**Example**:
- Visiting `tenantone.example.com:5173` → API calls to `tenantone.example.com:8000`
- Visiting `tenanttwo.example.com:5173` → API calls to `tenanttwo.example.com:8000`

### Making API Calls

```typescript
import { fetchFromSubdomain } from './utils/Api';
import { HttpMethods } from './types';

// GET request
const products = await fetchFromSubdomain<Product[]>('api/products/');

// POST request
const newOrder = await fetchFromSubdomain<Order>(
  'api/orders/',
  HttpMethods.POST,
  orderData
);
```

---

## 🎨 Styling

### Approach

- **TailwindCSS**: Utility-first CSS for rapid development
- **Bootstrap**: Component library for consistent UI
- **Custom CSS**: Global styles in `index.css`

### Responsive Design

All components are mobile-first and responsive:

```tsx
<div className="container mx-auto px-4">
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {/* Product cards */}
  </div>
</div>
```

---

## 🧪 Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Type check
npm run type-check
```

### Code Quality

- **ESLint**: Enforces code style and catches errors
- **TypeScript**: Type checking at compile time
- **Prettier**: Code formatting (via ESLint)

---

## 📦 Build & Deployment

### Production Build

```bash
# Create optimized build
npm run build

# Output will be in dist/ directory
```

### Build Optimizations

Vite automatically applies:
- Code splitting
- Tree shaking
- Asset optimization
- Minification

### Deployment

The `dist/` folder can be deployed to:

- **AWS S3 + CloudFront**: Static hosting with CDN
- **Netlify/Vercel**: Zero-config deployment
- **Nginx**: Traditional web server

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name tenantone.example.com;

    root /var/www/e-pharmacy/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

---

## 🔧 Configuration

### Vite Config

Key configurations in `vite.config.ts`:

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
```

### TypeScript Config

Strict mode enabled for maximum type safety:

```json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2020",
    "module": "ESNext",
    "jsx": "react-jsx"
  }
}
```

---

## 🤝 Contributing

1. Follow React best practices and hooks guidelines
2. Use TypeScript for all new components
3. Ensure responsive design (mobile-first)
4. Write descriptive component names
5. Keep components small and focused

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.

---

*Built with ⚛️ React and modern web technologies*
