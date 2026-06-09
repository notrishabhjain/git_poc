#!/bin/bash
# Termux setup script for WhatsApp AI Assistant
# Run with: curl -sL <raw-url>/termux-setup.sh | bash

set -e

echo "================================================"
echo "  WhatsApp AI Assistant — Termux Setup"
echo "  This will take ~10 minutes on first run"
echo "================================================"
echo ""

# Update packages
echo "[1/6] Updating Termux packages..."
pkg update -y && pkg upgrade -y

# Install system dependencies
echo "[2/6] Installing Python, Node.js, and tools..."
pkg install -y python nodejs-lts git ffmpeg termux-api

# Install pip packages
echo "[3/6] Installing Python dependencies..."
pip install --upgrade pip
pip install \
    fastapi \
    'uvicorn[standard]' \
    'sqlalchemy[asyncio]' \
    aiosqlite \
    pydantic \
    pydantic-settings \
    cryptography \
    openai \
    httpx \
    'python-jose[cryptography]' \
    'passlib[bcrypt]' \
    python-multipart \
    apscheduler \
    python-dateutil \
    pytz \
    google-api-python-client \
    google-auth-oauthlib \
    google-auth-httplib2

# Clone or update repo
echo "[4/6] Setting up project..."
PROJ_DIR="$HOME/whatsapp-assistant"
if [ -d "$PROJ_DIR" ]; then
    cd "$PROJ_DIR" && git pull origin claude/great-ptolemy-sVXfw
else
    git clone -b claude/great-ptolemy-sVXfw https://github.com/notrishabhjain/git_poc.git "$PROJ_DIR"
fi
cd "$PROJ_DIR"

# Install Node.js dependencies for bridge
echo "[5/6] Installing Baileys bridge dependencies..."
cd "$PROJ_DIR/baileys-bridge"
npm install
npx tsc
cd "$PROJ_DIR"

# Create .env if not exists
echo "[6/6] Setting up configuration..."
if [ ! -f "$PROJ_DIR/.env" ]; then
    cp "$PROJ_DIR/.env.example" "$PROJ_DIR/.env"

    # Generate random secrets
    ENC_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
    JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
    BRIDGE_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
    DASH_PASS=$(python -c "import secrets; print(secrets.token_urlsafe(12))")

    # Update .env with SQLite and generated secrets
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=sqlite+aiosqlite:///$PROJ_DIR/data/assistant.db|" "$PROJ_DIR/.env"
    sed -i "s|REDIS_URL=.*|REDIS_URL=|" "$PROJ_DIR/.env"
    sed -i "s|ENCRYPTION_SECRET=.*|ENCRYPTION_SECRET=$ENC_SECRET|" "$PROJ_DIR/.env"
    sed -i "s|JWT_SECRET=.*|JWT_SECRET=$JWT_SECRET|" "$PROJ_DIR/.env"
    sed -i "s|BRIDGE_SHARED_SECRET=.*|BRIDGE_SHARED_SECRET=$BRIDGE_SECRET|" "$PROJ_DIR/.env"
    sed -i "s|DASHBOARD_PASSWORD=.*|DASHBOARD_PASSWORD=$DASH_PASS|" "$PROJ_DIR/.env"
    sed -i "s|BRIDGE_URL=.*|BRIDGE_URL=http://localhost:3001|" "$PROJ_DIR/.env"
    sed -i "s|BACKEND_WEBHOOK_URL=.*|BACKEND_WEBHOOK_URL=http://localhost:8000/api/v1/webhooks/whatsapp/message|" "$PROJ_DIR/.env"
    sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=|" "$PROJ_DIR/.env"

    # Create data directory
    mkdir -p "$PROJ_DIR/data"

    echo ""
    echo "================================================"
    echo "  Almost done! Enter your API keys:"
    echo "================================================"
    echo ""

    read -p "Groq API Key (gsk_...): " GROQ_KEY
    sed -i "s|GROQ_API_KEY=.*|GROQ_API_KEY=$GROQ_KEY|" "$PROJ_DIR/.env"

    read -p "NVIDIA API Key (nvapi-...): " NVIDIA_KEY
    sed -i "s|NVIDIA_API_KEY=.*|NVIDIA_API_KEY=$NVIDIA_KEY|" "$PROJ_DIR/.env"

    read -p "ntfy.sh topic name: " NTFY_TOPIC
    sed -i "s|NTFY_TOPIC=.*|NTFY_TOPIC=$NTFY_TOPIC|" "$PROJ_DIR/.env"

    echo ""
    echo "Your dashboard password is: $DASH_PASS"
    echo "(Save this! You need it to log into the dashboard)"
fi

echo ""
echo "================================================"
echo "  Setup complete!"
echo ""
echo "  Start the app with:"
echo "    cd ~/whatsapp-assistant && ./start.sh"
echo ""
echo "  Then open in Chrome:"
echo "    Dashboard: http://localhost:8000"
echo "    WhatsApp QR: http://localhost:3001/qr"
echo "================================================"
