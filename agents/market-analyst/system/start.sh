#!/bin/bash
# Market Analyst News Server 起動スクリプト

cd "$(dirname "$0")"

echo "Starting Market Analyst News Server..."

# バックグラウンドでサーバーを起動
nohup uv run uvicorn news_server:app --host 0.0.0.0 --port 8000 > nohup.out 2>&1 &

# プロセスIDを保存
echo $! > server.pid

echo "Server started with PID: $(cat server.pid)"
echo "Logs: nohup.out"
echo ""
echo "To stop the server, run: ./stop.sh"
