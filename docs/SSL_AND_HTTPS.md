# AUTHORA SSL & HTTPS Setup

Production HTTPS configuration for **authora.studio**, **app.authora.studio**, **api.authora.studio**.

## Requirements

- Secure all three production hostnames
- Redirect HTTP → HTTPS
- Support Cloudflare-compatible SSL modes
- Document certificate issuance and renewal

## Caddy (Automatic HTTPS)

### Behavior

- Caddy obtains and renews Let's Encrypt certificates automatically.
- HTTP requests are redirected to HTTPS.
- No manual cert steps if DNS points to the server before Caddy starts.

### Prerequisites

1. DNS A/CNAME for `api.authora.studio`, `authora.studio`, `app.authora.studio` → server IP
2. Port 80 open (HTTP-01 challenge)
3. `ACME_EMAIL` set in Caddyfile global block (e.g. `admin@authora.studio`)

### Certificate Paths

Caddy stores certs in its data directory (e.g. `/data/caddy/certificates`). No manual paths needed.

### Cloudflare Interplay

- **Full (strict):** Caddy uses Let's Encrypt. Cloudflare connects to origin via HTTPS.
- **Full:** Cloudflare accepts any origin cert (not recommended).
- **Flexible:** Cloudflare terminates SSL; origin can be HTTP (not recommended for API).

## Nginx + Let's Encrypt (Certbot)

### Issuance

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificates (Nginx must be configured for server_name first, or use standalone)
sudo certbot --nginx -d api.authora.studio -d authora.studio -d app.authora.studio -d www.authora.studio
```

### Certificate Layout

- **api.authora.studio:** `/etc/letsencrypt/live/api.authora.studio/fullchain.pem`, `privkey.pem`
- **authora.studio, app.authora.studio, www.authora.studio:** Single cert with SANs → `/etc/letsencrypt/live/authora.studio/`

For a combined cert:

```bash
sudo certbot certonly --nginx -d authora.studio -d www.authora.studio -d app.authora.studio
```

### Renewal

```bash
sudo certbot renew
```

Add to crontab: `0 0 1 * * certbot renew --quiet`

## Cloudflare Origin Certificate (Optional)

If Cloudflare terminates SSL at the edge and you want encrypted origin traffic:

1. Cloudflare Dashboard → SSL/TLS → Origin Server
2. Create Certificate (15-year, Cloudflare-signed)
3. Install on origin (Nginx/Caddy)
4. Set SSL mode to **Full (strict)**

## Go-Live SSL Validation

1. **HTTP redirect:** `curl -I http://authora.studio` → 301 to `https://authora.studio`
2. **HTTPS reachable:** `curl -sI https://api.authora.studio/health` → 200
3. **Certificate valid:** `openssl s_client -connect api.authora.studio:443 -servername api.authora.studio </dev/null 2>/dev/null | openssl x509 -noout -dates`
4. **No mixed content:** Browser DevTools → Console; no HTTP resources on HTTPS pages
