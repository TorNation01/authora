# AUTHORA Production URL Alignment Report

**Production URL structure (locked for launch):**
- https://authora.studio — Marketing
- https://app.authora.studio — Application
- https://api.authora.studio — API

---

## 1. Production URL Alignment Report

### Frontend Public URL Config
| Location | Config | Production Default | Status |
|----------|--------|---------------------|--------|
| `layout.tsx` | metadataBase | `NEXT_PUBLIC_MARKETING_URL \|\| NEXT_PUBLIC_WEB_URL \|\| 'https://authora.studio'` | ✓ Aligned |
| `sitemap.ts` | baseUrl | Same fallback | ✓ Aligned |
| `robots.ts` | baseUrl | Same fallback | ✓ Aligned |
| `config.ts` | getAppBaseUrl() | `'https://app.authora.studio'` when host is authora.studio | ✓ Aligned |
| `config.ts` | getMarketingBaseUrl() | `'https://authora.studio'` when host is app.authora.studio | ✓ Aligned |
| `middleware.ts` | MARKETING_HOST, APP_HOST | `authora.studio`, `app.authora.studio` | ✓ Aligned |

### Backend Public URL Config
| Location | Config | Production | Status |
|----------|--------|------------|--------|
| `config.py` | cors_origins | From CORS_ORIGINS env | ✓ Env-based |
| API config route | No public URL in response | N/A | ✓ |

### API Client Base URL Config
| Location | Config | Production | Status |
|----------|--------|------------|--------|
| `lib/api.ts` | API_BASE | `NEXT_PUBLIC_API_URL` → https://api.authora.studio | ✓ Aligned |
| `api-gateway.ts` | Same | Same | ✓ Aligned |
| `next.config.js` | rewrites destination | `NEXT_PUBLIC_API_URL \|\| 'http://localhost:8000'` | ✓ Dev fallback |

### Auth Callback URLs
| Flow | URL | Status |
|------|-----|--------|
| Login success | app.authora.studio/dashboard | ✓ |
| Register success | app.authora.studio/onboarding | ✓ |
| Logout | authora.studio (via getMarketingBaseUrl) | ✓ |
| OAuth/SSO | app.authora.studio/sso | ✓ Documented |

### Session / Cookie Domain
| Item | Config | Status |
|------|--------|--------|
| Auth | JWT Bearer in localStorage (no cookies) | ✓ |
| Future cookies | `domain=.authora.studio` documented | ✓ |

### Email Links
| Item | Config | Status |
|------|--------|--------|
| App action links | NEXT_PUBLIC_APP_URL → https://app.authora.studio | ✓ Documented |
| Marketing links | NEXT_PUBLIC_MARKETING_URL → https://authora.studio | ✓ Documented |
| Email templates | No action links yet | N/A |

### Setup Wizard Defaults
| Item | Default | Status |
|------|---------|--------|
| setup_schema.py | domain = "authora.studio" | ✓ |
| setup page form | domain: 'authora.studio' | ✓ |

### SEO / Canonical / Metadata
| Item | Config | Status |
|------|--------|--------|
| metadataBase | https://authora.studio | ✓ |
| Open Graph | Uses metadataBase | ✓ |
| Sitemap | authora.studio marketing URLs only | ✓ |
| robots.txt | authora.studio, disallow app paths | ✓ |

### Local Development
| Item | Behavior | Status |
|------|----------|--------|
| getAppBaseUrl | Returns '' on localhost | ✓ |
| getMarketingBaseUrl | Returns '' on localhost | ✓ |
| Middleware | Skips redirects on localhost/127.0.0.1 | ✓ |
| next.config.js | Fallback http://localhost:8000 | ✓ |
| docker-compose.yml | NEXT_PUBLIC_API_URL=http://localhost:8000 | ✓ |

---

## 2. Updated Environment Variables

| Variable | Production Value |
|----------|------------------|
| NEXT_PUBLIC_API_URL | https://api.authora.studio |
| NEXT_PUBLIC_MARKETING_URL | https://authora.studio |
| NEXT_PUBLIC_APP_URL | https://app.authora.studio |
| CORS_ORIGINS | ["https://authora.studio","https://www.authora.studio","https://app.authora.studio"] |
| DOMAIN_API | api.authora.studio |
| DOMAIN_MARKETING | authora.studio |
| DOMAIN_APP | app.authora.studio |
| ACME_EMAIL | admin@authora.studio |

---

## 3. Updated Docs / Config Files

| File | Changes |
|------|---------|
| docs/DEPLOYMENT-SSL-DOMAIN.md | CORS_ORIGINS, DOMAIN_* vars |
| docs/PRODUCTION-READINESS.md | Setup URL, API register example |
| docs/PRODUCTION_URL_ALIGNMENT_REPORT.md | New report |
| docker-compose.prod.yml | Comment update |
| .env.example | Production examples (commented) |
| docker-compose.prod.yml | Production defaults |
| docs/DOMAIN_*.md | Already aligned |
| docs/ENV-MAP.md | Already aligned |
| docs/GO_LIVE_*.md | Already aligned |

---

## 4. Confirmation

**Production URL structure is consistent across the project.**

- All URL-sensitive areas use env-based configuration.
- Production defaults are https://authora.studio, https://app.authora.studio, https://api.authora.studio.
- Local development uses localhost and relative paths.
- Standalone deployment is preserved.
- No hardcoded production URLs in application code; fallbacks only where env is unset (e.g. metadataBase, sitemap).
