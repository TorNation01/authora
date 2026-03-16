#!/bin/bash
# AUTHORA One-Command Bootstrap (alias for deploy)
# Usage: ./scripts/bootstrap-one.sh [repo_url]
#
# Delegates to ./scripts/deploy.sh for the full flow.
# Kept for backwards compatibility.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/deploy.sh" dev "${1:-https://github.com/TorNation01/authora.git}"
