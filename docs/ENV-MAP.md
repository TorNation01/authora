# Environment Variable Map

## Quick Reference

| Variable | App | Required | Default | Description |
|----------|-----|----------|---------|-------------|
| **Core** |
| `NODE_ENV` | web | No | development | development \| production |
| `DATABASE_URL` | api, worker | Yes | - | PostgreSQL connection string |
| `REDIS_URL` | api, worker | Yes* | redis://localhost:6379/0 | Redis URL |
| `SECRET_KEY` | api | Yes | - | JWT signing, encryption |
| `CORS_ORIGINS` | api | No | ["http://localhost:3000"] | JSON array; prod: authora.studio, app.authora.studio |
| **Storage** |
| `STORAGE_PROVIDER` | api, worker | No | local | local \| s3 \| r2 \| gcs |
| `STORAGE_LOCAL_PATH` | api, worker | If local | ./storage | Local path |
| `S3_BUCKET` | api, worker | If S3 | - | Bucket name |
| `AWS_ACCESS_KEY_ID` | api, worker | If S3/R2 | - | AWS/Cloudflare |
| `AWS_SECRET_ACCESS_KEY` | api, worker | If S3/R2 | - | AWS/Cloudflare |
| `R2_ACCOUNT_ID` | api, worker | If R2 | - | Cloudflare account |
| `R2_BUCKET` | api, worker | If R2 | - | R2 bucket |
| **AI** |
| `AI_PROVIDER` | api | No | openai | openai \| anthropic \| ollama |
| `AI_PROVIDER_MODE` | api | No | auto | auto \| cloud \| local |
| `OPENAI_API_KEY` | api | If OpenAI | - | OpenAI key |
| `ANTHROPIC_API_KEY` | api | If Anthropic | - | Anthropic key |
| `AI_MODEL` | api | No | gpt-4o-mini | Model name |
| `OLLAMA_ENABLED` | api | No | false | Enable Ollama |
| `OLLAMA_BASE_URL` | api | No | http://localhost:11434 | Ollama API URL |
| `OLLAMA_MODEL_DEFAULT` | api | No | llama3.2 | Default Ollama model |
| `OLLAMA_MODEL_WRITING_ASSIST` | api | No | - | Legacy task-specific model |
| `OLLAMA_MODEL_FICTION_IDEATION` | api | No | - | Legacy task-specific model |
| `OLLAMA_MODEL_NONFICTION_STRUCTURE` | api | No | - | Legacy task-specific model |
| `OLLAMA_MODEL_GHOSTWRITING` | api | No | - | Legacy task-specific model |
| `OLLAMA_MODEL_EDITING_POLISH` | api | No | - | Legacy task-specific model |
| `OLLAMA_MODEL_QUICK_ASSIST` | api | No | qwen3:4b | Role: quick assist |
| `OLLAMA_MODEL_DEFAULT_WRITING` | api | No | qwen3:8b | Role: default writing |
| `OLLAMA_MODEL_PREMIUM_DRAFTING` | api | No | qwen3:14b | Role: premium drafting |
| `OLLAMA_MODEL_EMBEDDINGS` | api | No | qwen3-embedding:4b | Role: embeddings |
| `OLLAMA_MODEL_OPTIONAL_VISION` | api | No | qwen3-vl:8b | Role: vision (optional) |
| `OLLAMA_HARDWARE_TIER` | api | No | auto | 1 \| 2 \| 3 \| 4; auto-detected if unset |
| `EMBEDDINGS_ENABLED` | api | No | false | Enable RAG/semantic search |
| `EMBEDDINGS_PROVIDER` | api | No | ollama | ollama \| openai (future) |
| `OLLAMA_EMBEDDING_MODEL` | api | No | nomic-embed-text | Embedding model |
| `OLLAMA_EMBEDDING_BASE_URL` | api | No | - | Override Ollama URL for embeddings |
| `RAG_MAX_CHUNKS` | api | No | 5 | Max chunks for AI context |
| `RAG_CHUNK_SIZE` | api | No | 800 | Chunk size (chars) |
| `RAG_CHUNK_OVERLAP` | api | No | 100 | Chunk overlap (chars) |
| **Notifications** |
| `NOTIFICATION_EMAIL_PROVIDER` | api | No | none | smtp \| sendgrid \| none |
| `SMTP_HOST` | api | If SMTP | - | SMTP host |
| `SMTP_PORT` | api | No | 587 | SMTP port |
| `SMTP_USER` | api | If SMTP auth | - | SMTP username |
| `SMTP_PASSWORD` | api | If SMTP auth | - | SMTP password |
| `SMTP_FROM_EMAIL` | api | No | - | From address for emails |
| `SENDGRID_API_KEY` | api | If SendGrid | - | SendGrid API key |
| **Telemetry** |
| `TELEMETRY_ENABLED` | api, worker | No | false | Enable OTLP |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | api, worker | If telemetry | - | OTLP endpoint |
| `SENTRY_DSN` | api, web | No | - | Sentry DSN |
| **Feature Flags** |
| `FEATURE_FLAGS_PROVIDER` | api | No | database | database \| launchdarkly |
| `LAUNCHDARKLY_SDK_KEY` | api | If LD | - | LD key |
| **Deployment** |
| `DEPLOYMENT_MODE` | api | No | standalone | standalone \| anakatech \| white_label |
| `APP_MODE` | api | No | - | Overrides DEPLOYMENT_MODE when set |
| **Integration (Anakatech)** |
| `ENABLE_SSO` | api | No | false | SSO / shared identity |
| `ENABLE_SHARED_NAV` | api | No | false | Shared nav shell, embeddable |
| `ENABLE_SHARED_NOTIFICATIONS` | api | No | false | Shared notification center |
| `ENABLE_SHARED_ANALYTICS` | api | No | false | Forward audit/analytics events |
| `ENABLE_SHARED_BILLING` | api | No | false | Anakatech entitlement checks |
| `ENABLE_BRAND_OVERRIDES` | api | No | true | Apply branding overrides |
| `API_PUBLIC_URL` | api, web | Prod | - | Public API URL |
| `NEXT_PUBLIC_API_URL` | web | No | - | API URL for browser (e.g. https://api.authora.studio) |
| `NEXT_PUBLIC_MARKETING_URL` | web | No | https://authora.studio | Marketing site (Option 2) |
| `NEXT_PUBLIC_APP_URL` | web | No | https://app.authora.studio | App subdomain (Option 2) |
| `NEXT_PUBLIC_WEB_URL` | web | No | - | Legacy; fallback for sitemap/metadata |
| `DOMAIN_API` | caddy | Prod | api.authora.studio | API hostname for Caddy |
| `DOMAIN_MARKETING` | caddy | Prod | authora.studio | Marketing hostname (Option 2) |
| `DOMAIN_APP` | caddy | Prod | app.authora.studio | App hostname (Option 2) |
| `DOMAIN_WEB` | caddy | Prod | - | Legacy; falls back to DOMAIN_MARKETING |
| `ACME_EMAIL` | caddy | Prod | admin@authora.studio | Let's Encrypt contact |
| `LEADS_STORAGE_PATH` | web | No | ./storage/leads.jsonl | Fallback path when API unavailable |
| **Cron / Internal** |
| `CRON_SECRET` | api | Prod* | - | Secret for X-Cron-Secret header on /accountability/cron/reminders |
| **Billing** |
| `FEATURE_BILLING` | api | No | false | Enable plan limits and usage metering |
| `STRIPE_SECRET_KEY` | api | If Stripe | - | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | api | If Stripe | - | Stripe webhook signing secret |
| `STRIPE_PREMIUM_PRICE_ID` | api | If Stripe | - | Stripe Price ID for Premium |

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
- Set integration toggles: `ENABLE_SSO`, `ENABLE_SHARED_NAV`, etc.
- `API_GATEWAY_URL` for gateway routing

### White-Label
- Same as Standalone + `DEPLOYMENT_MODE=white_label`
- `ENABLE_BRAND_OVERRIDES=true` + `BRANDING_*` vars
