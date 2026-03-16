# First-Run Setup Wizard

The setup wizard guides you through initial configuration when AUTHORA is first deployed.

## Access

Visit **http://localhost:3000/setup** (or your domain) after the application is running. The wizard is only available in standalone mode and when setup is not yet complete.

## Steps

| Step | Description |
|------|-------------|
| **Site Name** | Product name and tagline |
| **Domain & SSL** | Domain and HTTPS expectation |
| **Database** | PostgreSQL connection URL |
| **Redis** | Redis connection URL |
| **Admin Account** | First admin email, password, display name |
| **Email** | Optional SMTP configuration |
| **Storage** | Local, S3, or R2 |
| **AI Provider** | OpenAI, Anthropic, or Ollama |
| **Stripe** | Optional billing integration |
| **Backup & Preferences** | Backup, reminders, analytics |
| **Launch** | Apply config and complete setup |

## Connection Testing

- **Database** – Test PostgreSQL connectivity before applying
- **Redis** – Test Redis connectivity
- **Ollama** – Test Ollama connection when using local AI

## What Gets Applied

The wizard writes configuration to `.env` and can:

- Run database migrations
- Seed starter templates
- Create the first admin user
- Set `setup_complete` in settings

## After Completion

1. You are redirected to `/login`
2. Sign in with the admin credentials you created
3. The setup wizard is no longer accessible (setup complete)

## Re-running Setup

If you need to re-run setup (e.g., after a fresh install), ensure:

- `setup_complete` is not set in settings, or
- No users exist in the database

The wizard checks `/api/v1/setup/status` to determine if setup is complete.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/setup/status` | GET | Check if setup is complete |
| `/api/v1/setup/test` | POST | Test DB, Redis, Ollama |
| `/api/v1/setup/apply` | POST | Write config to .env |
| `/api/v1/setup/finalize` | POST | Migrate, seed, create admin |
