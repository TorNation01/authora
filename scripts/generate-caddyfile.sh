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
# Max upload size (default 100MB for exports, large manuscripts)
MAX_UPLOAD="${MAX_UPLOAD:-100MB}"

mkdir -p caddy

cat > caddy/Caddyfile << EOF
# AUTHORA Option 2 - generated from .env
# authora.studio=marketing, app.authora.studio=app, api.authora.studio=API

{
    email ${ACME_EMAIL}
}

# Secure headers and options applied to all sites
(security_headers) {
    header {
        X-Content-Type-Options nosniff
        X-Frame-Options SAMEORIGIN
        X-XSS-Protection "1; mode=block"
        Referrer-Policy strict-origin-when-cross-origin
        -Server
    }
}

${DOMAIN_API} {
    import security_headers
    reverse_proxy api:8000 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-For {remote_host}
        header_up Host {host}
        # WebSocket support for real-time features
        header_up Connection {>Connection}
        header_up Upgrade {>Upgrade}
    }
    encode gzip
    # Allow large uploads (manuscripts, exports)
    request_body {
        max_size ${MAX_UPLOAD}
    }
}

${DOMAIN_MARKETING} {
    import security_headers
    reverse_proxy web:3000 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-For {remote_host}
        header_up Host {host}
        header_up Connection {>Connection}
        header_up Upgrade {>Upgrade}
    }
    encode gzip
    request_body {
        max_size ${MAX_UPLOAD}
    }
}

${DOMAIN_APP} {
    import security_headers
    reverse_proxy web:3000 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-For {remote_host}
        header_up Host {host}
        header_up Connection {>Connection}
        header_up Upgrade {>Upgrade}
    }
    encode gzip
    request_body {
        max_size ${MAX_UPLOAD}
    }
}

www.${DOMAIN_MARKETING} {
    redir https://${DOMAIN_MARKETING}{uri} permanent
}
EOF

echo "Generated caddy/Caddyfile: $DOMAIN_API, $DOMAIN_MARKETING, $DOMAIN_APP (max_upload=${MAX_UPLOAD})"
