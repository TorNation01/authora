# Standalone Mode

AUTHORA remains a fully functional standalone product. Standalone mode is the default and requires no Anakatech dependency.

## How AUTHORA Remains Fully Standalone

1. **No hard dependencies**: Anakatech integration is optional. When `APP_MODE=standalone` (default), all integration adapters are no-ops.

2. **Standalone auth**: Local email/password login and registration. Tokens stored in `localStorage`. No SSO or external identity required.

3. **Standalone setup wizard**: First-run setup creates admin, configures AI keys, and completes onboarding. No external provisioning.

4. **Standalone admin**: Admin panel for user management, system settings, and configuration. No dependency on Anakatech admin.

5. **Standalone dashboard**: Full sidebar navigation, projects, books, notes, journey, gamification. No shared nav shell.

6. **Standalone notifications**: In-app notifications and email reminders (when SMTP/SendGrid configured). No shared notification center.

7. **Standalone storage**: Local or S3/R2 storage. No shared storage service required.

8. **Standalone billing**: Internal plan/entitlement model when `FEATURE_BILLING=true`. No external billing integration required.

## Standalone Configuration

```env
APP_MODE=standalone
# or
DEPLOYMENT_MODE=standalone

# Integration toggles (all default false in standalone)
ENABLE_SSO=false
ENABLE_SHARED_NAV=false
ENABLE_SHARED_NOTIFICATIONS=false
ENABLE_SHARED_ANALYTICS=false
ENABLE_SHARED_BILLING=false
ENABLE_BRAND_OVERRIDES=false
```

## Standalone vs Anakatech-Connected

| Capability | Standalone | Anakatech Connected |
|------------|------------|---------------------|
| Auth | Local email/password | Optional SSO + local fallback |
| Setup | Setup wizard | May skip (provisioned) |
| Navigation | Full sidebar | Optional embeddable shell |
| Notifications | In-app + email | Optional shared center |
| Analytics | Internal only | Optional shared forwarding |
| Billing | Internal plans | Optional shared entitlements |
| Branding | AUTHORA default | Optional overrides |
| Storage | Local/S3/R2 | Optional shared adapter |

## Deployment

Standalone AUTHORA can be deployed:

- As a single Docker Compose stack
- On any cloud provider (AWS, GCP, Azure, Cloudflare)
- Without any Anakatech services
- With or without billing (Stripe) and AI providers

See `docs/ENV-MAP.md` for environment variables.
