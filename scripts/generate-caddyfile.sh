#!/bin/bash
# Generate Caddyfile from .env (DOMAIN_API, DOMAIN_WEB, ACME_EMAIL)
# Usage: ./scripts/generate-caddyfile.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

[ -f .env ] && set -a && source .env && set +a

DOMAIN_API="${DOMAIN_API:-api.example.com}"
DOMAIN_WEB="${DOMAIN_WEB:-app.example.com}"
ACME_EMAIL="${ACME_EMAIL:-admin@example.com}"

mkdir -p caddy

cat > caddy/Caddyfile << EOF
# AUTHORA - generated from .env (DOMAIN_API, DOMAIN_WEB, ACME_EMAIL)

{
    email ${ACME_EMAIL}
}

${DOMAIN_API} {
    reverse_proxy api:8000
    encode gzip
}

${DOMAIN_WEB} {
    reverse_proxy web:3000
    encode gzip
}
EOF

echo "Generated caddy/Caddyfile with domains: $DOMAIN_API, $DOMAIN_WEB"
