# AUTHORA Reverse Proxy Setup

Production reverse proxy configuration for **authora.studio**, **app.authora.studio**, **api.authora.studio**, **www.authora.studio**.

## Overview

| Hostname | Backend | Port |
|----------|---------|------|
| authora.studio | Next.js (web) | 3000 |
| app.authora.studio | Next.js (web) | 3000 |
| api.authora.studio | FastAPI (api) | 8000 |
| www.authora.studio | 301 redirect to authora.studio | — |

## Caddy (Recommended)

### Generate from .env

```bash
./scripts/generate-caddyfile.sh
```

### Full Caddyfile (Production)

```caddyfile
# AUTHORA - authora.studio production
# Caddy auto-provisions HTTPS via Let's Encrypt

{
    email admin@authora.studio
}

# API - supports streaming responses
api.authora.studio {
    reverse_proxy api:8000 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-For {remote_host}
        header_up Host {host}
    }
    encode gzip
}

# Marketing
authora.studio {
    reverse_proxy web:3000 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-For {remote_host}
        header_up Host {host}
    }
    encode gzip
}

# App
app.authora.studio {
    reverse_proxy web:3000 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-For {remote_host}
        header_up Host {host}
    }
    encode gzip
}

# www redirect
www.authora.studio {
    redir https://authora.studio{uri} permanent
}
```

### Caddy Features

- **Automatic HTTPS:** Let's Encrypt via ACME; no manual cert steps.
- **HTTP→HTTPS:** Automatic redirect.
- **Streaming:** Caddy passes through streaming responses by default.
- **Gzip:** `encode gzip` compresses responses.
- **Cloudflare:** Use `X-Forwarded-For` and `X-Forwarded-Proto`; Caddy forwards these.

### Caddy Logging

Default access log to stdout. For file logging:

```caddyfile
{
    log {
        output file /var/log/caddy/access.log
        format json
    }
}
```

## Nginx (Alternative)

### Full Configuration

See `nginx/authora.conf`. Summary:

```nginx
# Upstreams
upstream authora_api {
    server 127.0.0.1:8000;
}

upstream authora_web {
    server 127.0.0.1:3000;
}

# api.authora.studio - HTTP redirect + HTTPS
server {
    listen 80;
    server_name api.authora.studio;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.authora.studio;
    ssl_certificate /etc/letsencrypt/live/api.authora.studio/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.authora.studio/privkey.pem;

    location / {
        proxy_pass http://authora_api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_read_timeout 300s;
    }
}

# authora.studio, app.authora.studio - similar blocks
# www.authora.studio - 301 redirect
```

### Nginx: Streaming Support

API uses `StreamingResponse` for AI completion. Add:

```nginx
proxy_buffering off;
proxy_read_timeout 300s;
```

### Nginx: Security Headers

```nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Nginx: Health Check Endpoints

Health endpoints pass through to the API:

- `https://api.authora.studio/health`
- `https://api.authora.studio/health/ready`

## Static Assets

- **Next.js:** Serves `/_next/static/*` and static files. Proxy passes through.
- **API:** No static asset serving; all dynamic.

## WebSocket / Streaming

- **WebSockets:** Not used by AUTHORA. If added, Nginx needs `proxy_http_version 1.1` and `proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade";`
- **HTTP Streaming:** AI endpoints use `StreamingResponse`. Caddy and Nginx (with `proxy_buffering off`) support this.

## Docker Compose

```yaml
caddy:
  image: caddy:2-alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./caddy/Caddyfile:/etc/caddy/Caddyfile
    - caddy_data:/data
    - caddy_config:/config
  depends_on:
    - api
    - web
```

Use hostnames `api`, `web` as Docker service names in `reverse_proxy api:8000` and `reverse_proxy web:3000`.
