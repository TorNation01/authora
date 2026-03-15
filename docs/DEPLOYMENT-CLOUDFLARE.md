# AUTHORA Deployment with Cloudflare

Use Cloudflare as reverse proxy, DNS, and optional WAF for AUTHORA.

---

## 1. DNS Setup

1. Add your domain to Cloudflare (or use existing).
2. Create A/AAAA records:
   - `api.yourdomain.com` → your server IP
   - `app.yourdomain.com` → your server IP
3. Set proxy status to **Proxied** (orange cloud) for SSL and DDoS protection.

---

## 2. SSL (Full Strict)

With Cloudflare proxying:

- **Cloudflare → Visitor:** Automatic (Cloudflare issues cert).
- **Cloudflare → Origin:** Use **Full (strict)**.
  - Cloudflare Dashboard → SSL/TLS → Overview → set to **Full (strict)**.
  - Origin must have a valid cert (e.g. from Let’s Encrypt).

### Option A: Caddy on Origin (recommended)

Caddy auto-provisions Let’s Encrypt. Cloudflare proxies to Caddy.

1. On server: set `DOMAIN_API`, `DOMAIN_WEB`, `ACME_EMAIL` in `.env`.
2. Run `./scripts/generate-caddyfile.sh`.
3. Caddy will obtain certs; Cloudflare connects over HTTPS.

### Option B: Cloudflare Origin Certificate

1. Cloudflare Dashboard → SSL/TLS → Origin Server → Create Certificate.
2. Save cert and key on server.
3. Configure Caddy/Nginx to use that cert for the origin.

---

## 3. Cloudflare Tunnel (no open ports)

If you don’t want to expose ports 80/443:

1. Install `cloudflared` on the server.
2. Create a tunnel: `cloudflared tunnel create authora`.
3. Configure ingress (e.g. `https://api.yourdomain.com` → `http://localhost:8000`).
4. Run `cloudflared tunnel run authora`.

---

## 4. Environment Variables

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
DOMAIN_API=api.yourdomain.com
DOMAIN_WEB=app.yourdomain.com
ACME_EMAIL=admin@yourdomain.com
CORS_ORIGINS=["https://app.yourdomain.com"]
```

---

## 5. Caddy Behind Cloudflare

Caddy can validate Let’s Encrypt via HTTP-01 even when Cloudflare proxies. Ensure:

- DNS is proxied (orange cloud).
- SSL mode: Full (strict) on Cloudflare.
- Port 80 is open for ACME validation (or use DNS-01 with Cloudflare API).

---

## 6. WAF and Rate Limiting (optional)

- Cloudflare Dashboard → Security → WAF.
- Create rules for `/api/v1/auth/login`, `/api/v1/auth/register` if needed.
- Rate limiting: Security → Rate limiting rules.
