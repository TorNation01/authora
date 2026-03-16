# AUTHORA on Cloudflare

Deploy AUTHORA behind Cloudflare for DDoS protection, CDN, and optional Workers.

## Architecture Options

### Option 1: Cloudflare Tunnel (recommended)

Run AUTHORA on a VPS or bare metal, expose via Cloudflare Tunnel. No open ports.

1. Install `cloudflared` on your server
2. Create a tunnel: `cloudflared tunnel create authora`
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
  - service: http_status:404
```

4. Run: `cloudflared tunnel run authora`
5. In Cloudflare Dashboard: DNS → CNAME api.authora.studio → your-tunnel-id.cfargotunnel.com

### Option 2: Cloudflare Proxy (orange cloud)

Point your domain to your server IP. Cloudflare proxies traffic.

1. Add A record: `api.authora.studio` → your server IP
2. Add A record: `authora.studio` → your server IP
3. Enable proxy (orange cloud)
4. SSL/TLS mode: Full (strict) if you have origin certs, or Full
5. Run Caddy/Nginx with Let's Encrypt on origin

### Option 3: Cloudflare Pages + Workers (future)

- Frontend on Cloudflare Pages
- API on Workers or external origin
- Requires architecture changes for serverless

## Environment Variables

When behind Cloudflare, ensure:

```
NEXT_PUBLIC_API_URL=https://api.authora.studio
CORS_ORIGINS=["https://authora.studio","https://www.authora.studio","https://app.authora.studio"]
```

## Cloudflare Settings

- **SSL/TLS**: Full (strict) with origin certificate, or Full
- **Always Use HTTPS**: On
- **Minimum TLS**: 1.2
- **Under Attack Mode**: Enable during DDoS
- **Rate Limiting**: Consider rules for /api/v1/auth/login

## Headers

Cloudflare adds `CF-Connecting-IP`. If using Nginx/Caddy, ensure `X-Forwarded-For` and `X-Forwarded-Proto` are passed to the app.
