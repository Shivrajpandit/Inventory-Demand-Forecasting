# Deployment Guide

This document outlines deployment options and production configurations for the **AI-Powered Inventory Demand Forecasting & Optimization System**.

---

## 1. Architecture Overview

The production system consists of three decoupled components:

1. **Frontend**: React 18 + TypeScript SPA served via Nginx (Port `80` / `3000`).
2. **Backend / Inference Engine**: FastAPI + LightGBM / XGBoost ML models running on Uvicorn (Port `8000`).
3. **Database**: PostgreSQL 15 (or SQLite for zero-config lightweight setups).

---

## 2. Local Containerized Deployment (Docker Compose)

### Prerequisites
- Docker Engine $\ge 20.10$
- Docker Compose v2

### Quick Start

1. **Clone the repository and prepare environment variables**:
   ```bash
   cp .env.example .env
   ```

2. **Build and launch all services**:
   ```bash
   docker-compose up --build -d
   ```

3. **Initialize the database & seed sample data**:
   ```bash
   docker-compose exec backend python scripts/seed_database.py
   ```

4. **Access the application**:
   - Web Dashboard: [http://localhost:3000](http://localhost:3000)
   - FastAPI Interactive API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Backend Health Check: [http://localhost:8000/health](http://localhost:8000/health)

5. **Stop services**:
   ```bash
   docker-compose down
   ```

---

## 3. Cloud Deployment Strategies

### Option A: Render / Railway (Recommended for Full-Stack)

#### Backend + PostgreSQL
1. Create a **PostgreSQL Database** instance on Railway/Render. Copy the `DATABASE_URL`.
2. Create a new **Web Service** pointing to the repository.
   - **Root Directory**: `.`
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Environment Variables**:
     - `DATABASE_URL`: Your PostgreSQL connection string
     - `SECRET_KEY`: High-entropy 32+ character random string
     - `ENVIRONMENT`: `production`
     - `CORS_ORIGINS`: Your frontend production domain URL

#### Frontend (Vercel / Netlify / Render Static Site)
1. Link the `frontend/` directory as the project root.
2. **Build Command**: `npm run build`
3. **Output Directory**: `dist`
4. **Environment Variables**:
   - `VITE_API_BASE_URL`: `https://your-backend-service.onrender.com/api/v1`

---

### Option B: Fly.io (MicroVMs)

1. Launch backend:
   ```bash
   fly launch --dockerfile backend/Dockerfile
   ```
2. Attach Postgres:
   ```bash
   fly postgres create
   fly postgres attach <postgres-app-name>
   ```
3. Set secrets:
   ```bash
   fly secrets set SECRET_KEY=$(openssl rand -hex 32)
   ```

---

## 4. Production Environment Variables Reference

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | SQLAlchemy connection string | `postgresql+psycopg2://user:pwd@db:5432/inventory_db` |
| `SECRET_KEY` | JWT signing secret | 64-character random string |
| `ALGORITHM` | JWT token algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Session validity duration | `1440` (24 hours) |
| `ENVIRONMENT` | Runtime mode (`development` / `production`) | `production` |
| `CORS_ORIGINS` | Comma-delimited allowed browser origins | `https://inventory.yourdomain.com` |

---

## 5. Automated Health Checks & Monitoring

- **Liveness probe**: `GET /health` $\to$ Returns `{"status": "healthy", "timestamp": "...", "version": "1.0.0"}`
- **Database connectivity**: Checked automatically on startup and during health checks.
- **Model Registry check**: `GET /api/v1/models/summary` $\to$ Verifies champion model (`lightgbm`) weights are loaded in memory.
