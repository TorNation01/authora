# AUTHORA Auth, Session & Cookie Strategy (Option 2)

How auth works across **authora.studio** (marketing), **app.authora.studio** (app), and **api.authora.studio** (API).

## Auth Model

AUTHORA uses **JWT Bearer tokens** in the `Authorization` header, stored in **localStorage** on the client. No HTTP-only cookies are used for auth.

## Implications for Subdomains

- **localStorage** is origin-scoped. Tokens stored on `app.authora.studio` are not visible to `authora.studio` or `api.authora.studio`.
- **Marketing site** (authora.studio) does not need auth. "Sign in" and "Start free" links go to `app.authora.studio/login` and `app.authora.studio/register`.
- **App** (app.authora.studio) is the only origin that stores tokens and makes authenticated API calls.
- **API** (api.authora.studio) receives requests from both marketing and app:
  - Marketing: `/api/v1/config` (public, no auth)
  - App: all API calls with `Authorization: Bearer <token>`

## CORS Configuration

The API must allow both origins in `CORS_ORIGINS`:

```bash
CORS_ORIGINS=["https://authora.studio","https://www.authora.studio","https://app.authora.studio"]
```

- `authora.studio` — For config fetch and any public API calls from marketing pages
- `app.authora.studio` — For all authenticated API calls from the app

CORS is configured with `allow_credentials=True` for cookie support (e.g. future session cookies). Current implementation uses Bearer tokens only.

## Cookie Strategy (Future)

If you add HTTP-only session cookies later:

1. Set `domain=.authora.studio` so cookies work across `authora.studio` and `app.authora.studio`
2. Ensure `SameSite=Lax` or `Strict` for CSRF protection
3. Use `Secure` in production
4. API must send `Access-Control-Allow-Credentials: true` and CORS must include the exact origins (no `*`)

## API Client Base URLs

- **Next.js rewrites**: `/api/v1/*` is rewritten to `NEXT_PUBLIC_API_URL` (or `API_URL` server-side)
- **Direct fetch**: When `NEXT_PUBLIC_API_URL` is set, the client fetches `https://api.authora.studio/api/v1/*` directly
- **Same-origin**: When unset (local dev), client uses same-origin `/api/v1/*` via Next.js rewrites

## Auth Callback URLs

- **Login/Register**: After success, user stays on `app.authora.studio` and is redirected to `/dashboard`
- **Logout**: Redirects to `https://authora.studio` (marketing) when `getMarketingBaseUrl()` returns a value
- **OAuth/SSO** (if enabled): Redirect URIs must include `https://app.authora.studio/sso` (or equivalent callback path)

## Magic Links / Email Links

If emails contain action links (e.g. password reset):

- Use `NEXT_PUBLIC_APP_URL` (https://app.authora.studio) for app action links
- Use `NEXT_PUBLIC_MARKETING_URL` (https://authora.studio) for marketing-only links

## Local Development

- No subdomain separation. All paths work on `localhost:3000`
- `getAppBaseUrl()` and `getMarketingBaseUrl()` return empty string on localhost → relative paths used
- Middleware skips host-based redirects for localhost/127.0.0.1
