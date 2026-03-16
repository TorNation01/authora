# AUTHORA Production Domain — Final Summary

Consolidated reference for production deployment with **authora.studio**, **app.authora.studio**, **api.authora.studio**.

---

## 1. Final Domain Architecture Summary

| Hostname | Purpose | Service | Port |
|----------|---------|---------|------|
| **authora.studio** | Public marketing site | Next.js | 3000 |
| **app.authora.studio** | Main logged-in application | Next.js | 3000 |
| **api.authora.studio** | Backend API | FastAPI | 8000 |
| **www.authora.studio** | Redirect only | 301 → authora.studio | — |

**Routing:** Marketing on authora.studio; app paths redirect to app.authora.studio. App on app.authora.studio; marketing paths redirect to authora.studio. Local dev: no redirects.

---

## 2. Final DNS Record Summary

| Type | Name | Content | Notes |
|------|------|---------|-------|
| A | @ | YOUR_SERVER_IP | Root |
| A | api | YOUR_SERVER_IP | API subdomain |
| A | app | YOUR_SERVER_IP | App subdomain |
| CNAME | www | authora.studio | Redirect target |

**Cloudflare:** Enable proxy (orange cloud). SSL: Full (strict).

**Tunnel:** CNAME @, api, app → YOUR_TUNNEL_ID.cfargotunnel.com.

---

## 3. Final Reverse Proxy Summary

**Caddy (recommended):** Run `./scripts/generate-caddyfile.sh`. Auto-HTTPS, gzip, X-Forwarded-* headers.

**Nginx:** See `nginx/authora.conf`. HTTP→HTTPS redirect, `proxy_buffering off` for API streaming, `proxy_read_timeout 300s`.

**Mappings:**
- api.authora.studio → localhost:8000 (API)
- authora.studio, app.authora.studio → localhost:3000 (Next.js)
- www.authora.studio → 301 to authora.studio

---

## 4. Final SSL/HTTPS Summary

**Caddy:** Automatic Let's Encrypt. No manual steps if DNS correct and port 80 open.

**Nginx + Certbot:**
```bash
sudo certbot --nginx -d api.authora.studio -d authora.studio -d app.authora.studio -d www.authora.studio
```

**Cloudflare:** Full (strict). Origin needs valid cert.

---

## 5. Final Cloudflare Summary

- **DNS:** A records, proxy enabled
- **SSL:** Full (strict)
- **Cache:** Bypass for api.authora.studio, app.authora.studio
- **Cache:** Standard for authora.studio static assets (/_next/static/*)
- **Headers:** X-Forwarded-For, CF-Connecting-IP forwarded
- **Tunnel:** Optional; no open ports

---

## 6. Exact Environment Variable Examples

```bash
# Frontend
NEXT_PUBLIC_API_URL=https://api.authora.studio
NEXT_PUBLIC_MARKETING_URL=https://authora.studio
NEXT_PUBLIC_APP_URL=https://app.authora.studio
NEXT_PUBLIC_DEPLOYMENT_MODE=standalone

# API
CORS_ORIGINS=["https://authora.studio","https://www.authora.studio","https://app.authora.studio"]
API_URL=http://api:8000

# Caddy
DOMAIN_API=api.authora.studio
DOMAIN_MARKETING=authora.studio
DOMAIN_APP=app.authora.studio
ACME_EMAIL=admin@authora.studio
```

---

## 7. Exact Go-Live Validation Checklist

```bash
# DNS
dig authora.studio +short
dig api.authora.studio +short
dig app.authora.studio +short

# SSL
curl -sI https://api.authora.studio/health
curl -sI https://authora.studio
curl -sI https://app.authora.studio

# Redirects
curl -sI http://authora.studio | grep -i location
curl -sI https://www.authora.studio | grep -i location

# Full verification
./scripts/verify-go-live.sh https://api.authora.studio https://authora.studio https://app.authora.studio
```

**Manual:** Marketing loads; Sign in → app; Login/register works; Dashboard loads; Logout → marketing; No mixed content; CORS allows app and marketing.

---

## Documentation Index

| Doc | Purpose |
|-----|---------|
| [DOMAIN_ARCHITECTURE.md](DOMAIN_ARCHITECTURE.md) | Routing, service mapping, scale path |
| [DNS_SETUP.md](DNS_SETUP.md) | DNS records, TTL, Cloudflare |
| [REVERSE_PROXY_SETUP.md](REVERSE_PROXY_SETUP.md) | Caddy/Nginx configuration |
| [SSL_AND_HTTPS.md](SSL_AND_HTTPS.md) | HTTPS setup |
| [CLOUDFLARE_SETUP.md](CLOUDFLARE_SETUP.md) | Cloudflare configuration |
| [SUBDOMAIN_AUTH_AND_COOKIES.md](SUBDOMAIN_AUTH_AND_COOKIES.md) | Auth, CORS, cookies |
| [GO_LIVE_DOMAIN_CHECKLIST.md](GO_LIVE_DOMAIN_CHECKLIST.md) | Go-live validation |
