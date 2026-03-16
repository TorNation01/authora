#!/bin/bash
# Validate required environment variables for AUTHORA
# Usage: source .env && ./scripts/validate-env.sh [development|staging|production|standalone]
#
# Modes:
#   development - relaxed; SECRET_KEY default OK
#   staging     - stricter; SECRET_KEY must be changed
#   production  - strict; all prod vars required
#   standalone  - alias for development (default)

set -e

MODE="${1:-standalone}"
FAIL=0

# Normalize mode
case "$MODE" in
  dev|development) MODE="development" ;;
  staging)         MODE="staging" ;;
  prod|production) MODE="production" ;;
  standalone)      MODE="development" ;;
  *)              MODE="standalone" ;;
esac

check() {
  if [ -z "${!1}" ]; then
    echo "ERROR: $1 is required but not set"
    FAIL=1
  fi
}

check_optional() {
  if [ -z "${!1}" ]; then
    echo "WARN: $1 is not set (optional)"
  fi
}

check_secret_not_default() {
  if [ "$SECRET_KEY" = "change-me-in-production-use-openssl-rand-hex-32" ] || \
     [ "$SECRET_KEY" = "dev-secret-change-in-production" ]; then
    echo "ERROR: SECRET_KEY must be changed (use: openssl rand -hex 32)"
    FAIL=1
  fi
}

echo "Validating environment for mode: $MODE"

# Core - always required
check DATABASE_URL
check REDIS_URL
check SECRET_KEY

# Development: allow default SECRET_KEY
if [ "$MODE" = "development" ]; then
  check_optional OPENAI_API_KEY
  check_optional ANTHROPIC_API_KEY
  echo "Environment validation passed (development)."
  exit 0
fi

# Staging and Production: SECRET_KEY must be changed
if [ "$MODE" = "staging" ] || [ "$MODE" = "production" ]; then
  check_secret_not_default
fi

# Production-specific
if [ "$MODE" = "production" ]; then
  check NEXT_PUBLIC_API_URL
  check_optional NEXT_PUBLIC_MARKETING_URL
  check_optional NEXT_PUBLIC_APP_URL
  check_optional DOMAIN_API
  check_optional DOMAIN_MARKETING
  check_optional DOMAIN_APP
  check_optional ACME_EMAIL
fi

# Optional for all
check_optional OPENAI_API_KEY
check_optional ANTHROPIC_API_KEY
check_optional STRIPE_SECRET_KEY
check_optional STRIPE_PUBLISHABLE_KEY
check_optional STRIPE_WEBHOOK_SECRET

# Stripe: when feature_billing or STRIPE_SECRET_KEY set, webhook secret required for production
if [ "$MODE" = "production" ] && [ -n "$STRIPE_SECRET_KEY" ]; then
  if [ -z "$STRIPE_WEBHOOK_SECRET" ] && [ -z "$STRIPE_WEBHOOK_SECRET_LIVE" ]; then
    echo "WARN: Stripe configured but STRIPE_WEBHOOK_SECRET not set. Webhooks will fail."
  fi
  if [ -z "$STRIPE_PUBLISHABLE_KEY" ]; then
    echo "WARN: STRIPE_PUBLISHABLE_KEY not set. Checkout UI may not work."
  fi
fi

if [ $FAIL -eq 1 ]; then
  echo ""
  echo "Fix missing variables and retry. See .env.example or .env.production.example for reference."
  exit 1
fi

echo "Environment validation passed."
exit 0
