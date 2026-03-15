#!/bin/bash
# Validate required environment variables for AUTHORA
# Usage: source .env && ./scripts/validate-env.sh [standalone|production]

set -e

MODE="${1:-standalone}"
FAIL=0

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

echo "Validating environment for mode: $MODE"

# Core - always required
check DATABASE_URL
check REDIS_URL
check SECRET_KEY

# Production-specific
if [ "$MODE" = "production" ]; then
  check NEXT_PUBLIC_API_URL
  if [ "$SECRET_KEY" = "change-me-in-production-use-openssl-rand-hex-32" ] || \
     [ "$SECRET_KEY" = "dev-secret-change-in-production" ]; then
    echo "ERROR: SECRET_KEY must be changed in production (use: openssl rand -hex 32)"
    FAIL=1
  fi
fi

# Optional
check_optional OPENAI_API_KEY
check_optional ANTHROPIC_API_KEY

if [ $FAIL -eq 1 ]; then
  echo ""
  echo "Fix missing variables and retry. See .env.example for reference."
  exit 1
fi

echo "Environment validation passed."
