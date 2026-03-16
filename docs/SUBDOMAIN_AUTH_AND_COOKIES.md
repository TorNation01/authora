# AUTHORA Subdomain Auth & Cookies

Auth, CORS, cookies, and callback URLs for **authora.studio**, **app.authora.studio**, **api.authora.studio**.

## API Base URLs

| Context | Variable | Value |
|---------|----------|-------|
| Browser (client) | `NEXT_PUBLIC_API_URL` | `https://api.authora.studio` |
| Server (Next.js API routes) | `API_URL` or `NEXT_PUBLIC_API_URL` | `https://api.authora.studio` or `http://api:8000` (Docker) |

## CORS Configuration

API must allow these origins:

```bash
CORS_ORIGINS=["https://authora.studio","https://www.authora.studio","https://app.authora.studio"]
```

- **authora.studio** — Config fetch, public API calls from marketing
- **app.authora.studio** — All authenticated API calls from app

CORS uses `allow_credentials=True` for future cookie support.

## Secure App-to-API Communication

- **Transport:** HTTPS only. All production traffic over TLS.
- **Auth:** Bearer token in `Authorization` header. No credentials in URL.
- **Credentials:** `fetch(..., { credentials: 'include' })` when using cookies; not required for Bearer.

## Cookie / Session Strategy

### Current (JWT in localStorage)

- Tokens stored in `localStorage` on `app.authora.studio`
- Origin-scoped; not shared across subdomains
- No cookies used for auth

### Future (HTTP-Only Cookies)

If switching to session cookies:

1. **Domain:** `domain=.authora.studio` — shared across `authora.studio` and `app.authora.studio`
2. **SameSite:** `Lax` or `Strict` — CSRF protection
3. **Secure:** Always in production
4. **Path:** `/` or `/api` depending on where API sets cookies
5. **CORS:** `Access-Control-Allow-Credentials: true`; origins must be explicit (no `*`)

## Auth Callback URLs

| Flow | URL |
|------|-----|
| Login success | `https://app.authora.studio/dashboard` |
| Register success | `https://app.authora.studio/onboarding` |
| Logout | `https://authora.studio` (marketing) |
| OAuth/SSO callback | `https://app.authora.studio/sso` |

## CSRF / Session Notes

- **JWT:** No CSRF for API (Bearer in header; not sent automatically)
- **Cookies:** If added, use SameSite and consider CSRF tokens for state-changing requests

## Environment Variables (Domain-Aware)

```bash
NEXT_PUBLIC_API_URL=https://api.authora.studio
NEXT_PUBLIC_MARKETING_URL=https://authora.studio
NEXT_PUBLIC_APP_URL=https://app.authora.studio
CORS_ORIGINS=["https://authora.studio","https://www.authora.studio","https://app.authora.studio"]
```

## Email / Magic Link URL Generation

For emails with action links (e.g. password reset, magic link):

- **App actions:** Use `NEXT_PUBLIC_APP_URL` → `https://app.authora.studio`
- **Marketing:** Use `NEXT_PUBLIC_MARKETING_URL` → `https://authora.studio`

Example: Password reset link = `https://app.authora.studio/reset-password?token=...`
