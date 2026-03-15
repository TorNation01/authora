# SSL/TLS Configuration for AUTHORA

## Caddy (recommended – automatic)

Caddy auto-provisions Let's Encrypt certificates.

1. Edit `caddy/Caddyfile` with your domains
2. Ensure ports 80 and 443 are open
3. Caddy handles ACME challenge and renewal

```caddyfile
api.yourdomain.com {
    reverse_proxy api:8000
}

app.yourdomain.com {
    reverse_proxy web:3000
}
```

## Let's Encrypt with Nginx

1. Install certbot: `apt install certbot python3-certbot-nginx`
2. Get certificates: `certbot certonly --nginx -d api.yourdomain.com -d app.yourdomain.com`
3. Certificates in `/etc/letsencrypt/live/<domain>/`
4. Use `nginx/authora.conf` and update paths
5. Renewal: `certbot renew` (add to cron: `0 0 1 * * certbot renew --quiet`)

## Let's Encrypt with Docker

```bash
docker run -it --rm -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/www/html:/var/www/html certbot/certbot certonly \
  --standalone -d api.yourdomain.com -d app.yourdomain.com
```

## Cloudflare Origin Certificates

If using Cloudflare proxy (orange cloud):

1. Cloudflare Dashboard → SSL/TLS → Origin Server
2. Create Certificate (15-year, for your domain)
3. Save cert and key to server
4. Configure Nginx/Caddy to use these instead of Let's Encrypt
5. Set SSL mode to Full (strict)

## TLS Best Practices

- Use TLS 1.2 minimum (1.3 preferred)
- Enable HSTS: `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- Disable TLS 1.0 and 1.1
