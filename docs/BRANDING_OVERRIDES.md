# Branding Overrides

AUTHORA supports environment-driven branding overrides for white-label and Anakatech deployments.

## Overridable Fields

| Variable | Description | Default |
|----------|-------------|---------|
| `BRANDING_PRODUCT_NAME` | App name (sidebar, login, emails) | `AUTHORA` |
| `BRANDING_TAGLINE` | Tagline (landing, metadata) | `AI-Powered Book Builder` |
| `BRANDING_LOGO_URL` | Logo URL (sidebar, login) | `null` |
| `BRANDING_FAVICON_URL` | Favicon URL | `null` |
| `BRANDING_PRIMARY_COLOR` | Accent color (hex) | `null` |
| `BRANDING_SHOW_POWERED_BY` | Show "Powered by AUTHORA" | `true` |

## When Overrides Apply

- **Standalone**: Overrides apply when set (e.g. for custom deployments).
- **White-label**: `ENABLE_BRAND_OVERRIDES=true` (default). Overrides are expected.
- **Anakatech**: `ENABLE_BRAND_OVERRIDES=true`. Overrides can come from portal config.

## API

Branding is exposed at:

- `GET /api/v1/config` – Includes `branding` object
- `GET /api/v1/config/branding` – Branding only

Response shape:

```json
{
  "product_name": "My Writing App",
  "tagline": "Write Your Book",
  "logo_url": "https://example.com/logo.png",
  "favicon_url": "https://example.com/favicon.ico",
  "primary_color": "#6366f1",
  "show_powered_by": false
}
```

## Usage in Frontend

- `BrandedSidebar` – Uses `product_name`, `logo_url`
- Login/Register pages – Use `product_name`
- Email templates – Use `product_name` in subject/body
- Metadata – Use `product_name`, `tagline` for `<title>`, `<meta>`

## Integration Adapter

For programmatic access:

```python
from authora.integration.branding import get_effective_branding, product_name, primary_color

branding = get_effective_branding()
name = product_name()
color = primary_color()
```
