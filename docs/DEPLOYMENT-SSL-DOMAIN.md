# AUTHORA SSL and Domain Setup

---

## 1. Domain Setup

### DNS Records

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | api | Your server IP | Yes (Cloudflare) or No |
| A | app | Your server IP | Yes or No |

For Caddy + Let’s Encrypt, port 80 must be reachable (or use DNS-01).

### .env Configuration

```env
DOMAIN_API=api.yourdomain.com
DOMAIN_WEB=app.yourdomain.com
ACME_EMAIL=admin@yourdomain.com
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
CORS_ORIGINS=["https://app.yourdomain.com"]
```

---

## 2. SSL with Caddy (Automatic)

Caddy obtains and renews Let’s Encrypt certs automatically.

```bash
# Generate Caddyfile from .env
./scripts/generate-caddyfile.sh

# Start stack (Caddy will request certs on first request)
npm run deploy:prod
```

Caddy stores certs in `caddy_data` volume. No manual cert steps.

---

## 3. SSL with Nginx (Manual)

If using Nginx instead of Caddy:

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certs
sudo certbot --nginx -d api.yourdomain.com -d app.yourdomain.com
```

Example Nginx config:

```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 4. HTTP → HTTPS Redirect

Caddy redirects HTTP to HTTPS by default. For Nginx:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com app.yourdomain.com;
    return 301 https://$host$request_uri;
}
```

---

## 5. HSTS

Caddy adds `Strict-Transport-Security` when serving HTTPS. For Nginx:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```
