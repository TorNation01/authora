# AUTHORA Admin Guide

For administrators managing AUTHORA deployments.

## Related Documentation

- [Deployment](DEPLOYMENT.md) – Deploy and run AUTHORA
- [Security](SECURITY.md) – Security practices
- [Monitoring](MONITORING.md) – Health checks and metrics
- [Logging](LOGGING.md) – Log configuration
- [ENV-MAP](ENV-MAP.md) – Environment variables

## Initial Setup

### Standalone Mode

1. Run the setup wizard: `./scripts/setup-wizard.mjs` or `npm run setup`
2. Create the first admin user when prompted
3. Configure `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL` in `.env`

### SSO / Anakatech Mode

1. Configure IdP (OAuth/OIDC) and set `NEXT_PUBLIC_SSO_*` variables
2. Set `NEXT_PUBLIC_DEPLOYMENT_MODE=anakatech` if embedding
3. See [INTEGRATION.md](INTEGRATION.md) for API contracts

## User Management

### Local Auth (Standalone)

- Users register at `/register`
- Admin creation: `local_admin_creation` feature flag enables first-user-as-admin
- **Profile edit**: Users can update display name and password in Dashboard → Settings
- **Password reset**: Not implemented. Users who forget password must be reset by admin (update `hashed_password` in DB or re-seed)

### SSO

- Users sign in via IdP. No local passwords.
- User identity comes from IdP claims. Map to AUTHORA user records.

## Feature Flags

Configured via API `/api/v1/config` or env. Key flags:

| Flag | Description |
|------|-------------|
| `standalone_auth` | Local login/register |
| `standalone_landing` | Marketing landing page |
| `sso_ready` | SSO login enabled |
| `billing` | Billing/pricing features |
| `embeddable_shell` | Hide sidebar for embedded use |

## Content & Branding

- **Product name, tagline**: Set in config/branding
- **Logo, favicon**: URLs in branding config
- **Help content**: Edit `apps/web/src/content/help-center.ts` and `tooltips.ts`

## Maintenance

- **Backups**: See [BACKUP-RESTORE.md](BACKUP-RESTORE.md)
- **Migrations**: `alembic upgrade head` in API container
- **Secrets rotation**: Update `SECRET_KEY`, re-issue tokens; users re-login

## Incident Response

See [INCIDENT-RECOVERY.md](INCIDENT-RECOVERY.md) for runbooks.
