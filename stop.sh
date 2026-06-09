#!/bin/bash
# Stop all WhatsApp AI Assistant services

PROJ_DIR="$HOME/whatsapp-assistant"

if [ -f "$PROJ_DIR/data/bridge.pid" ]; then
    kill $(cat "$PROJ_DIR/data/bridge.pid") 2>/dev/null
    rm "$PROJ_DIR/data/bridge.pid"
    echo "Bridge stopped"
fi

if [ -f "$PROJ_DIR/data/backend.pid" ]; then
    kill $(cat "$PROJ_DIR/data/backend.pid") 2>/dev/null
    rm "$PROJ_DIR/data/backend.pid"
    echo "Backend stopped"
fi

termux-wake-unlock 2>/dev/null
echo "All services stopped"
