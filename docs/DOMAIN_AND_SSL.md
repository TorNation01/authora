# Domain and SSL Configuration

AUTHORA uses a multi-subdomain architecture (Option 2) for production.

## Domain Structure

| Subdomain | Purpose | Example |
|-----------|---------|---------|
| `authora.studio` | Marketing/landing | `yourdomain.com` |
| `app.authora.studio` | App (dashboard, auth) | `app.yourdomain.com` |
| `api.authora.studio` | API | `api.yourdomain.com` |
| `www.*` | Redirect to marketing | `www.yourdomain.com` → `yourdomain.com` |

## DNS Setup

Point your domains to your server:

```
A     yourdomain.com      → SERVER_IP
A     app.yourdomain.com  → SERVER_IP
A     api.yourdomain.com → SERVER_IP
A     www.yourdomain.com  → SERVER_IP
```

Or use CNAME records if using a load balancer or CDN.

## SSL with Caddy

Caddy automatically obtains and renews Let's Encrypt certificates. No manual certificate management is required.

### Requirements

- Ports 80 and 443 open
- Domains resolving to your server
- Valid email for ACME (Let's Encrypt)

### Configuration

Set in `.env`:

```
DOMAIN_API=api.yourdomain.com
DOMAIN_MARKETING=yourdomain.com
DOMAIN_APP=app.yourdomain.com
ACME_EMAIL=admin@yourdomain.com
```

Then run:

```bash
./scripts/generate-caddyfile.sh
```

### Caddyfile Features

The generated Caddyfile includes:

- **Automatic HTTPS** – Let's Encrypt via ACME
- **Secure headers** – X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy
- **Gzip compression** – Response compression
- **WebSocket support** – For real-time features
- **Upload limits** – 100MB default (configurable via `MAX_UPLOAD`)

## Custom SSL (Advanced)

If you have your own certificates, you can modify the Caddyfile to use them instead of ACME. See [Caddy TLS documentation](https://caddyserver.com/docs/caddyfile/directives/tls).

## Troubleshooting

### Certificate not issued
- Ensure DNS has propagated
- Check ports 80/443 are reachable
- Verify `ACME_EMAIL` is valid

### Mixed content
- Set `NEXT_PUBLIC_API_URL` to `https://` (not `http://`)
- Ensure CORS includes your production origins
