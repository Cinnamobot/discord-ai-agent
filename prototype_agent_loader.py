"""
エージェント設定読み込みのプロトタイプ

agent.yaml と system_prompt.txt を読み込んで、
Agent SDK の ClaudeAgentOptions に適用できる形式に変換します。
"""

import sys
import io
import os
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List

# Windows環境での文字コード問題を回避
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


@dataclass
class AgentConfig:
    """エージェント設定"""

    name: str
    system_prompt: str
    allowed_commands: Optional[List[str]]
    workspace: Path
    agent_root: Path


def load_agent_config(agent_path: Path) -> AgentConfig:
    """
    エージェント設定を読み込む

    Args:
        agent_path: エージェントディレクトリのパス

    Returns:
        AgentConfig: エージェント設定

    Raises:
        ValueError: 設定ファイルが見つからない場合
    """
    agent_path = Path(agent_path).resolve()

    # agent.yaml を読み込み
    config_file = agent_path / "agent.yaml"
    if not config_file.exists():
        raise ValueError(f"agent.yaml not found in {agent_path}")

    with open(config_file, "r", encoding="utf-8") as f:
        agent_yaml = yaml.safe_load(f)

    # 名前を取得
    name = agent_yaml.get("name", agent_path.name)

    # allowed_commands を取得
    allowed_commands = agent_yaml.get("allowed_commands")

    # system_prompt を読み込み
    # 1. system_prompt.txt ファイルがあれば優先
    # 2. なければ agent.yaml の system_prompt フィールド
    prompt_file = agent_path / "system_prompt.txt"
    if prompt_file.exists():
        with open(prompt_file, "r", encoding="utf-8") as f:
            system_prompt = f.read()
    elif "system_prompt" in agent_yaml:
        system_prompt = agent_yaml["system_prompt"]
    else:
        raise ValueError(
            f"Neither system_prompt.txt nor system_prompt field found in {agent_path}"
        )

    # workspace ディレクトリ
    # 優先順位:
    # 1. agent.yaml の workspace フィールド（絶対パス）
    # 2. 環境変数 AGENT_WORKSPACE_ROOT
    # 3. デフォルト（エージェントディレクトリ内）
    workspace_config = agent_yaml.get("workspace")

    if workspace_config:
        # agent.yamlで指定されている場合
        workspace = Path(workspace_config)
        if not workspace.is_absolute():
            # 相対パスの場合はエージェントルートからの相対パス
            workspace = agent_path / workspace_config
    else:
        # 環境変数 AGENT_WORKSPACE_ROOT が設定されている場合はそちらを使用
        workspace_root = os.getenv("AGENT_WORKSPACE_ROOT")
        if workspace_root:
            workspace = Path(workspace_root) / name / "workspace"
        else:
            workspace = agent_path / "workspace"

    workspace.mkdir(parents=True, exist_ok=True)

    return AgentConfig(
        name=name,
        system_prompt=system_prompt,
        allowed_commands=allowed_commands,
        workspace=workspace,
        agent_root=agent_path,
    )


def agent_config_to_sdk_options(config: AgentConfig, **kwargs) -> dict:
    """
    AgentConfig を Agent SDK の ClaudeAgentOptions に変換

    Args:
        config: エージェント設定
        **kwargs: 追加のオプション

    Returns:
        dict: ClaudeAgentOptions に渡すパラメータ
    """
    from claude_agent_sdk import ClaudeAgentOptions

    options_dict = {
        "system_prompt": config.system_prompt,
        "cwd": str(config.workspace),
        "allowed_tools": ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    }

    # allowed_commands がある場合、Bash ツールのサブコマンドとして設定
    # Note: Agent SDK での実装方法を後で確認
    if config.allowed_commands:
        # 現時点では、allowed_tools に Bash を含めるかどうかの判断に使用
        options_dict["_allowed_commands"] = config.allowed_commands

    # 追加オプションをマージ
    options_dict.update(kwargs)

    return ClaudeAgentOptions(**options_dict)


def main():
    """テスト実行"""
    print("=" * 60)
    print("エージェント設定読み込みテスト")
    print("=" * 60)

    # テスト用のエージェントディレクトリ
    test_agents = ["./agents/default", "./agents/python-tutor"]

    for agent_dir in test_agents:
        agent_path = Path(agent_dir)

        print(f"\n📁 エージェント: {agent_path}")

        if not agent_path.exists():
            print(f"  ⚠️ ディレクトリが存在しません")
            continue

        try:
            # 設定を読み込み
            config = load_agent_config(agent_path)

            print(f"  ✅ 名前: {config.name}")
            print(f"  ✅ システムプロンプト: {len(config.system_prompt)} 文字")
            print(f"  ✅ 許可コマンド: {config.allowed_commands or '(制限なし)'}")
            print(f"  ✅ ワークスペース: {config.workspace}")

            # システムプロンプトのプレビュー
            preview = config.system_prompt[:200].replace("\n", " ")
            print(f"\n  --- システムプロンプト(プレビュー) ---")
            print(f"  {preview}...")

            # Agent SDK オプションへの変換テスト
            print(f"\n  🔧 Agent SDK オプションへの変換...")
            try:
                # sdk_options = agent_config_to_sdk_options(
                #     config,
                #     max_turns=10,
                #     permission_mode="bypassPermissions"
                # )
                # print(f"  ✅ 変換成功")
                print(f"  ⚠️ Agent SDK 認証問題のため、変換テストをスキップ")
            except Exception as e:
                print(f"  ❌ 変換エラー: {e}")

        except Exception as e:
            print(f"  ❌ エラー: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)


if __name__ == "__main__":
    main()
