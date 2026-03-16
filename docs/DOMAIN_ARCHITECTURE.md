# AUTHORA Domain Architecture

Production domain structure for **authora.studio**.

## Hostnames

| Hostname | Purpose | Service | Port |
|----------|---------|---------|------|
| **authora.studio** | Public marketing site | Next.js | 3000 |
| **app.authora.studio** | Main logged-in application | Next.js | 3000 |
| **api.authora.studio** | Backend API | FastAPI | 8000 |
| **www.authora.studio** | Redirect only | — | 301 → authora.studio |

## Routing Responsibilities

### authora.studio (Marketing)
- **Serves:** `/`, `/features`, `/pricing`, `/faq`, `/contact`, `/demo`, `/terms`, `/privacy`
- **Redirects:** `/dashboard`, `/login`, `/register`, `/sso`, `/setup`, `/onboarding` → `app.authora.studio`
- **Public surface:** Marketing content, SEO, lead capture, newsletter signup

### app.authora.studio (Application)
- **Serves:** `/dashboard`, `/login`, `/register`, `/sso`, `/setup`, `/onboarding`, and all app routes
- **Redirects:** `/` → `/dashboard`; marketing paths → `authora.studio`
- **Private surface:** Authenticated app; requires login for dashboard

### api.authora.studio (API)
- **Serves:** `/api/v1/*`, `/health`, `/health/ready`, `/api/docs`
- **Public endpoints:** `/api/v1/config`, `/api/v1/leads` (no auth)
- **Private endpoints:** All others require `Authorization: Bearer <token>`

### www.authora.studio
- **Redirects:** All requests → `https://authora.studio{uri}` (301 permanent)

## Service Mapping (Single-Server)

```
                    ┌─────────────────────────────────────────┐
                    │           Reverse Proxy (Caddy/Nginx)     │
                    │            Ports 80, 443                 │
                    └─────────────────────────────────────────┘
                                        │
         ┌──────────────────────────────┼──────────────────────────────┐
         │                              │                              │
         ▼                              ▼                              ▼
┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
│ authora.studio  │          │ app.authora.    │          │ api.authora.     │
│ www.authora.    │          │ studio          │          │ studio           │
│ (redirect)      │          │                 │          │                  │
└────────┬────────┘          └────────┬────────┘          └────────┬────────┘
         │                            │                            │
         └────────────────────────────┼────────────────────────────┘
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
                ┌─────────────────┐       ┌─────────────────┐
                │ Next.js (web)   │       │ FastAPI (api)   │
                │ localhost:3000  │       │ localhost:8000  │
                └─────────────────┘       └─────────────────┘
```

## Public vs Private Surface Area

| Surface | Hostname | Paths | Auth |
|---------|----------|-------|------|
| **Public** | authora.studio | /, /features, /pricing, /faq, /contact, /demo, /terms, /privacy | None |
| **Public** | api.authora.studio | /health, /health/ready, /api/v1/config, /api/v1/leads | None |
| **Private** | app.authora.studio | /dashboard/*, /login, /register, /setup, /onboarding | JWT for dashboard |
| **Private** | api.authora.studio | /api/v1/* (except config, leads) | Bearer token |

## Future Scale Path

If app and API split onto separate hosts later:

1. **API scaling:** Point `api.authora.studio` DNS to a load balancer or API cluster. No app changes if `NEXT_PUBLIC_API_URL` stays `https://api.authora.studio`.
2. **App scaling:** Point `app.authora.studio` to a separate Next.js deployment. Ensure CORS includes the new origin if different.
3. **Marketing CDN:** Point `authora.studio` to Cloudflare Pages or a CDN for static marketing. Keep `app.authora.studio` and `api.authora.studio` on origin.
4. **DNS:** Use CNAME for each subdomain to its respective target. A records can become CNAME to LB/CDN.

## Local Development

- **No subdomain separation.** All paths work on `localhost:3000`.
- Middleware skips host-based redirects for `localhost` and `127.0.0.1`.
- `getAppBaseUrl()` and `getMarketingBaseUrl()` return empty string → relative paths.

## See Also

- [PRODUCTION_DOMAIN_SUMMARY.md](PRODUCTION_DOMAIN_SUMMARY.md) — Consolidated final summary
- [DNS_SETUP.md](DNS_SETUP.md) — DNS records and Cloudflare
- [REVERSE_PROXY_SETUP.md](REVERSE_PROXY_SETUP.md) — Caddy/Nginx configuration
- [SSL_AND_HTTPS.md](SSL_AND_HTTPS.md) — HTTPS setup
- [CLOUDFLARE_SETUP.md](CLOUDFLARE_SETUP.md) — Cloudflare configuration
- [SUBDOMAIN_AUTH_AND_COOKIES.md](SUBDOMAIN_AUTH_AND_COOKIES.md) — Auth and CORS
- [GO_LIVE_DOMAIN_CHECKLIST.md](GO_LIVE_DOMAIN_CHECKLIST.md) — Go-live validation
