# Application Modes

AUTHORA operates in three modes, controlled by `APP_MODE` or `DEPLOYMENT_MODE`.

## Mode 1: Standalone

**Purpose**: Fully self-contained product. No Anakatech dependency.

- **Branding**: AUTHORA
- **Auth**: Standalone (local email/password)
- **Setup**: Standalone wizard
- **Admin**: Standalone admin panel
- **Dashboard**: Standalone sidebar and navigation
- **Notifications**: AUTHORA in-app + email
- **Dependencies**: None on Anakatech

**Configuration**:
```env
APP_MODE=standalone
```

## Mode 2: Anakatech Connected

**Purpose**: Integrated into the Anakatech ecosystem. Optional shared services.

- **Branding**: Optional override (Authora or custom)
- **Auth**: Optional SSO + local fallback
- **Setup**: May be skipped (provisioned by portal)
- **Admin**: Standalone or delegated
- **Dashboard**: Optional embeddable shell (no sidebar)
- **Notifications**: Optional shared notification center
- **Analytics**: Optional shared audit/analytics forwarding
- **Billing**: Optional shared entitlement checks
- **Storage**: Optional shared storage adapter

**Configuration**:
```env
APP_MODE=anakatech
ENABLE_SSO=true
ENABLE_SHARED_NAV=true
ENABLE_SHARED_NOTIFICATIONS=true
ENABLE_SHARED_ANALYTICS=true
ENABLE_SHARED_BILLING=true
ENABLE_BRAND_OVERRIDES=true
API_GATEWAY_URL=https://gateway.anakatech.example.com
```

## Mode 3: White-Label Ready

**Purpose**: Resale/licensing model. Configurable branding without Anakatech portal.

- **Branding**: Environment-driven overrides (logos, colors, product name)
- **Auth**: Standalone (local)
- **Setup**: Standalone wizard
- **Admin**: Standalone
- **Dashboard**: Standalone
- **Notifications**: Standalone
- **Dependencies**: None on Anakatech; branding only

**Configuration**:
```env
APP_MODE=white_label
ENABLE_BRAND_OVERRIDES=true
BRANDING_PRODUCT_NAME=My Writing App
BRANDING_TAGLINE=Write Your Book
BRANDING_LOGO_URL=https://example.com/logo.png
BRANDING_PRIMARY_COLOR=#6366f1
```

## Mode Selection

| Variable | Values | Default |
|----------|--------|---------|
| `APP_MODE` | `standalone` \| `anakatech` \| `white_label` | `standalone` |
| `DEPLOYMENT_MODE` | Same | `standalone` |

`APP_MODE` takes precedence when set. Otherwise `DEPLOYMENT_MODE` is used.

## Frontend

Config is fetched from `GET /api/v1/config`. Response includes:

- `app_mode` – Effective mode
- `is_standalone`, `is_anakatech`, `is_white_label`
- `feature_flags` – Product feature flags
- `integration_flags` – Integration toggles
- `branding` – White-label config
