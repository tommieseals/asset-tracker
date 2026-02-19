# Deployment Guide

## Prerequisites

- Docker & Docker Compose
- PostgreSQL (for production)
- Reverse proxy (nginx/Caddy)

---

## Docker Compose (Recommended)

### 1. Clone and Configure

```bash
git clone https://github.com/tommieseals/asset-tracker.git
cd asset-tracker

# Create .env file
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/assets
AI_API_URL=http://ollama:11434/v1
AI_MODEL=qwen2.5:3b
EOF
```

### 2. Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: assets
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:${DB_PASSWORD}@db:5432/assets
      SECRET_KEY: ${SECRET_KEY}
      AI_API_URL: ${AI_API_URL}
      AI_MODEL: ${AI_MODEL}
    depends_on:
      - db
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: ${API_URL}
    depends_on:
      - backend
    restart: unless-stopped

  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  caddy_data:
```

### 3. Caddyfile

```caddyfile
assets.example.com {
    handle /api/* {
        reverse_proxy backend:8000
    }
    handle {
        reverse_proxy frontend:3000
    }
}
```

### 4. Deploy

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Cloud Deployment

### Google Cloud Run

1. Build and push images:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/asset-tracker-backend ./backend
gcloud builds submit --tag gcr.io/PROJECT_ID/asset-tracker-frontend ./frontend
```

2. Deploy backend:
```bash
gcloud run deploy asset-tracker-backend \
  --image gcr.io/PROJECT_ID/asset-tracker-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars "DATABASE_URL=..." \
  --set-secrets "SECRET_KEY=asset-tracker-secret:latest"
```

3. Deploy frontend:
```bash
gcloud run deploy asset-tracker-frontend \
  --image gcr.io/PROJECT_ID/asset-tracker-frontend \
  --platform managed \
  --region us-central1 \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://asset-tracker-backend-xxx.run.app"
```

---

## Database Migrations

### Initial Setup

```bash
cd backend

# Initialize Alembic (already done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial"

# Apply migration
alembic upgrade head
```

### Seed Data

```bash
# SQLite
sqlite3 assets.db < seed/sample_data.sql

# PostgreSQL
psql -h localhost -U postgres -d assets -f seed/sample_data.sql
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | JWT signing key (min 32 chars) |
| `DATABASE_URL` | Yes | Database connection string |
| `AI_API_URL` | No | OpenAI-compatible API (default: Ollama) |
| `AI_MODEL` | No | Model name (default: qwen2.5:3b) |
| `CORS_ORIGINS` | No | Allowed CORS origins |

---

## Security Checklist

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Regular backups
- [ ] Monitor access logs

---

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Logs

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Metrics

Consider adding:
- Prometheus metrics endpoint
- Grafana dashboards
- Error tracking (Sentry)

---

## Backup

### PostgreSQL

```bash
# Backup
pg_dump -h localhost -U postgres assets > backup.sql

# Restore
psql -h localhost -U postgres -d assets < backup.sql
```

### Full Backup (Docker volumes)

```bash
docker run --rm \
  -v asset-tracker_postgres_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/db-$(date +%Y%m%d).tar.gz /data
```
