# Security Hardening

Recommendations for securing AUTHORA in production.

## Secrets

### SECRET_KEY

- **Never** use the default value in production
- Generate: `openssl rand -hex 32`
- Rotate periodically; requires re-login of all users

### CRON_SECRET

If using the accountability reminders cron endpoint, set `CRON_SECRET` to a random value and pass it in the request.

### API Keys

- Store OpenAI, Anthropic, Stripe keys in `.env` only
- Never commit `.env` to version control
- Use environment-specific keys (test vs live)

## Database

- Use a strong password for PostgreSQL
- Do not expose PostgreSQL port in production (Docker prod config hides it)
- Prefer managed PostgreSQL with encryption at rest

## Network

- Expose only ports 80 and 443 (Caddy) in production
- Use a firewall (e.g., `ufw`) to restrict access
- Consider a WAF for DDoS and common attacks

## Caddy / Reverse Proxy

The generated Caddyfile includes:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `-Server` (removes Server header)

## CORS

Set `CORS_ORIGINS` to your exact production domains. Avoid wildcards in production.

## HTTPS

- Always use HTTPS in production
- Caddy obtains Let's Encrypt certificates automatically
- Ensure `NEXT_PUBLIC_API_URL` and related URLs use `https://`

## Updates

- Keep Docker images and base images updated
- Run `./scripts/update.sh prod` regularly
- Monitor security advisories for dependencies

## Backups

- Encrypt backups at rest
- Store backups off-server
- Test restore procedures
