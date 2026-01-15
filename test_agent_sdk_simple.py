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


async def main():
    print("=" * 60)
    print("Agent SDK 簡易テスト（デバッグ出力付き）")
    print("=" * 60)

    # 環境変数確認
    print("\n📋 環境変数チェック:")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    print(f"  ANTHROPIC_API_KEY: {'設定済み' if api_key else '未設定'}")
    if api_key:
        print(f"  キーの先頭: {api_key[:20]}...")

    # .env から読み込み
    try:
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        print(f"  .env読み込み後: {'設定済み' if api_key else '未設定'}")
    except ImportError:
        print("  ⚠️ dotenv がインストールされていません")

    # Claude CLI パス確認
    claude_cli = Path(r"C:\Users\szk27\.local\bin\claude.exe")
    print(f"\n📍 Claude CLI パス:")
    print(f"  {claude_cli}")
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

        # 環境変数を明示的に渡す
        env_vars = {
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
            "ANTHROPIC_BASE_URL": os.getenv("ANTHROPIC_BASE_URL", ""),
        }

        async for message in query(
            prompt="Hi",
            options=ClaudeAgentOptions(
                cli_path=str(claude_cli),
                permission_mode="bypassPermissions",
                max_turns=1,
                env=env_vars,  # 環境変数を明示的に渡す
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
