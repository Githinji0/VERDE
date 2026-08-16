# Deployment Guide

## 1. Local Development
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

## 2. Production Deployment
For institutional deployments with PostgreSQL:

```bash
# Set environment variables in .env
DATABASE_URL=postgresql+asyncpg://verde_user:strong_password@localhost:5432/verde_db
APP_ENV=production
DEBUG=false
SECRET_KEY=generate_64_byte_random_secret_here

# Run with multi-worker Uvicorn / Gunicorn
gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```
