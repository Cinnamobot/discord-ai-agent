"""Claude CLI パス自動検知ユーティリティ"""

import os
import shutil
import sys
from pathlib import Path
from typing import Optional

import loguru


logger = loguru.logger


def find_claude_cli() -> Optional[Path]:
    """
    Claude CLI の実行パスを自動検知する

    検索順序:
    1. 環境変数 CLAUDE_CLI_PATH
    2. PATH環境変数から検索 (which/where)
    3. プラットフォーム別のデフォルトパス

    Returns:
        Path: Claude CLI の実行パス (見つからない場合は None)
    """

    # 1. 環境変数から取得
    env_path = os.getenv("CLAUDE_CLI_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists() and path.is_file():
            logger.info(f"Claude CLI を環境変数から検出: {path}")
            return path
        else:
            logger.warning(
                f"環境変数 CLAUDE_CLI_PATH が設定されていますが、ファイルが存在しません: {path}"
            )

    # 2. PATH環境変数から検索
    # Windows: claude.exe, Linux/macOS: claude
    executable_names = (
        ["claude.exe", "claude"] if sys.platform == "win32" else ["claude"]
    )

    for exe_name in executable_names:
        which_result = shutil.which(exe_name)
        if which_result:
            path = Path(which_result)
            logger.info(f"Claude CLI を PATH から検出: {path}")
            return path

    # 3. プラットフォーム別のデフォルトパスを試行
    default_paths = _get_default_paths()

    for path in default_paths:
        if path.exists() and path.is_file():
            logger.info(f"Claude CLI をデフォルトパスから検出: {path}")
            return path

    # 見つからなかった
    logger.error("Claude CLI が見つかりませんでした")
    logger.error("以下の方法で解決できます:")
    logger.error("  1. 環境変数 CLAUDE_CLI_PATH に Claude CLI のパスを設定")
    logger.error("  2. Claude CLI を PATH に追加")
    logger.error(
        "  3. Claude CLI をインストール: npm install -g @anthropic-ai/claude-cli"
    )

    return None


def _get_default_paths() -> list[Path]:
    """
    プラットフォーム別のデフォルトパスリストを取得

    Returns:
        list[Path]: 試行するパスのリスト
    """
    paths = []

    if sys.platform == "win32":
        # Windows
        userprofile = os.getenv("USERPROFILE", "")
        if userprofile:
            paths.extend(
                [
                    Path(userprofile) / ".local" / "bin" / "claude.exe",
                    Path(userprofile)
                    / "AppData"
                    / "Local"
                    / "Programs"
                    / "Claude"
                    / "claude.exe",
                    Path(userprofile) / "AppData" / "Roaming" / "npm" / "claude.exe",
                ]
            )

        # グローバルインストール
        paths.extend(
            [
                Path("C:/Program Files/Claude/claude.exe"),
                Path("C:/Program Files (x86)/Claude/claude.exe"),
            ]
        )

    else:
        # Linux / macOS
        home = Path.home()
        paths.extend(
            [
                home / ".local" / "bin" / "claude",
                Path("/usr/local/bin/claude"),
                Path("/usr/bin/claude"),
                home / ".npm-global" / "bin" / "claude",
            ]
        )

    return paths


def get_claude_cli_path_or_exit() -> Path:
    """
    Claude CLI のパスを取得し、見つからない場合は終了する

    Returns:
        Path: Claude CLI の実行パス
    """
    path = find_claude_cli()
    if path is None:
        logger.critical("Claude CLI が見つからないため、起動できません")
        sys.exit(1)
    return path
