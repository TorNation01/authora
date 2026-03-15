# SSO Ready Notes

AUTHORA is SSO-ready for Anakatech integration. SSO is optional and does not affect standalone operation.

## Requirements

- `APP_MODE=anakatech` (or `DEPLOYMENT_MODE=anakatech`)
- `ENABLE_SSO=true`
- `FEATURE_SSO_READY=true`

## Configuration

```env
# SSO (SAML/OIDC)
SSO_ISSUER_URL=https://idp.anakatech.example.com
SSO_CLIENT_ID=authora
SSO_METADATA_URL=https://idp.anakatech.example.com/.well-known/openid-configuration
```

## Integration Adapter

```python
from authora.integration.identity import use_sso_login, should_use_local_auth

# Show SSO button when enabled
if use_sso_login():
    # Redirect to IdP or exchange token from parent
    ...

# Local auth still available when feature_standalone_auth=true
if should_use_local_auth():
    # Show email/password form
    ...
```

## Auth Flow Options

1. **Redirect to IdP**: User clicks "Sign in with SSO" → redirect to IdP → callback with token.
2. **Token from parent**: When embedded in Anakatech portal, token passed via `postMessage` or gateway header.
3. **Local fallback**: When `FEATURE_STANDALONE_AUTH=true`, local login remains available.

## Implementation Status

- **Ready**: Config, feature flags, identity adapter, auth route structure.
- **To implement**: IdP redirect flow, token exchange, shared identity resolution.

The `/sso` route and `apps/web/src/app/(auth)/sso/page.tsx` are entry points. Wire your IdP (e.g. Auth0, Okta, Keycloak) according to your Anakatech identity service.
