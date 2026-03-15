# Environment Variable Map

## Quick Reference

| Variable | App | Required | Default | Description |
|----------|-----|----------|---------|-------------|
| **Core** |
| `NODE_ENV` | web | No | development | development \| production |
| `DATABASE_URL` | api, worker | Yes | - | PostgreSQL connection string |
| `REDIS_URL` | api, worker | Yes* | redis://localhost:6379/0 | Redis URL |
| `SECRET_KEY` | api | Yes | - | JWT signing, encryption |
| `CORS_ORIGINS` | api | No | ["http://localhost:3000"] | JSON array |
| **Storage** |
| `STORAGE_PROVIDER` | api, worker | No | local | local \| s3 \| r2 \| gcs |
| `STORAGE_LOCAL_PATH` | api, worker | If local | ./storage | Local path |
| `S3_BUCKET` | api, worker | If S3 | - | Bucket name |
| `AWS_ACCESS_KEY_ID` | api, worker | If S3/R2 | - | AWS/Cloudflare |
| `AWS_SECRET_ACCESS_KEY` | api, worker | If S3/R2 | - | AWS/Cloudflare |
| `R2_ACCOUNT_ID` | api, worker | If R2 | - | Cloudflare account |
| `R2_BUCKET` | api, worker | If R2 | - | R2 bucket |
| **AI** |
| `AI_PROVIDER` | api | No | openai | openai \| anthropic \| none |
| `OPENAI_API_KEY` | api | If OpenAI | - | OpenAI key |
| `ANTHROPIC_API_KEY` | api | If Anthropic | - | Anthropic key |
| `AI_MODEL` | api | No | gpt-4o-mini | Model name |
| **Notifications** |
| `NOTIFICATION_EMAIL_PROVIDER` | api, worker | No | none | smtp \| sendgrid \| ses |
| `SMTP_HOST` | worker | If SMTP | - | SMTP host |
| `SENDGRID_API_KEY` | worker | If SendGrid | - | SendGrid key |
| **Telemetry** |
| `TELEMETRY_ENABLED` | api, worker | No | false | Enable OTLP |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | api, worker | If telemetry | - | OTLP endpoint |
| `SENTRY_DSN` | api, web | No | - | Sentry DSN |
| **Feature Flags** |
| `FEATURE_FLAGS_PROVIDER` | api | No | database | database \| launchdarkly |
| `LAUNCHDARKLY_SDK_KEY` | api | If LD | - | LD key |
| **Deployment** |
| `DEPLOYMENT_MODE` | api | No | standalone | standalone \| saas \| anakatech |
| `API_PUBLIC_URL` | api, web | Prod | - | Public API URL |
| `NEXT_PUBLIC_API_URL` | web | No | - | API URL for browser |
| `NEXT_PUBLIC_WEB_URL` | web | No | - | Web URL for emails |

*Redis optional in minimal standalone (no worker, no queues)

## By Deployment Mode

### Standalone
- `DATABASE_URL`, `SECRET_KEY` required
- `REDIS_URL` optional if no worker
- `STORAGE_PROVIDER=local`
- `DEPLOYMENT_MODE=standalone`

### SaaS
- All core + storage (S3/R2) + notifications
- `DEPLOYMENT_MODE=saas`
- Billing env (Stripe) when enabled

### Anakatech
- Same as SaaS + `DEPLOYMENT_MODE=anakatech`
- Org/tenant config from Anakatech
