#!/bin/bash
# Start all services for WhatsApp AI Assistant (Termux)

PROJ_DIR="$HOME/whatsapp-assistant"
cd "$PROJ_DIR"

# Acquire wake lock to prevent Android from killing Termux
echo "Acquiring wake lock..."
termux-wake-lock 2>/dev/null || true

# Create data dir if missing
mkdir -p "$PROJ_DIR/data"

# Load env
set -a
source "$PROJ_DIR/.env"
set +a

echo "Starting Baileys bridge on port 3001..."
cd "$PROJ_DIR/baileys-bridge"
node dist/index.js &
BRIDGE_PID=$!
cd "$PROJ_DIR"

echo "Starting backend on port 8000..."
cd "$PROJ_DIR/backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd "$PROJ_DIR"

# Save PIDs for stop script
echo "$BRIDGE_PID" > "$PROJ_DIR/data/bridge.pid"
echo "$BACKEND_PID" > "$PROJ_DIR/data/backend.pid"

echo ""
echo "========================================="
echo "  All services running!"
echo ""
echo "  Dashboard:    http://localhost:8000"
echo "  WhatsApp QR:  http://localhost:3001/qr"
echo "  Bridge status: http://localhost:3001/status"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "========================================="

# Wait for both processes, exit if either dies
trap "kill $BRIDGE_PID $BACKEND_PID 2>/dev/null; termux-wake-unlock 2>/dev/null; exit 0" INT TERM

wait -n $BRIDGE_PID $BACKEND_PID
echo "A service stopped. Shutting down..."
kill $BRIDGE_PID $BACKEND_PID 2>/dev/null
termux-wake-unlock 2>/dev/null
