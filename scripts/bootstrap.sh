#!/bin/bash
# AUTHORA Fresh Ubuntu Bootstrap
# Usage: ./scripts/bootstrap.sh
# Run on a fresh Ubuntu 22.04/24.04 server. Installs Docker, Docker Compose, Git, Node, Python.
# Idempotent: safe to re-run.

set -e

echo "=== AUTHORA Fresh Ubuntu Bootstrap ==="

# Detect OS
if [ -f /etc/os-release ]; then
  . /etc/os-release
  OS_ID="${ID:-unknown}"
  OS_VERSION="${VERSION_ID:-}"
else
  OS_ID="unknown"
fi

if [ "$OS_ID" != "ubuntu" ] && [ "$OS_ID" != "debian" ]; then
  echo "WARN: This script targets Ubuntu/Debian. You may need to adapt package names."
fi

# Update and install base packages
echo ""
echo "Installing base packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  software-properties-common \
  git \
  jq \
  unzip

# Docker
if ! command -v docker &> /dev/null; then
  echo ""
  echo "Installing Docker..."
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER" 2>/dev/null || true
  echo "Docker installed. You may need to log out and back in for group membership."
else
  echo "Docker already installed: $(docker --version)"
fi

# Docker Compose (plugin)
if ! docker compose version &> /dev/null; then
  echo ""
  echo "Installing Docker Compose plugin..."
  sudo apt-get install -y -qq docker-compose-plugin || {
    echo "Falling back to standalone docker-compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
  }
else
  echo "Docker Compose already installed: $(docker compose version)"
fi

# Node.js 20 LTS (for setup wizard, local dev)
if ! command -v node &> /dev/null; then
  echo ""
  echo "Installing Node.js 20..."
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y -qq nodejs
else
  echo "Node.js already installed: $(node -v)"
fi

# Python 3.11+ (for local dev, migrations without Docker)
if ! command -v python3 &> /dev/null; then
  echo ""
  echo "Installing Python 3..."
  sudo apt-get install -y -qq python3 python3-pip python3-venv
fi
PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "?")
echo "Python: $(python3 --version 2>/dev/null || echo 'not found')"

# Firewall (optional - uncomment if using ufw)
# sudo ufw allow 22/tcp
# sudo ufw allow 80/tcp
# sudo ufw allow 443/tcp
# sudo ufw --force enable

echo ""
echo "=== Bootstrap complete ==="
echo ""
echo "Next steps:"
echo "  1. Log out and back in (if Docker was just installed) so 'docker' works without sudo"
echo "  2. Clone repo: git clone https://github.com/TorNation01/authora.git && cd authora"
echo "  3. Run: ./scripts/install.sh"
echo ""
