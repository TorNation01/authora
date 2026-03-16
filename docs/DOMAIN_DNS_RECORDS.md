# AUTHORA DNS Records (Option 2)

Recommended DNS configuration for **authora.studio**, **app.authora.studio**, **api.authora.studio**.

## Direct A/CNAME (No Tunnel)

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | Your server IP | 300 |
| A | api | Your server IP | 300 |
| A | app | Your server IP | 300 |
| CNAME | www | authora.studio | 300 |

Or with CNAME (if using a CDN/host that provides a CNAME target):

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | @ | your-cdn-or-host | 300 |
| CNAME | api | your-cdn-or-host | 300 |
| CNAME | app | your-cdn-or-host | 300 |
| CNAME | www | authora.studio | 300 |

## Cloudflare Tunnel

| Type | Name | Value | Proxy |
|------|------|-------|-------|
| CNAME | @ | your-tunnel-id.cfargotunnel.com | Proxied |
| CNAME | api | your-tunnel-id.cfargotunnel.com | Proxied |
| CNAME | app | your-tunnel-id.cfargotunnel.com | Proxied |
| CNAME | www | authora.studio | Proxied |

All hostnames point to the same tunnel; the tunnel's `config.yml` routes by hostname to the correct service.

## Verification

```bash
# After DNS propagation
dig authora.studio +short
dig api.authora.studio +short
dig app.authora.studio +short
dig www.authora.studio +short
```

All should return your server IP (or Cloudflare IPs if using Cloudflare proxy).
