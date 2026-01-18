#!/bin/bash
# DenisOS Setup Script
# Run this once to get everything running

set -e

echo "=========================================="
echo "  DenisOS Setup - Your Personal Codex"
echo "=========================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
    echo "For Windows, please install Docker Desktop manually:"
    echo "https://www.docker.com/products/docker-desktop/"
    echo "Then run: docker-compose up --build"
    exit 0
else
    OS="unknown"
fi

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "[OK] Docker is installed"
else
    echo "[!] Docker not found. Installing..."

    if [[ "$OS" == "mac" ]]; then
        echo ""
        echo "Please install Docker Desktop for Mac:"
        echo "https://www.docker.com/products/docker-desktop/"
        echo ""
        echo "Or install via Homebrew:"
        echo "  brew install --cask docker"
        echo ""
        read -p "Press Enter after Docker is installed..."
    elif [[ "$OS" == "linux" ]]; then
        echo "Installing Docker..."
        curl -fsSL https://get.docker.com | sh
        sudo usermod -aG docker $USER
        echo ""
        echo "[!] You may need to log out and back in for Docker permissions."
        echo "    Or run: newgrp docker"
    fi
fi

# Check if Docker is running
if docker info &> /dev/null; then
    echo "[OK] Docker is running"
else
    echo "[!] Docker is not running. Please start Docker Desktop."
    read -p "Press Enter when Docker is running..."
fi

# Check for docker-compose
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    echo "[OK] Docker Compose is available"
else
    echo "[!] Docker Compose not found."
    echo "    It should come with Docker Desktop."
    exit 1
fi

echo ""
echo "=========================================="
echo "  Building and Starting DenisOS..."
echo "=========================================="
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# Build and run
if command -v docker-compose &> /dev/null; then
    docker-compose up --build -d
else
    docker compose up --build -d
fi

echo ""
echo "=========================================="
echo "  DenisOS is Ready!"
echo "=========================================="
echo ""
echo "  Open in browser: http://localhost:8501"
echo ""
echo "  To stop:  docker-compose down"
echo "  To start: docker-compose up -d"
echo "  Logs:     docker-compose logs -f"
echo ""

# Get local IP for phone access
if [[ "$OS" == "mac" ]]; then
    LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || echo "unknown")
elif [[ "$OS" == "linux" ]]; then
    LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "unknown")
fi

if [[ "$LOCAL_IP" != "unknown" ]]; then
    echo "  Phone access (same WiFi): http://$LOCAL_IP:8501"
    echo ""
fi

echo "\"Hello, Denis. I am your Codex.\""
echo ""

# Try to open browser
if [[ "$OS" == "mac" ]]; then
    open http://localhost:8501 2>/dev/null || true
elif [[ "$OS" == "linux" ]]; then
    xdg-open http://localhost:8501 2>/dev/null || true
fi
