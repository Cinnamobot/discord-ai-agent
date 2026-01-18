#!/bin/bash
# Market Analyst News Server 停止スクリプト

cd "$(dirname "$0")"

if [ ! -f server.pid ]; then
    echo "Error: server.pid not found. Server may not be running."
    exit 1
fi

PID=$(cat server.pid)

echo "Stopping Market Analyst News Server (PID: $PID)..."

# プロセスを終了
kill $PID 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Server stopped successfully."
    rm server.pid
else
    echo "Error: Failed to stop server. Process may have already terminated."
    rm server.pid
    exit 1
fi
