#!/usr/bin/env bash
# ==============================================================================
# MCP Gateway - Stop Script
# ==============================================================================

# Determine base directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

PID_FILE="$SCRIPT_DIR/app.pid"

echo "========================================================"
echo "          🛑 Stopping MCP Gateway Daemon                "
echo "========================================================"

STOPPED=false

# 1. Stop using PID file if present
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE" 2>/dev/null)
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        echo "⏳ Sending SIGTERM to MCP Gateway (PID: $PID)..."
        kill "$PID" 2>/dev/null
        
        # Wait up to 5 seconds for graceful shutdown
        for i in {1..5}; do
            if kill -0 "$PID" 2>/dev/null; then
                sleep 1
            else
                break
            fi
        done

        # Force kill if still alive
        if kill -0 "$PID" 2>/dev/null; then
            echo "⚠️  Process did not stop gracefully. Forcing SIGKILL (PID: $PID)..."
            kill -9 "$PID" 2>/dev/null
        fi
        STOPPED=true
    fi
    rm -f "$PID_FILE"
fi

# 2. Cleanup any remaining app.py or orphaned gateway processes
PIDS=$(pgrep -f "python.*app.py" | tr '\n' ' ')
if [ -n "$PIDS" ]; then
    echo "🧹 Cleaning up remaining processes: $PIDS"
    for p in $PIDS; do
        kill -9 "$p" 2>/dev/null
    done
    STOPPED=true
fi

if [ "$STOPPED" = true ]; then
    echo "✅ MCP Gateway stopped successfully."
else
    echo "ℹ️  No running MCP Gateway process was found."
fi
echo "========================================================"
