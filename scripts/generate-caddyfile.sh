#!/bin/bash
# Generate Caddyfile from .env (DOMAIN_API, DOMAIN_MARKETING, DOMAIN_APP, ACME_EMAIL)
# Option 2: authora.studio=marketing, app.authora.studio=app, api.authora.studio=API
# Usage: ./scripts/generate-caddyfile.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

[ -f .env ] && set -a && source .env && set +a

DOMAIN_API="${DOMAIN_API:-api.authora.studio}"
DOMAIN_MARKETING="${DOMAIN_MARKETING:-authora.studio}"
DOMAIN_APP="${DOMAIN_APP:-app.authora.studio}"
ACME_EMAIL="${ACME_EMAIL:-admin@authora.studio}"
# Legacy: DOMAIN_WEB falls back to DOMAIN_MARKETING
DOMAIN_WEB="${DOMAIN_WEB:-$DOMAIN_MARKETING}"

mkdir -p caddy

cat > caddy/Caddyfile << EOF
# AUTHORA Option 2 - generated from .env
# authora.studio=marketing, app.authora.studio=app, api.authora.studio=API

{
    email ${ACME_EMAIL}
}

${DOMAIN_API} {
    reverse_proxy api:8000 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-For {remote_host}
        header_up Host {host}
    }
    encode gzip
}

${DOMAIN_MARKETING} {
    reverse_proxy web:3000 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-For {remote_host}
        header_up Host {host}
    }
    encode gzip
}

${DOMAIN_APP} {
    reverse_proxy web:3000 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-For {remote_host}
        header_up Host {host}
    }
    encode gzip
}

www.${DOMAIN_MARKETING} {
    redir https://${DOMAIN_MARKETING}{uri} permanent
}
EOF

echo "Generated caddy/Caddyfile: $DOMAIN_API, $DOMAIN_MARKETING, $DOMAIN_APP"
