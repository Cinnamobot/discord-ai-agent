"""
Agent SDK 簡易テスト - デバッグ出力付き
"""

import asyncio
import os
import sys
import io
from pathlib import Path

# Windows環境での文字コード問題を回避
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Claude CLI finder をインポート
from discord_ai_agent.claude_cli_finder import find_claude_cli


async def main():
    print("=" * 60)
    print("Agent SDK 簡易テスト（デバッグ出力付き）")
    print("=" * 60)

    # 環境変数確認
    print("\n📋 環境変数チェック:")
    print("  Note: Claude Code CLIを使用するため、Anthropic APIキーは不要です")

    # .env から読み込み
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print("  .env 読み込み完了")
    except ImportError:
        print("  ⚠️ dotenv がインストールされていません")

    # Claude CLI パス確認（自動検知）
    print(f"\n📍 Claude CLI パス検出:")
    claude_cli = find_claude_cli()
    if claude_cli is None:
        print("  ❌ Claude CLI が見つかりませんでした")
        print(
            "  環境変数 CLAUDE_CLI_PATH を設定するか、Claude CLI を PATH に追加してください"
        )
        return
    print(f"  ✅ {claude_cli}")
    print(f"  存在: {claude_cli.exists()}")

    # Agent SDK インポート
    print("\n🔧 Agent SDK インポート:")
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions

        print("  ✅ インポート成功")
    except ImportError as e:
        print(f"  ❌ インポートエラー: {e}")
        return

    # 最小限のテスト
    print("\n🚀 最小限のクエリを実行:")
    print("  プロンプト: 'Hi'")
    print("  オプション: permission_mode='bypassPermissions', max_turns=1")

    try:
        result_text = ""
        message_count = 0

        # Note: Claude Code CLIを使用するため、環境変数は不要
        async for message in query(
            prompt="Hi",
            options=ClaudeAgentOptions(
                cli_path=str(claude_cli),
                permission_mode="bypassPermissions",
                max_turns=1,
            ),
        ):
            message_count += 1
            print(f"\n  📨 メッセージ #{message_count}:")
            print(f"     タイプ: {type(message).__name__}")

            if hasattr(message, "type"):
                print(f"     message.type: {message.type}")

            if hasattr(message, "subtype"):
                print(f"     message.subtype: {message.subtype}")

            if hasattr(message, "result"):
                result_text = message.result
                print(f"     result 取得: {len(result_text)} 文字")

            # ResultMessage を受け取ったらループを抜ける
            if hasattr(message, "subtype") and message.subtype == "success":
                print("     ✅ success メッセージ受信、ループ終了")
                break

        if result_text:
            print("\n✅ テスト成功!")
            print(f"\n--- Agent の応答 ({len(result_text)}文字) ---")
            print(result_text[:300] + "..." if len(result_text) > 300 else result_text)
            print("--- 応答ここまで ---")
        else:
            print("\n⚠️ 応答が取得できませんでした")
            print(f"   受信メッセージ数: {message_count}")

    except Exception as e:
        print(f"\n❌ エラー発生:")
        print(f"   {type(e).__name__}: {e}")

        import traceback

        print("\n詳細:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
