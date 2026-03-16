# AUTHORA Go-Live Domain Checklist

Validation steps for domain launch with **authora.studio**, **app.authora.studio**, **api.authora.studio**.

## 1. DNS Resolution Checks

```bash
# All should return your server IP (or Cloudflare IPs if proxied)
dig authora.studio +short
dig api.authora.studio +short
dig app.authora.studio +short
dig www.authora.studio +short
```

- [ ] authora.studio resolves
- [ ] api.authora.studio resolves
- [ ] app.authora.studio resolves
- [ ] www.authora.studio resolves

## 2. SSL Checks

```bash
# Certificate valid
openssl s_client -connect api.authora.studio:443 -servername api.authora.studio </dev/null 2>/dev/null | openssl x509 -noout -dates

# HTTPS reachable
curl -sI https://api.authora.studio/health
curl -sI https://authora.studio
curl -sI https://app.authora.studio
```

- [ ] api.authora.studio — valid cert, HTTPS 200
- [ ] authora.studio — valid cert, HTTPS 200
- [ ] app.authora.studio — valid cert, HTTPS 200

## 3. Redirect Checks

```bash
# HTTP → HTTPS
curl -sI http://authora.studio | grep -i location
# Expect: 301/302 to https://authora.studio

# www → apex
curl -sI https://www.authora.studio | grep -i location
# Expect: 301 to https://authora.studio
```

- [ ] HTTP redirects to HTTPS
- [ ] www.authora.studio redirects to authora.studio

## 4. Marketing Site Checks

- [ ] https://authora.studio loads
- [ ] https://authora.studio/features loads
- [ ] https://authora.studio/pricing loads
- [ ] "Sign in" links to https://app.authora.studio/login
- [ ] "Start free" links to https://app.authora.studio/register
- [ ] No mixed content (DevTools → Console)

## 5. App Login Checks

- [ ] https://app.authora.studio loads (redirects to /dashboard)
- [ ] https://app.authora.studio/login loads
- [ ] Login works; redirects to /dashboard
- [ ] Register works; redirects to /onboarding
- [ ] Dashboard loads after login
- [ ] Logout redirects to https://authora.studio

## 6. API Health Checks

```bash
curl -sf https://api.authora.studio/health
# Expect: {"status":"ok","app":"AUTHORA"}

curl -sf https://api.authora.studio/health/ready
# Expect: {"status":"ready","checks":{"database":true,"redis":true}}
```

- [ ] /health returns 200
- [ ] /health/ready returns 200 when DB/Redis up

## 7. CORS Verification

```bash
./scripts/verify-go-live.sh https://api.authora.studio https://authora.studio https://app.authora.studio
```

Or manual:

```bash
curl -sI -X OPTIONS https://api.authora.studio/api/v1/config \
  -H "Origin: https://app.authora.studio" \
  -H "Access-Control-Request-Method: GET"
# Expect: Access-Control-Allow-Origin in response
```

- [ ] CORS allows authora.studio
- [ ] CORS allows app.authora.studio

## 8. Cookie / Session Verification

- [ ] Login on app.authora.studio; token stored (localStorage)
- [ ] API calls from app include Authorization header
- [ ] Logout clears tokens

## 9. Email Link Verification

If email notifications are enabled:

- [ ] Reminder emails use correct base URL (app.authora.studio for app links)
- [ ] Links open in browser and work

## 10. Cloudflare Behavior Verification

If using Cloudflare:

- [ ] Cache bypass for api.authora.studio
- [ ] Cache bypass for app.authora.studio
- [ ] Cache rules for authora.studio static assets (optional)
- [ ] SSL mode: Full (strict)
- [ ] Real IP forwarded (X-Forwarded-For / CF-Connecting-IP)

## 11. Cache Behavior Verification

- [ ] App and API responses not cached (Cache-Control or Cloudflare Bypass)
- [ ] Marketing static assets cached where appropriate

## 12. Streaming Verification

If AI streaming is used:

- [ ] AI completion streams correctly (no buffering/timeout)
- [ ] No 502/504 on long-running streams

## Quick Command

```bash
./scripts/verify-go-live.sh https://api.authora.studio https://authora.studio https://app.authora.studio
```

## Post-Go-Live

- [ ] Monitor error logs
- [ ] Monitor SSL cert expiry (Caddy auto-renews; Certbot: `certbot renew`)
- [ ] Set up uptime monitoring (e.g. health endpoint every 5 min)
