"""
Agent SDKのプロセス表示テスト

このスクリプトでAgent SDKの実行プロセス（推論、ツール使用、結果）が
ターミナルに表示されることを確認します。
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 標準出力のバッファリングを無効化（リアルタイム表示のため）
os.environ["PYTHONUNBUFFERED"] = "1"
# Windows用UTF-8エンコーディング設定（emoji・カラー対応）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Agent SDK
from claude_agent_sdk import query, ClaudeAgentOptions

# ロギング設定
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# カラーコード
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def log_agent_message(message):
    """Agent SDKのメッセージを表示"""
    # デバッグ: メッセージタイプを表示
    msg_type = type(message).__name__

    # SystemMessage - システムメッセージ（スキップ）
    if msg_type == "SystemMessage":
        return

    # AssistantMessage - アシスタントの応答（思考・ツール使用を含む）
    if msg_type == "AssistantMessage" and hasattr(message, "content"):
        content = message.content
        if not content:
            return

        # content は TextBlock/ToolUseBlock のリスト
        if isinstance(content, list):
            for item in content:
                # TextBlock - テキスト（思考）
                if type(item).__name__ == "TextBlock":
                    text = getattr(item, "text", "")
                    if text:
                        text_preview = text[:200]
                        if len(text) > 200:
                            text_preview += "..."
                        print(
                            f"{Colors.CYAN}💭 Claude Thinking:{Colors.ENDC}", flush=True
                        )
                        print(f"   {text_preview}", flush=True)

                # ToolUseBlock - ツール使用
                elif type(item).__name__ == "ToolUseBlock":
                    tool_name = getattr(item, "name", "unknown")
                    tool_input = getattr(item, "input", {})
                    print(
                        f"\n{Colors.YELLOW}🔧 Tool Use:{Colors.ENDC} {Colors.BOLD}{tool_name}{Colors.ENDC}",
                        flush=True,
                    )
                    if isinstance(tool_input, dict):
                        for key, value in tool_input.items():
                            value_str = str(value)
                            if len(value_str) > 100:
                                value_str = value_str[:100] + "..."
                            print(
                                f"   {Colors.BLUE}└─{Colors.ENDC} {key}: {value_str}",
                                flush=True,
                            )
                    else:
                        input_str = str(tool_input)[:200]
                        print(
                            f"   {Colors.BLUE}└─{Colors.ENDC} input: {input_str}",
                            flush=True,
                        )

        # content が文字列の場合
        elif isinstance(content, str):
            text_preview = content[:200]
            if len(content) > 200:
                text_preview += "..."
            print(f"{Colors.CYAN}💭 Claude Thinking:{Colors.ENDC}", flush=True)
            print(f"   {text_preview}", flush=True)

    # UserMessage - ツール実行結果が含まれる場合がある
    if msg_type == "UserMessage" and hasattr(message, "content"):
        content = message.content
        if not content:
            return

        # content は ToolResultBlock のリスト
        if isinstance(content, list):
            for item in content:
                # ToolResultBlock - ツール実行結果
                if type(item).__name__ == "ToolResultBlock":
                    tool_result = getattr(item, "content", "")
                    is_error = getattr(item, "is_error", False)
                    result_str = str(tool_result)

                    # 結果の長さに応じて表示方法を変える
                    if len(result_str) > 500:
                        lines = result_str.split("\n")
                        preview = "\n".join(lines[:5])
                        if is_error:
                            print(
                                f"{Colors.RED}✗ Tool Error:{Colors.ENDC} ({len(result_str)} chars, {len(lines)} lines)",
                                flush=True,
                            )
                        else:
                            print(
                                f"{Colors.GREEN}✓ Tool Result:{Colors.ENDC} ({len(result_str)} chars, {len(lines)} lines)",
                                flush=True,
                            )
                        print(f"   {preview}", flush=True)
                        if len(lines) > 5:
                            print(
                                f"   {Colors.BLUE}... ({len(lines) - 5} more lines){Colors.ENDC}",
                                flush=True,
                            )
                    else:
                        if is_error:
                            print(f"{Colors.RED}✗ Tool Error:{Colors.ENDC}", flush=True)
                        else:
                            print(
                                f"{Colors.GREEN}✓ Tool Result:{Colors.ENDC}", flush=True
                            )
                        print(f"   {result_str}", flush=True)

    # ResultMessage - 最終応答
    if hasattr(message, "result") and message.result:
        result_preview = message.result[:200]
        if len(message.result) > 200:
            result_preview += "..."
        print(f"\n{Colors.GREEN}📨 Final Result:{Colors.ENDC}", flush=True)
        print(f"   {result_preview}", flush=True)

    # ErrorMessage - エラー
    if hasattr(message, "error") and message.error is not None:
        print(f"{Colors.RED}❌ Error:{Colors.ENDC} {message.error}", flush=True)


async def test_process_display():
    """プロセス表示のテスト"""

    # .envファイルを読み込み
    load_dotenv()

    # Note: Claude Code CLIを使用するため、Anthropic APIキーは不要
    print(f"{Colors.GREEN}✓ Claude Code CLI を使用（APIキー不要）{Colors.ENDC}\n")

    # テストケース
    test_queries = [
        {
            "name": "簡単な質問（ツール不使用）",
            "prompt": "Hello! What's 2+2?",
        },
        {
            "name": "ファイル操作（Read/Write）",
            "prompt": "Create a file called test.txt with content 'Hello from Agent SDK'",
        },
        {
            "name": "Bashコマンド実行",
            "prompt": "List all Python files in the current directory",
        },
    ]

    for i, test in enumerate(test_queries, 1):
        print(f"\n{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
        print(
            f"{Colors.BOLD}{Colors.CYAN}テスト {i}/{len(test_queries)}: {test['name']}{Colors.ENDC}"
        )
        print(f"{Colors.BLUE}📝 Query:{Colors.ENDC} {test['prompt']}")
        print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n")

        try:
            result_text = ""

            async for message in query(
                prompt=test["prompt"],
                options=ClaudeAgentOptions(
                    allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
                    permission_mode="bypassPermissions",  # テスト用に全許可
                    max_turns=10,
                ),
            ):
                # メッセージを表示
                log_agent_message(message)

                # 結果を取得
                if hasattr(message, "result"):
                    result_text = message.result

            print(f"\n{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.GREEN}✅ テスト {i} 完了{Colors.ENDC}")
            print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n")

            # 次のテストまで少し待機
            if i < len(test_queries):
                await asyncio.sleep(2)

        except Exception as e:
            print(f"{Colors.RED}❌ エラー: {e}{Colors.ENDC}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("=" * 80)
    print(" Agent SDK プロセス表示テスト")
    print("=" * 80)
    print(f"{Colors.ENDC}\n")

    asyncio.run(test_process_display())

    print(f"\n{Colors.BOLD}{Colors.GREEN}✅ 全てのテスト完了{Colors.ENDC}\n")
