# AUTHORA Cloudflare Setup

Configure AUTHORA for Cloudflare in front of your deployment.

## DNS Proxy Recommendations

- **Enable proxy (orange cloud)** for DDoS protection and CDN.
- **Records:** A or CNAME for `@`, `api`, `app` → your server IP or tunnel.
- **www:** CNAME to `authora.studio` (proxied).

## SSL Mode Recommendation

| Mode | Use Case |
|------|----------|
| **Full (strict)** | Recommended. Cloudflare → origin via HTTPS. Origin needs valid cert (Let's Encrypt or Cloudflare Origin). |
| Full | Cloudflare → origin HTTPS; accepts any origin cert. |
| Flexible | Cloudflare terminates SSL; origin HTTP. Not recommended for API. |

**Recommendation:** Full (strict) with Let's Encrypt on origin.

## Caching Considerations

### Bypass / No-Cache (App & API)

- **app.authora.studio:** All paths dynamic. Add Page Rule or Cache Rule: `app.authora.studio/*` → Cache Level: Bypass.
- **api.authora.studio:** All paths dynamic. Add: `api.authora.studio/*` → Cache Level: Bypass.

### Cache (Marketing / Static)

- **authora.studio:** Marketing pages can be cached. Static assets (`/_next/static/*`, images) benefit from cache.
- **Cache rules:** 
  - `authora.studio/_next/static/*` → Cache Level: Standard, Edge TTL 1 month
  - `authora.studio/*` → Cache Level: Standard, Edge TTL 1 hour (or Bypass for dynamic)

### Cloudflare Cache Rules (Configurable)

1. Dashboard → Caching → Cache Rules
2. Create rule: If hostname equals `api.authora.studio` → Bypass cache
3. Create rule: If hostname equals `app.authora.studio` → Bypass cache
4. Create rule: If hostname equals `authora.studio` AND URI path starts with `/_next/static/` → Cache, TTL 1 month

## Real IP / Forwarded Headers

Cloudflare sends:
- `CF-Connecting-IP` — Client IP
- `X-Forwarded-For` — Client IP (append)
- `X-Forwarded-Proto` — Original scheme (https)

Caddy and Nginx forward these. FastAPI/Next.js can use `X-Forwarded-For` for rate limiting and logging.

## Rate Limiting / Security Headers

- **Cloudflare:** Security → WAF, Rate limiting rules. Avoid blocking `/api/v1/auth/login` or `/api/v1/auth/register` with overly aggressive rules.
- **Bot protection:** "Under Attack" mode can block legitimate API clients. Use "I'm Under Attack" only during DDoS; otherwise Standard.
- **Security headers:** Cloudflare can add headers (X-Content-Type-Options, etc.). Next.js and FastAPI also set some. Avoid duplicates.

## Auth / App Behavior

- **CORS:** API must allow `https://authora.studio`, `https://app.authora.studio` in `CORS_ORIGINS`. Cloudflare does not modify CORS headers when proxying.
- **Cookies:** If using cookies, set `SameSite=Lax` or `Strict`; `Secure` in production.
- **Auth callbacks:** OAuth redirect URIs must use `https://app.authora.studio/...` (not Cloudflare URLs).

## WebSocket Compatibility

AUTHORA uses HTTP streaming, not WebSockets. If you add WebSockets later, Cloudflare supports them by default; no extra config needed.

## Cloudflare Tunnel (No Open Ports)

1. Install `cloudflared`
2. Create tunnel: `cloudflared tunnel create authora`
3. Configure `config.yml`:

```yaml
tunnel: <TUNNEL_ID>
credentials-file: /path/to/<TUNNEL_ID>.json

ingress:
  - hostname: api.authora.studio
    service: http://localhost:8000
  - hostname: authora.studio
    service: http://localhost:3000
  - hostname: app.authora.studio
    service: http://localhost:3000
  - hostname: www.authora.studio
    service: http://localhost:3000
  - service: http_status:404
```

4. DNS: CNAME all hostnames to `YOUR_TUNNEL_ID.cfargotunnel.com`
5. Run: `cloudflared tunnel run authora`

SSL is terminated at Cloudflare; no origin cert needed for tunnel.
