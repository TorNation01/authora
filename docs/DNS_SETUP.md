# AUTHORA DNS Setup

Recommended DNS configuration for **authora.studio**, **app.authora.studio**, **api.authora.studio**, **www.authora.studio**.

## Single-Server Deployment (All Hostnames → One IP)

### Option A: A Records (Recommended for Root)

| Type | Name | Content | TTL | Proxy |
|------|------|---------|-----|-------|
| A | @ | `YOUR_SERVER_IP` | 300 | Optional |
| A | api | `YOUR_SERVER_IP` | 300 | Optional |
| A | app | `YOUR_SERVER_IP` | 300 | Optional |
| CNAME | www | authora.studio | 300 | Optional |

**Note:** Root (@) often requires A or AAAA. Subdomains can use A or CNAME.

### Option B: AAAA for IPv6

| Type | Name | Content | TTL |
|------|------|---------|-----|
| AAAA | @ | `YOUR_IPV6` | 300 |
| AAAA | api | `YOUR_IPV6` | 300 |
| AAAA | app | `YOUR_IPV6` | 300 |

### Option C: CNAME for Subdomains (If Using CDN/LB)

| Type | Name | Content | TTL |
|------|------|---------|-----|
| A | @ | `YOUR_SERVER_IP` | 300 |
| CNAME | api | `your-server.example.com` or LB | 300 |
| CNAME | app | `your-server.example.com` or LB | 300 |
| CNAME | www | authora.studio | 300 |

## Cloudflare Proxy Recommendations

When using Cloudflare in front of your server:

1. **Add records** as above (A or CNAME).
2. **Enable proxy** (orange cloud) for DDoS protection and CDN.
3. **SSL/TLS mode:** Full (strict) — Cloudflare terminates SSL, connects to origin via HTTPS.
4. **Origin server:** Must have valid SSL or use Cloudflare Origin Certificate.

### Cloudflare DNS (Proxied)

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | @ | `YOUR_SERVER_IP` | Proxied |
| A | api | `YOUR_SERVER_IP` | Proxied |
| A | app | `YOUR_SERVER_IP` | Proxied |
| CNAME | www | authora.studio | Proxied |

## TTL Guidance

| Phase | TTL | Reason |
|-------|-----|--------|
| **Pre-launch / testing** | 60–300 | Quick changes during setup |
| **Production stable** | 3600 (1 hr) | Balance propagation vs flexibility |
| **Long-term stable** | 86400 (24 hr) | Reduce DNS load |

## Cloudflare Tunnel (No Open Ports)

When using Cloudflare Tunnel instead of A records:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | @ | `YOUR_TUNNEL_ID.cfargotunnel.com` | Proxied |
| CNAME | api | `YOUR_TUNNEL_ID.cfargotunnel.com` | Proxied |
| CNAME | app | `YOUR_TUNNEL_ID.cfargotunnel.com` | Proxied |
| CNAME | www | authora.studio | Proxied |

Tunnel `config.yml` routes by hostname to localhost:3000 (web) or localhost:8000 (API).

## www Redirect Target

- **www.authora.studio** → CNAME to `authora.studio` (or A to same IP).
- Reverse proxy handles 301 redirect: `www.authora.studio` → `https://authora.studio{uri}`.

## Verification

```bash
# After DNS propagation (wait TTL or use short TTL during setup)
dig authora.studio +short
dig api.authora.studio +short
dig app.authora.studio +short
dig www.authora.studio +short
```

All should return your server IP (or Cloudflare IPs if proxied).

## Moving to Split Infrastructure Later

1. **API on separate host:** Change `api` A/CNAME to new API server or load balancer.
2. **App on separate host:** Change `app` A/CNAME to new app server.
3. **Marketing on CDN:** Change `@` and `www` to CDN CNAME (e.g. Cloudflare Pages).
4. **No app code changes** if hostnames stay the same; only DNS targets change.
