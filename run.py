"""
Discord AI Agent Bot - Launcher

Simple launcher script for starting the bot with different agent profiles.
"""

import sys
import os
from pathlib import Path

# 標準出力のバッファリングを無効化（リアルタイム表示のため）
os.environ["PYTHONUNBUFFERED"] = "1"
# Windows用UTF-8エンコーディング設定（emoji・カラー対応）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")
elif hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Discord Botをインポートして実行
from src.discord_bot import main

if __name__ == "__main__":
    # デフォルトエージェントを使用
    if len(sys.argv) == 1:
        sys.argv.append("./agents/default")
        print("デフォルトエージェント (./agents/default) を使用します")

    main()
