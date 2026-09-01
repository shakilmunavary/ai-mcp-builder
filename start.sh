#!/usr/bin/env bash
# ==============================================================================
# MCP Gateway - Start Script (Background Daemon & Codespaces Ready)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

PID_FILE="$SCRIPT_DIR/app.pid"
LOG_FILE="$SCRIPT_DIR/app.log"

echo "========================================================"
echo "          🚀 Starting AI DevOps Portal Daemon           "
echo "========================================================"

# 1. Check if already running via PID file
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE" 2>/dev/null)
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        echo "⚠️  AI DevOps Portal is ALREADY running (PID: $PID)."
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
    echo "⚠️  AI DevOps Portal process found running (PID: $EXISTING_PID)."
    echo "$EXISTING_PID" > "$PID_FILE"
    echo "🌐 Web UI:  http://localhost:5000"
    echo "🔒 Gateway: http://localhost:5001"
    exit 0
fi

# 3. Locate Python execution environment
PYTHON_EXEC=""
if [ -n "$CODESPACES" ] || [ -n "$DEVCONTAINER" ]; then
    # In GitHub Codespaces or Devcontainer, use container Python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_EXEC="$(command -v python3)"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_EXEC="$(command -v python)"
    fi
elif [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON_EXEC="$SCRIPT_DIR/venv/bin/python"
elif [ -f "$SCRIPT_DIR/venv_linux/bin/python" ]; then
    PYTHON_EXEC="$SCRIPT_DIR/venv_linux/bin/python"
elif command -v python3 >/dev/null 2>&1 && python3 -c "import flask" >/dev/null 2>&1; then
    PYTHON_EXEC="$(command -v python3)"
else
    echo "📦 Initializing virtual environment in $SCRIPT_DIR/venv..."
    python3 -m venv "$SCRIPT_DIR/venv"
    "$SCRIPT_DIR/venv/bin/pip" install --upgrade pip
    "$SCRIPT_DIR/venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
    PYTHON_EXEC="$SCRIPT_DIR/venv/bin/python"
fi

echo "🐍 Using Python: $PYTHON_EXEC"

# 4. Start application in the background
echo "▶️  Launching app.py in background..."
nohup "$PYTHON_EXEC" app.py > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

# 5. Verify process started
sleep 2
if kill -0 "$NEW_PID" 2>/dev/null; then
    echo "✅ AI DevOps Portal started successfully in background!"
    echo "🆔 PID:     $NEW_PID"
    echo "📄 Log:     $LOG_FILE"
    echo "🌐 Web UI:  http://localhost:5000"
    echo "🔒 Gateway: http://localhost:5001"
    echo "========================================================"
else
    echo "❌ Failed to start AI DevOps Portal. Recent log output:"
    echo "--------------------------------------------------------"
    tail -n 20 "$LOG_FILE" 2>/dev/null
    echo "--------------------------------------------------------"
    rm -f "$PID_FILE"
    exit 1
fi
