# Database and Storage

## PostgreSQL

AUTHORA uses PostgreSQL 16 with the pgvector extension for embeddings and semantic search.

### Connection String

```
postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```

- **Docker dev**: `postgresql://authora:authora@localhost:5432/authora`
- **Docker prod**: `postgresql://authora:PASSWORD@postgres:5432/authora` (internal hostname)

### Migrations

```bash
# Via Docker
./scripts/db-migrate.sh --docker

# Production
./scripts/db-migrate.sh --docker --prod
```

Or directly:

```bash
cd apps/api
alembic upgrade head
```

### Managed PostgreSQL

For production, you can use a managed PostgreSQL service (e.g., AWS RDS, Supabase). Update `DATABASE_URL` to point to the external host. Ensure:

- pgvector extension is available
- SSL is enabled if required
- Connection pool limits are appropriate

## Redis

Redis is used for caching, sessions, and background job queues.

### Connection String

```
redis://HOST:PORT/DB
```

- **Docker dev**: `redis://localhost:6379/0`
- **Docker prod**: `redis://redis:6379/0`

### Managed Redis

You can use managed Redis (e.g., Redis Cloud, ElastiCache). Update `REDIS_URL` accordingly.

## Storage

### Local Storage

Default: `STORAGE_PROVIDER=local` with `STORAGE_LOCAL_PATH=./storage`

Files (manuscripts, exports, uploads) are stored on the filesystem. Ensure the path is writable and has sufficient disk space.

### S3 / R2

For production, consider object storage:

- **Amazon S3**: Set `STORAGE_PROVIDER=s3`, `S3_BUCKET`, `AWS_REGION`, and AWS credentials
- **Cloudflare R2**: Set `STORAGE_PROVIDER=r2`, `R2_BUCKET`, `R2_ACCOUNT_ID`, and R2 credentials

Configure via the setup wizard or `.env`.
