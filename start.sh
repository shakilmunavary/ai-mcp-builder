#!/usr/bin/env bash
# ==============================================================================
# MCP Gateway - Start Script (Background Daemon)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

PID_FILE="$SCRIPT_DIR/app.pid"
LOG_FILE="$SCRIPT_DIR/app.log"

echo "========================================================"
echo "          🚀 Starting MCP Gateway Daemon                "
echo "========================================================"

# 1. Check if already running via PID file
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE" 2>/dev/null)
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        echo "⚠️  MCP Gateway is ALREADY running (PID: $PID)."
        echo "🌐 Web UI:  http://localhost:5000"
        echo "🔒 Gateway: http://localhost:5001"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

# 2. Check if already running via process table
EXISTING_PID=$(pgrep -f "python.*app.py" | head -n 1)
if [ -n "$EXISTING_PID" ]; then
    echo "⚠️  MCP Gateway process found running (PID: $EXISTING_PID)."
    echo "$EXISTING_PID" > "$PID_FILE"
    echo "🌐 Web UI:  http://localhost:5000"
    echo "🔒 Gateway: http://localhost:5001"
    exit 0
fi

# 3. Locate Python virtual environment (Prefer local venv)
PYTHON_EXEC=""
if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON_EXEC="$SCRIPT_DIR/venv/bin/python"
elif [ -f "$SCRIPT_DIR/venv_linux/bin/python" ]; then
    PYTHON_EXEC="$SCRIPT_DIR/venv_linux/bin/python"
else
    echo "📦 Initializing virtual environment in $SCRIPT_DIR/venv..."
    python3 -m venv "$SCRIPT_DIR/venv"
    "$SCRIPT_DIR/venv/bin/pip" install --upgrade pip
    "$SCRIPT_DIR/venv/bin/pip" install flask requests httpx python-dotenv pyyaml keyring keyrings.alt mistralai mcp
    PYTHON_EXEC="$SCRIPT_DIR/venv/bin/python"
fi

# 4. Start application in the background
echo "▶️  Launching app.py in background..."
nohup "$PYTHON_EXEC" app.py > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

# 5. Verify process started
sleep 2
if kill -0 "$NEW_PID" 2>/dev/null; then
    echo "✅ MCP Gateway started successfully in background!"
    echo "🆔 PID:     $NEW_PID"
    echo "📄 Log:     $LOG_FILE"
    echo "🌐 Web UI:  http://localhost:5000"
    echo "🔒 Gateway: http://localhost:5001"
    echo "========================================================"
else
    echo "❌ Failed to start MCP Gateway. Recent log output:"
    echo "--------------------------------------------------------"
    tail -n 20 "$LOG_FILE" 2>/dev/null
    echo "--------------------------------------------------------"
    rm -f "$PID_FILE"
    exit 1
fi
