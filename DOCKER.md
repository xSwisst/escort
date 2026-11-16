# Docker Compose Infrastructure

This document describes the Docker Compose setup for the escort project.

## Services

### Core Infrastructure

#### PostgreSQL Database
- **Container:** `escort_postgres`
- **Image:** `postgres:16-alpine`
- **Port:** `5432`
- **Config:** `postgres/.env`
- **Volume:** `postgres_data` (persistent storage)

#### Cloudflare Tunnel
- **Container:** `escort_cloudflare_tunnel`
- **Image:** `cloudflare/cloudflared:latest`
- **Config:** `cloudflare/.env`
- **Purpose:** Expose services to the internet securely

### Application Services

#### API Service
- **Container:** `escort_api`
- **Port:** `8000`
- **Config:** `api/.env`
- **Routes:**
  - `/client/v1/*` - Client endpoints (JWT auth)
  - `/admin/v1/*` - Admin endpoints (API Key auth)

#### Photos Service
- **Container:** `escort_photos`
- **Port:** `8005`
- **Config:** `photos/.env`
- **Volume:** `photos_storage` (photo files storage)

#### Logs Service
- **Container:** `escort_logs`
- **Port:** `8006`
- **Config:** `logs/.env`

#### Main Bot
- **Container:** `escort_main_bot`
- **Port:** `8001`
- **Config:** `main/.env`

#### Support Bot
- **Container:** `escort_support_bot`
- **Port:** `8002`
- **Config:** `support/.env`

#### Admin Bot
- **Container:** `escort_admin_bot`
- **Port:** `8003`
- **Config:** `admin/.env`

#### Web App
- **Container:** `escort_web_app`
- **Port:** `8004`
- **Config:** `web_app/.env`

#### Web Landing Service
- **Container:** `escort_web`
- **Port:** `8007`
- **Config:** `web/.env`

## Networks

All services are connected via `escort_network` bridge network for internal communication.

## Volumes

- **postgres_data** - PostgreSQL database persistent storage
- **photos_storage** - Uploaded photos persistent storage
- **logs_data** - Logs service persistent storage

## Configuration Files

Each service has its own `.env` file:

```
new_escort/
├── postgres/.env        # POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
├── cloudflare/.env      # TUNNEL_TOKEN
├── api/.env             # API_SECRET_KEY, ADMIN_API_KEY, DB_URL, etc.
├── photos/.env          # API_SECRET_KEY, PHOTOS_DOMAIN, etc.
├── logs/.env            # API_SECRET_KEY, DB credentials, etc.
├── main/.env            # BOT_TOKEN, API_BASE_URL, etc.
├── support/.env         # BOT_TOKEN, API_BASE_URL, etc.
├── admin/.env           # BOT_TOKEN, API_BASE_URL, ADMIN_API_KEY, etc.
├── web_app/.env         # WEB_APP_BOT_TOKEN, API_BASE_URL, etc.
├── web/.env             # WEB_DOMAIN, BOT_USERNAME, API_BASE_URL, etc.
```

└── web_app/.env         # API_BASE_URL, SESSION_SECRET, etc.
```

Copy `.env.example` to `.env` in each directory and fill in the values.

## Setup Instructions

### 1. Copy environment files

```bash
# For each service
cp postgres/.env.example postgres/.env
cp cloudflare/.env.example cloudflare/.env
cp api/.env.example api/.env
cp photos/.env.example photos/.env
cp logs/.env.example logs/.env
cp main/.env.example main/.env
cp support/.env.example support/.env
cp admin/.env.example admin/.env
cp web_app/.env.example web_app/.env
```

### 2. Generate secrets

```bash
# Generate API_SECRET_KEY (same for all services)
openssl rand -hex 32

# Generate ADMIN_API_KEY
openssl rand -hex 32

# Generate POSTGRES_PASSWORD
openssl rand -hex 32

# Generate WEB_APP_SESSION_SECRET
openssl rand -hex 32

# Generate WEBHOOK_SECRET_TOKEN (for each bot if using webhooks)
openssl rand -hex 32
```

### 3. Configure PostgreSQL

Edit `postgres/.env`:
```bash
POSTGRES_USER=escort
POSTGRES_PASSWORD=<generated-password>
POSTGRES_DB=escort
```

### 4. Configure Cloudflare Tunnel

1. Go to https://one.dash.cloudflare.com/
2. Navigate to Networks > Tunnels
3. Create a new tunnel
4. Configure public hostnames:
   - `api.domain.com` → `http://escort_api:8000`
   - `photos.domain.com` → `http://escort_photos:8005`
   - `logs.domain.com` → `http://escort_logs:8006`
   - `web.domain.com` → `http://escort_web_app:3000`
