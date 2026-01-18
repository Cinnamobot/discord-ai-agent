@echo off
REM Market Analyst News Server 起動スクリプト (Windows)

cd /d "%~dp0"

echo Starting Market Analyst News Server...

REM バックグラウンドでサーバーを起動
start /B uv run uvicorn news_server:app --host 0.0.0.0 --port 8000 > nohup.out 2>&1

echo Server started.
echo Logs: nohup.out
echo.
echo To stop the server, use Task Manager or:
echo   taskkill /F /IM python.exe
