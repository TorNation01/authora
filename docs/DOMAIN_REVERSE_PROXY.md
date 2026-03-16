# AUTHORA Reverse Proxy / Domain Setup (Option 2)

Reverse proxy configuration for **authora.studio** (marketing), **app.authora.studio** (app), **api.authora.studio** (API).

## Caddy (Recommended)

### Generate from .env

```bash
# Set in .env:
# DOMAIN_API=api.authora.studio
# DOMAIN_MARKETING=authora.studio
# DOMAIN_APP=app.authora.studio
# ACME_EMAIL=admin@authora.studio

./scripts/generate-caddyfile.sh
```

### Generated Caddyfile

```caddyfile
{
    email admin@authora.studio
}

api.authora.studio {
    reverse_proxy api:8000
    encode gzip
}

authora.studio {
    reverse_proxy web:3000
    encode gzip
}

app.authora.studio {
    reverse_proxy web:3000
    encode gzip
}

www.authora.studio {
    redir https://authora.studio{uri} permanent
}
```

### SSL

Caddy auto-provisions Let's Encrypt certificates. Ensure:

- Ports 80 and 443 are open
- DNS A/CNAME records point to the server for all three hostnames before starting Caddy
- `ACME_EMAIL` is valid for certificate notifications

## Nginx (Alternative)

See `nginx/authora.conf` for full config. Summary:

- `api.authora.studio` → `http://127.0.0.1:8000`
- `authora.studio` → `http://127.0.0.1:3000`
- `app.authora.studio` → `http://127.0.0.1:3000`
- `www.authora.studio` → 301 redirect to `authora.studio`

Certbot: `sudo certbot --nginx -d api.authora.studio -d authora.studio -d app.authora.studio -d www.authora.studio`

## Cloudflare

### Option A: Cloudflare Tunnel (No Open Ports)

1. Install `cloudflared` and create a tunnel
2. Configure `config.yml`:

```yaml
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

3. DNS: CNAME all hostnames to `your-tunnel-id.cfargotunnel.com`
4. Cloudflare terminates SSL

### Option B: Cloudflare Proxy (A Records)

1. Add A records: `api.authora.studio`, `authora.studio`, `app.authora.studio` → your server IP
2. Enable Cloudflare proxy (orange cloud)
3. SSL/TLS mode: Full (strict) or Full
4. Run Caddy or Nginx on the server for origin SSL

## Docker Compose

Ensure `caddy` service uses the generated Caddyfile and ports 80/443 are published:

```yaml
caddy:
  image: caddy:latest
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./caddy/Caddyfile:/etc/caddy/Caddyfile
  depends_on:
    - api
    - web
```
