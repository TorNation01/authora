# Affiliate Tracking System

## How Tracking Works

1. **Affiliate link**: `https://authora.studio?aff=CODE` (or `https://authora.studio/register?aff=CODE`)
2. **Click recording**: Frontend or redirect calls `GET /api/v1/affiliates/track?aff=CODE` when the page loads with `?aff=` in the URL
3. **Attribution**: On registration, pass `affiliate_code: CODE` in the request body
4. **Conversion**: When the user pays (Stripe checkout or invoice), a conversion is created automatically

## Tracking Endpoint

```
GET /api/v1/affiliates/track?aff=CODE&landing=/pricing
```

- `aff` (required): Affiliate code
- `landing` (optional): Landing path (e.g. `/pricing`, `/`)

Records: IP (hashed), user-agent (hashed), landing path, referrer. No auth required.

## Frontend Integration

### Option A: Redirect Page

Create `/r/CODE` or `/go/CODE` that:
1. Records the click via `GET /api/v1/affiliates/track?aff=CODE`
2. Sets a cookie (e.g. `aff=CODE`, 30 days)
3. Redirects to `/` or `/register`

### Option B: Client-Side on Load

On app load, if URL has `?aff=CODE`:
1. Call `GET /api/v1/affiliates/track?aff=CODE&landing=/current-path`
2. Store `aff` in `sessionStorage` or cookie
3. On registration form submit, include `affiliate_code: CODE`

### Option C: Server-Side Redirect

If using SSR, when request has `?aff=CODE`:
1. Server calls tracking API
2. Sets `Set-Cookie: aff=CODE; Max-Age=2592000; Path=/`
3. Renders page

## Attribution Window

Default: 30 days (configurable via `cookie_days` in affiliate settings). The attribution is stored when the user registers with `affiliate_code`; there is no time-based expiry for attribution once stored.

## Tracking ID

Each click gets a unique `click_id` (UUID). Conversions are linked to the affiliate via `affiliate_attributions` (user_id → affiliate_id), not directly to a specific click. For analytics, use `affiliate_id` and `user_id` on conversions.