5. Copy the tunnel token

Edit `cloudflare/.env`:
```bash
TUNNEL_TOKEN=<your-tunnel-token>
```

### 5. Configure API Service

Edit `api/.env`:
```bash
API_SECRET_KEY=<generated-secret>
API_AUDIENCE=escort_api
ADMIN_API_KEY=<generated-admin-key>
DB_URL=postgresql+asyncpg://escort:<postgres-password>@postgres:5432/escort
PHOTOS_API_URL=https://photos.domain.com
LOGS_API_URL=https://logs.domain.com
```

### 6. Configure Photos Service

Edit `photos/.env`:
```bash
API_SECRET_KEY=<same-as-api>
API_AUDIENCE=photos_service
PHOTOS_DOMAIN=photos.domain.com
PHOTOS_STORAGE_PATH=/data/photos
```

### 7. Configure Logs Service

Edit `logs/.env`:
```bash
API_SECRET_KEY=<same-as-api>
API_AUDIENCE=logs_service
DB_HOST=postgres
DB_PASSWORD=<postgres-password>
LOGS_BOT_TOKEN=<telegram-bot-token>
LOGS_CHAT_ID=<telegram-chat-id>
```

### 8. Configure Bots

Edit `main/.env`, `support/.env`, `admin/.env`:
```bash
BOT_TOKEN=<telegram-bot-token>
API_SECRET_KEY=<same-as-api>
API_BASE_URL=https://api.domain.com
LOGS_API_URL=https://logs.domain.com
```

For admin bot, also add:
```bash
ADMIN_API_KEY=<same-as-api-admin-key>
```

### 9. Configure Web App

Edit `web_app/.env`:
```bash
API_SECRET_KEY=<same-as-api>
WEB_APP_SESSION_SECRET=<generated-session-secret>
API_BASE_URL=https://api.domain.com
LOGS_API_URL=https://logs.domain.com
```

## Running

### Start all services

```bash
docker compose up -d
```

### Check status

```bash
docker compose ps
```

### View logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f postgres
docker compose logs -f cloudflare_tunnel
```

### Stop all services

```bash
docker compose down
```

### Stop and remove volumes (WARNING: deletes data)

```bash
docker compose down -v
```

## Database Migrations

### API Service

```bash
# Enter API container
docker compose exec api bash

# Run migrations
alembic upgrade head
```

### Logs Service

```bash
# Enter Logs container
docker compose exec logs bash

# Run migrations
alembic upgrade head
```

## Healthchecks

All services expose `/health` endpoint for monitoring:

- API: http://localhost:8000/health
- Photos: http://localhost:8005/health
- Logs: http://localhost:8006/health

## Troubleshooting

### PostgreSQL connection issues

```bash
# Check postgres is running
docker compose ps postgres

# Check postgres logs
docker compose logs postgres

# Test connection
docker compose exec postgres psql -U escort -d escort
```

### Cloudflare Tunnel not connecting

```bash
# Check tunnel logs
docker compose logs cloudflare_tunnel

# Verify TUNNEL_TOKEN is correct
# Check Cloudflare dashboard for tunnel status
```

### Service can't reach another service

All services use internal Docker network names:
- `postgres` (not localhost)
- `escort_api` (not localhost)
- `escort_photos` (not localhost)

Example:
```bash
# WRONG
DB_URL=postgresql://escort:password@localhost:5432/escort

# CORRECT
DB_URL=postgresql://escort:password@postgres:5432/escort
```

## Backup

### Database

```bash
# Backup
docker compose exec postgres pg_dump -U escort escort > backup.sql

# Restore
docker compose exec -T postgres psql -U escort escort < backup.sql
```

### Photos

```bash
# Backup photos volume
docker run --rm \
  -v escort_photos_storage:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/photos-backup.tar.gz /data
```

## Production Recommendations

1. **Use secrets management** - Don't commit `.env` files
2. **Set up monitoring** - Prometheus + Grafana
3. **Configure backups** - Automated database and photos backups
4. **Use Docker secrets** - Instead of env files
5. **Set resource limits** - Memory and CPU limits per service
6. **Enable logging driver** - Centralized log collection
