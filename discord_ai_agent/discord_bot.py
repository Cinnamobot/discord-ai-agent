"""
Discord AI Agent Bot

Discord bot implementation using Claude Agent SDK with multiple specialized agent profiles.
"""

import asyncio
import logging
import os
import sys
import yaml
from pathlib import Path
from typing import Optional

import aiohttp

# 標準出力のバッファリングを無効化（リアルタイム表示のため）
# Windows用UTF-8エンコーディング設定（emoji・カラー対応）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
if hasattr(sys.stdout, "flush"):
    # Python 3.6以前の互換性
    import functools

    print = functools.partial(print, flush=True)

import discord
from discord.ext import commands

from .claude_cli_finder import find_claude_cli
from .database import SessionStore
from .message_queue import ThreadMessageQueue
from dotenv import load_dotenv
from datetime import datetime

# Agent SDK
from claude_agent_sdk import query, ClaudeAgentOptions

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 既存モジュール（セッション管理、レート制限など）
from discord_ai_agent.session_adapter import DiscordSessionManager
from discord_ai_agent.rate_limit import RateLimiter
from discord_ai_agent import file_manager

# エージェント設定ローダー
from discord_ai_agent.agent_loader import load_agent_config, AgentConfig
from discord_ai_agent.agent_registry import AgentRegistry

# ロギング設定（カラー出力対応）
logging.basicConfig(
    level=logging.INFO,  # INFOレベル（プロセス表示に最適）
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ターミナル用のカラーコード（ANSI）
class Colors:
    """ターミナル出力用カラーコード"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class DiscordAIBot(commands.Bot):
    """Discord AI Agent Bot - Agent SDK Integration"""

    def __init__(
        self, agents_dir: str = "./agents", intents: Optional[discord.Intents] = None
    ):
        """
        Initialize Discord AI Bot

        Args:
            agents_dir: Path to directory containing all agents (default: ./agents)
            intents: Discord intents (optional, uses defaults if not provided)
        """
        # Setup intents
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.messages = True
            intents.guilds = True
            intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )

        # Initialize agent registry (discovers all agents)
        try:
            self.agent_registry = AgentRegistry(agents_dir=agents_dir)
            logger.info(
                f"Agent registry initialized with {len(self.agent_registry.list_agents())} agents"
            )
        except Exception as e:
            logger.error(f"Failed to initialize agent registry: {e}")
            raise

        # セッション管理（SQLiteベース）
        # Use a shared database for all agents
        db_path = Path(agents_dir) / "shared_sessions.db"
        self.session_store = SessionStore(str(db_path))
        logger.info(f"セッションDB: {db_path}")

        # メッセージキュー（スレッド単位）
        self.message_queue = ThreadMessageQueue()
        logger.info("メッセージキューシステム初期化完了")

        # 旧セッション管理（後方互換性のため残す）
        # Note: TTLを無効化（セッションは永久保持）
        self.session_manager = DiscordSessionManager(
            ttl_minutes=999999,  # 実質無期限（約1900年）
            cleanup_interval=86400,  # クリーンアップは1日1回のみ
        )

        # レート制限
        self.rate_limiter = RateLimiter(
            per_minute=10,
            per_hour=100,
        )

        # Claude CLI パス（自動検知）
        self.claude_cli_path = find_claude_cli()
        if self.claude_cli_path is None:
            logger.critical("Claude CLI が見つかりません。起動を中止します。")
            raise FileNotFoundError(
                "Claude CLI が見つかりません。環境変数 CLAUDE_CLI_PATH を設定するか、"
                "Claude CLI を PATH に追加してください。"
            )
        logger.info(f"Claude CLI を使用: {self.claude_cli_path}")

        # 環境変数（Agent SDKに渡す）
        # Note: Claude Code CLIを使用するため、Anthropic APIキーは不要
        self.env_vars = {}

    async def on_ready(self):
        """Bot起動時の処理"""
        logger.info(f"ログイン成功: {self.user} (ID: {self.user.id})")

        # List all available agents
        agents = self.agent_registry.list_agents()
        logger.info(f"利用可能なエージェント: {', '.join([a.name for a in agents])}")

        # Setup slash commands
        try:
            from .commands import setup_commands

            await setup_commands(self)
            await self.tree.sync()
            logger.info(f"Slash commands synced")
        except Exception as e:
            logger.error(f"Failed to setup commands: {e}", exc_info=True)

        logger.info("Bot準備完了")

    async def on_message_delete(self, message: discord.Message):
        """メッセージ削除時の処理"""
        # スレッド内のメッセージのみ処理
        if isinstance(message.channel, discord.Thread):
            if message.channel.owner_id == self.user.id:
                # キューから削除済みとしてマーク
                if self.message_queue.mark_deleted(message.channel.id, message.id):
                    logger.info(
                        f"メッセージをキューから削除: thread={message.channel.id}, msg={message.id}"
                    )

    async def on_message(self, message: discord.Message):
        """メッセージ受信時の処理（スレッドベース）"""
        # 自分自身のメッセージは無視
        if message.author.bot:
            return

        # 1. チャンネルでのメンション → 新規スレッド作成
        if isinstance(message.channel, discord.TextChannel):
            if self.user.mentioned_in(message):
                logger.info(f"新規スレッド作成: {message.author.name}")
                await self.create_thread_and_start(message)
            return

        # 2. スレッド内のメッセージ → キューに追加して順次処理
        if isinstance(message.channel, discord.Thread):
            # Botが作成したスレッドのみ反応
            if message.channel.owner_id == self.user.id:
                logger.info(
                    f"スレッド内メッセージ: {message.author.name} in thread {message.channel.id}"
                )

                # メッセージをキューに追加
                position = self.message_queue.add_message(
                    thread_id=message.channel.id,
                    message_id=message.id,
                    user_id=message.author.id,
                    content=message.content,
                    has_attachments=bool(message.attachments),
                )

                # キュー位置を通知（オプション）
                if position > 0:
                    queue_size = self.message_queue.get_queue_size(message.channel.id)
                    await message.add_reaction("⏳")  # キューイング中を示す
                    logger.info(
                        f"メッセージをキューに追加: position={position}, queue_size={queue_size}"
                    )

                # 処理ワーカーを起動（既に実行中の場合はスキップ）
                await self.process_thread_queue(message.channel)
            return

    async def handle_new_conversation(self, message: discord.Message):
        """新規対話の処理"""
        logger.info(f"新規対話開始: {message.author.name} (ID: {message.author.id})")

        # レート制限チェック
        allowed, error_msg = await self.rate_limiter.check_rate_limit(message.author.id)
        if not allowed:
            await message.reply(f"⚠️ {error_msg}")
            return

        # メンション部分を除去
        content = message.content
        for mention in message.mentions:
            content = content.replace(f"<@{mention.id}>", "")
            content = content.replace(f"<@!{mention.id}>", "")
        content = content.strip()

        if not content:
            await message.reply(
                f"こんにちは！私は **{self.agent_config.name}** です。\n"
                "何かお手伝いできることはありますか？"
            )
            return

        # 添付ファイルの処理
        if message.attachments:
            try:
                await file_manager.download_attachments(
                    message.attachments,
                    self.agent_config.workspace,
                    max_file_size=1024 * 1024,  # 1MB
                )
                content += f"\n\n（{len(message.attachments)}個のファイルをworkspace/に保存しました）"
            except (OSError, aiohttp.ClientError) as e:
                logger.error(f"ファイルダウンロードエラー: {e}")
                await message.reply(f"⚠️ ファイルのダウンロードに失敗しました: {e}")
                return

        # Agent SDK でエージェント実行
        try:
            async with message.channel.typing():
                result_text, sdk_session_id = await self.run_agent_sdk(content)

            # 応答を送信（Discord 2000文字制限対応）
            bot_message = await self.send_response(message, result_text)

            # セッション取得または作成（Agent SDK session_idを保存）
            if bot_message:
                # 既存セッションを取得、なければ作成
                session = await self.session_manager.get_or_create_session(
                    channel_id=message.channel.id,
                    user_id=message.author.id,
                    agent_name=self.agent_config.name,
                )

                # 新規メンションの場合はメッセージ履歴をリセット
                # （同じユーザーが新しい話題を始めた場合）
                session.messages = []

                # Agent SDKのセッションIDとbot_message_idを更新
                session.sdk_session = sdk_session_id
                session.bot_message_id = bot_message.id

                # bot_message_idマッピングを登録
                self.session_manager.register_bot_message(
                    bot_message.id, session.session_id
                )

                # メッセージ履歴に追加
                session.add_message("user", content)
                session.add_message("assistant", result_text)

                logger.info(
                    f"セッション作成: session_id={session.session_id}, "
                    f"sdk_session_id={sdk_session_id}, "
                    f"bot_message_id={bot_message.id}"
                )

        except (
            discord.HTTPException,
            discord.Forbidden,
            asyncio.TimeoutError,
            RuntimeError,
        ) as e:
            logger.error(f"エージェント実行エラー: {e}", exc_info=True)
            await message.reply(
                f"❌ エラーが発生しました: {str(e)}\n詳細はログを確認してください。"
            )

    async def handle_reply_conversation(self, message: discord.Message):
        """返信による対話継続の処理"""
        replied_message_id = message.reference.message_id
        logger.info(
            f"対話継続リクエスト: {message.author.name} -> message_id={replied_message_id}"
        )

        # メンションなしの返信は無視
        if not self.user.mentioned_in(message):
            logger.debug("メンションなしの返信はスキップ")
            return

        # セッション取得（bot_message_idから検索）
        logger.debug(f"セッション検索: bot_message_id={replied_message_id}")
        session = await self.session_manager.get_session_by_bot_message(
            replied_message_id
        )

        if not session:
            logger.warning(
                f"セッションが見つかりません: bot_message_id={replied_message_id}"
            )
            logger.debug(
                f"現在のセッション一覧: {list(self.session_manager.sessions.keys())}"
            )
            logger.info("新規対話として処理します。")
            await self.handle_new_conversation(message)
            return

        logger.info(
            f"セッション発見: session_id={session.session_id}, sdk_session={session.sdk_session}"
        )

        # 権限チェック
        if session.user_id != message.author.id:
            await message.reply("⚠️ このセッションは別のユーザーのものです。")
            return

        # レート制限チェック
        allowed, error_msg = await self.rate_limiter.check_rate_limit(message.author.id)
        if not allowed:
            await message.reply(f"⚠️ {error_msg}")
            return

        # メンション部分を除去
        content = message.content
        for mention in message.mentions:
            content = content.replace(f"<@{mention.id}>", "")
            content = content.replace(f"<@!{mention.id}>", "")
        content = content.strip()

        # 添付ファイルの処理
        if message.attachments:
            try:
                await file_manager.download_attachments(
                    message.attachments,
                    self.agent_config.workspace,
                    max_file_size=1024 * 1024,  # 1MB
                )
                content += f"\n\n（{len(message.attachments)}個のファイルをworkspace/に保存しました）"
            except (OSError, aiohttp.ClientError) as e:
                logger.error(f"ファイルダウンロードエラー: {e}")
                await message.reply(f"⚠️ ファイルのダウンロードに失敗しました: {e}")
                return

        # Agent SDK でエージェント実行（セッション継続）
        try:
            async with message.channel.typing():
                # Agent SDKのセッションIDを使用してセッション継続
                sdk_session_id = session.sdk_session
                logger.info(f"セッション継続: sdk_session_id={sdk_session_id}")

                result_text, new_sdk_session_id = await self.run_agent_sdk(
                    content, sdk_session_id=sdk_session_id
                )

            # 応答を送信
            bot_message = await self.send_response(message, result_text)

            # セッション更新
            if bot_message:
                # メッセージ履歴に追加
                session.add_message("user", content)
                session.add_message("assistant", result_text)

                # 新しいbot_message_idとsdk_session_idを更新
                session.bot_message_id = bot_message.id
                if new_sdk_session_id:
                    session.sdk_session = new_sdk_session_id

                # bot_message_idマッピングを更新
                self.session_manager.register_bot_message(
                    bot_message.id, session.session_id
                )

                logger.info(
                    f"セッション更新: bot_message_id={bot_message.id}, "
                    f"sdk_session_id={new_sdk_session_id}, "
                    f"メッセージ数={len(session.messages)}"
                )

        except (
            discord.HTTPException,
            discord.Forbidden,
            asyncio.TimeoutError,
            RuntimeError,
        ) as e:
            logger.error(f"エージェント実行エラー: {e}", exc_info=True)
            await message.reply(
                f"❌ エラーが発生しました: {str(e)}\n詳細はログを確認してください。"
            )

    async def run_agent_sdk(
        self, user_message: str, sdk_session_id: Optional[str] = None
    ) -> tuple[str, Optional[str]]:
        """
        Agent SDK を使用してエージェントを実行

        Args:
            user_message: ユーザーメッセージ
            sdk_session_id: Agent SDKのセッションID（セッション継続時）

        Returns:
            tuple[str, Optional[str]]: (エージェントの応答, 新しいセッションID)
        """
        result_text = ""
        new_session_id = None

        print(f"\n{Colors.HEADER}{'=' * 80}{Colors.ENDC}", flush=True)
        print(
            f"{Colors.BOLD}{Colors.CYAN}🤖 Agent SDK 実行開始{Colors.ENDC}", flush=True
        )
        print(
            f"{Colors.BLUE}📝 User Message:{Colors.ENDC} {user_message[:100]}...",
            flush=True,
        )
        if sdk_session_id:
            print(
                f"{Colors.YELLOW}🔄 Session Resume:{Colors.ENDC} {sdk_session_id[:20]}...",
                flush=True,
            )
        print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n", flush=True)

        try:
            async for message in query(
                prompt=user_message,
                options=ClaudeAgentOptions(
                    system_prompt=self.agent_config.system_prompt,
                    allowed_tools=[
                        "Read",
                        "Write",
                        "Edit",
                        "Bash",
                        "Glob",
                        "Grep",
                        "WebSearch",
                    ],
                    cwd=str(self.agent_config.workspace),
                    cli_path=str(self.claude_cli_path),
                    permission_mode="bypassPermissions",  # Auto-approve all tools including WebSearch
                    max_turns=15,
                    env=self.env_vars,
                    resume=sdk_session_id,  # Session continuity support
                ),
            ):
                # ストリーミングメッセージを表示
                self._log_agent_message(message)

                # ResultMessage を取得
                if hasattr(message, "result"):
                    result_text = message.result
                # セッションIDを取得
                if hasattr(message, "session_id"):
                    new_session_id = message.session_id
                    logger.debug(f"Agent SDK session_id: {new_session_id}")

        except (RuntimeError, OSError, ValueError) as e:
            logger.error(f"❌ Agent SDK実行エラー: {e}", exc_info=True)
            raise

        if not result_text:
            result_text = "（応答がありませんでした）"

        print(f"\n{Colors.HEADER}{'=' * 80}{Colors.ENDC}", flush=True)
        print(
            f"{Colors.BOLD}{Colors.GREEN}✅ Agent SDK 実行完了{Colors.ENDC}", flush=True
        )
        print(
            f"{Colors.BLUE}📤 Response Length:{Colors.ENDC} {len(result_text)} chars",
            flush=True,
        )
        print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n", flush=True)

        return result_text, new_session_id

    def _log_agent_message(self, message) -> None:
        """
        Agent SDKのメッセージをターミナルに表示（カラー出力）

        Args:
            message: Agent SDKから返されるメッセージオブジェクト
        """
        # デバッグ: メッセージタイプをログ出力（開発時のみ）
        msg_type = type(message).__name__
        logger.debug(f"Message type: {msg_type}")

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
                                f"{Colors.CYAN}💭 Claude Thinking:{Colors.ENDC}",
                                flush=True,
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
                                print(
                                    f"{Colors.RED}✗ Tool Error:{Colors.ENDC}",
                                    flush=True,
                                )
                            else:
                                print(
                                    f"{Colors.GREEN}✓ Tool Result:{Colors.ENDC}",
                                    flush=True,
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

        # デバッグ用（必要に応じてコメントアウト）
        # logger.debug(f"Message Type: {type(message).__name__}")

    async def send_response(
        self, message: discord.Message, response: str
    ) -> Optional[discord.Message]:
        """
        Discordに応答を送信（2000文字制限対応）

        Args:
            message: 元のメッセージ
            response: 応答テキスト

        Returns:
            送信したメッセージ（最初の1つ）
        """
        # Discord の文字数制限は2000文字（「続き」などを考慮して少し余裕を持つ）
        MAX_LENGTH = 1950

        if len(response) <= MAX_LENGTH:
            return await message.reply(response)

        # 長い応答は分割して送信
        parts = []
        current_part = ""

        for line in response.split("\n"):
            # 1行がMAX_LENGTHを超える場合は強制的に分割
            if len(line) > MAX_LENGTH:
                # 現在のパートを保存
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                # 長い行を分割
                for i in range(0, len(line), MAX_LENGTH):
                    chunk = line[i : i + MAX_LENGTH]
                    parts.append(chunk)
            elif len(current_part) + len(line) + 1 > MAX_LENGTH:
                parts.append(current_part)
                current_part = line
            else:
                if current_part:
                    current_part += "\n" + line
                else:
                    current_part = line

        if current_part:
            parts.append(current_part)

        # 最初のパートを返信、残りは通常メッセージ
        first_message = await message.reply(parts[0])

        for part in parts[1:]:
            # 「続き」を追加しても2000文字を超えないようにする
            if len(part) > 1950:
                part = part[:1950] + "..."
            await message.channel.send(f"（続き）\n{part}")

        return first_message

    # ========== スレッドベースの会話管理 ==========

    async def create_thread_and_start(
        self, message: discord.Message, agent_name: Optional[str] = None
    ):
        """
        新規スレッドを作成して会話を開始

        Args:
            message: ユーザーのメンション付きメッセージ
            agent_name: 使用するエージェント名 (Noneの場合はチャンネルのデフォルトを使用)
        """
        # レート制限チェック
        allowed, error_msg = await self.rate_limiter.check_rate_limit(message.author.id)
        if not allowed:
            await message.reply(f"⚠️ {error_msg}")
            return

        # エージェント名が指定されていない場合、チャンネルのデフォルトを取得
        if agent_name is None:
            settings = self.session_store.get_channel_settings(message.channel.id)
            if settings and settings.default_agent:
                agent_name = settings.default_agent
                logger.info(f"Using channel default agent: {agent_name}")
            else:
                agent_name = self.agent_registry.get_default_agent_name()
                logger.info(f"Using global default agent: {agent_name}")

        # エージェント設定を取得
        try:
            agent_config = self.agent_registry.get_agent(agent_name)
        except ValueError as e:
            await message.reply(f"⚠️ エージェント '{agent_name}' が見つかりません: {e}")
            return

        # メンション部分を除去
        content = message.content
        for mention in message.mentions:
            content = content.replace(f"<@{mention.id}>", "")
            content = content.replace(f"<@!{mention.id}>", "")
        content = content.strip()

        # スレッド作成
        thread_name = f"🤖 {message.author.display_name} - {datetime.now().strftime('%m/%d %H:%M')}"
        try:
            thread = await message.create_thread(
                name=thread_name[:100],  # Discord thread name limit
                auto_archive_duration=1440,  # 24 hours
            )
            logger.info(f"スレッド作成成功: {thread.id} - {thread_name}")
        except discord.HTTPException as e:
            logger.error(f"スレッド作成エラー: {e}")
            await message.reply(f"⚠️ スレッドの作成に失敗しました: {e}")
            return

        # データベースにセッションを即座に記録（重要: キュー処理前に作成）
        self.session_store.create_thread_session(
            thread_id=thread.id,
            user_id=message.author.id,
            agent_name=agent_name,
        )
        logger.info(f"セッション作成完了: thread_id={thread.id}, agent={agent_name}")

        # 挨拶メッセージ
        greeting = f"👋 {message.author.mention} こんにちは！\n"
        if content:
            greeting += f"\n> {content[:100]}{'...' if len(content) > 100 else ''}\n\nについて対応します。"
        else:
            greeting += f"私は **{agent_config.name}** です。何をお手伝いしましょうか？"

        await thread.send(greeting)

        # 初回プロンプトがある場合は直接処理（元メッセージはスレッド外なので）
        if content:
            # 添付ファイルの処理
            if message.attachments:
                try:
                    await file_manager.download_attachments(
                        message.attachments,
                        agent_config.workspace,
                        max_file_size=1024 * 1024,  # 1MB
                    )
                    content += f"\n\n（{len(message.attachments)}個のファイルをworkspace/に保存しました）"
                except (OSError, aiohttp.ClientError) as e:
                    logger.error(f"ファイルダウンロードエラー: {e}")
                    await thread.send(f"⚠️ ファイルのダウンロードに失敗しました: {e}")
                    return

            # 処理中フラグを立てる（他のメッセージがキューイングされるように）
            self.message_queue.set_processing(thread.id, True)

            try:
                # 初回メッセージを処理
                await self.process_in_thread(thread, content, message.author.id)
            finally:
                # 処理中フラグを下ろす
                self.message_queue.set_processing(thread.id, False)

                # キューに溜まっている他のメッセージを処理
                await self.process_thread_queue(thread)

    async def process_thread_queue(self, thread: discord.Thread):
        """
        スレッドのメッセージキューを順次処理

        Args:
            thread: Discord thread
        """
        thread_id = thread.id

        # 既に処理中の場合はスキップ
        if self.message_queue.is_processing(thread_id):
            logger.debug(f"Thread {thread_id} is already being processed")
            return

        # ロックを取得して処理開始
        async with self.message_queue.get_lock(thread_id):
            self.message_queue.set_processing(thread_id, True)

            try:
                # キューが空になるまで処理
                while True:
                    queued_msg = self.message_queue.get_next_message(thread_id)

                    if queued_msg is None:
                        # キューが空になった
                        logger.info(f"Queue empty for thread {thread_id}")
                        break

                    # メッセージを取得（削除されていないか確認）
                    try:
                        message = await thread.fetch_message(queued_msg.message_id)
                    except discord.NotFound:
                        logger.info(
                            f"Message {queued_msg.message_id} not found (deleted)"
                        )
                        continue
                    except discord.HTTPException as e:
                        logger.error(
                            f"Failed to fetch message {queued_msg.message_id}: {e}"
                        )
                        continue

                    # リアクションを削除（キューイング中マーク）
                    try:
                        await message.remove_reaction("⏳", self.user)
                    except:
                        pass

                    # メッセージを処理
                    await self.handle_thread_message(message)

            finally:
                self.message_queue.set_processing(thread_id, False)

    async def handle_thread_message(self, message: discord.Message):
        """
        スレッド内のメッセージを処理（キューから取り出された後）

        Args:
            message: スレッド内のユーザーメッセージ
        """
        thread = message.channel

        # レート制限チェック
        allowed, error_msg = await self.rate_limiter.check_rate_limit(message.author.id)
        if not allowed:
            await thread.send(f"⚠️ {error_msg}")
            return

        # セッションの存在確認と更新
        session = self.session_store.get_thread_session(thread.id)
        if not session:
            logger.warning(f"セッションが見つかりません: thread_id={thread.id}")
            await thread.send(
                "⚠️ セッション情報が見つかりません。新しいスレッドを作成してください。"
            )
            return

        # スレッドのエージェント設定を取得
        try:
            agent_config = self.agent_registry.get_agent(session.agent_name)
        except ValueError as e:
            logger.error(f"Failed to load agent '{session.agent_name}': {e}")
            await thread.send(
                f"⚠️ エージェント '{session.agent_name}' の読み込みに失敗しました"
            )
            return

        # 添付ファイルの処理
        content = message.content
        if message.attachments:
            try:
                await file_manager.download_attachments(
                    message.attachments,
                    agent_config.workspace,
                    max_file_size=1024 * 1024,  # 1MB
                )
                content += f"\n\n（{len(message.attachments)}個のファイルをworkspace/に保存しました）"
            except (OSError, aiohttp.ClientError) as e:
                logger.error(f"ファイルダウンロードエラー: {e}")
                await thread.send(f"⚠️ ファイルのダウンロードに失敗しました: {e}")
                return

        # Agent処理
        await self.process_in_thread(thread, content, message.author.id)

    async def process_in_thread(
        self, thread: discord.Thread, user_prompt: str, user_id: int
    ):
        """
        スレッド内でAgentを実行し、思考プロセスを可視化

        Args:
            thread: Discord thread
            user_prompt: ユーザーのプロンプト
            user_id: ユーザーID
        """
        # ユーザーメッセージをDBに保存
        self.session_store.add_message(
            thread_id=thread.id, role="user", content=user_prompt
        )

        # 既存のセッションを取得
        session = self.session_store.get_thread_session(thread.id)
        if not session:
            logger.error(f"Session not found for thread {thread.id}")
            await thread.send("⚠️ セッション情報が見つかりません")
            return

        sdk_session_id = session.sdk_session_id

        # スレッドのエージェント設定を取得
        try:
            agent_config = self.agent_registry.get_agent(session.agent_name)
        except ValueError as e:
            logger.error(f"Failed to load agent '{session.agent_name}': {e}")
            await thread.send(
                f"⚠️ エージェント '{session.agent_name}' の読み込みに失敗しました"
            )
            return

        # ステータスメッセージ
        if sdk_session_id:
            status_msg = await thread.send("🤔 処理中...（会話を継続）")
            logger.info(f"Resuming session: {sdk_session_id}")
        else:
            status_msg = await thread.send("🤔 処理中...（新規会話）")
            logger.info("Starting new session")

        # ターミナルログ出力開始
        print(f"\n{Colors.HEADER}{'=' * 80}{Colors.ENDC}", flush=True)
        print(
            f"{Colors.BOLD}{Colors.CYAN}🤖 Agent SDK 実行開始{Colors.ENDC}", flush=True
        )
        print(f"{Colors.BLUE}📝 Thread:{Colors.ENDC} {thread.id}", flush=True)
        print(f"{Colors.BLUE}📝 Agent:{Colors.ENDC} {agent_config.name}", flush=True)
        print(
            f"{Colors.BLUE}📝 User Message:{Colors.ENDC} {user_prompt[:100]}...",
            flush=True,
        )
        if sdk_session_id:
            print(
                f"{Colors.YELLOW}🔄 Session Resume:{Colors.ENDC} {sdk_session_id[:20]}...",
                flush=True,
            )
        print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n", flush=True)

        try:
            async with thread.typing():
                result_text = ""
                current_tool = None
                new_session_id = None
                current_tool_message = None  # ツールメッセージのIDを保持
                seen_thinking = set()  # 表示済みの思考を追跡（重複防止）

                # Agent SDK実行
                async for agent_message in query(
                    prompt=user_prompt,
                    options=ClaudeAgentOptions(
                        cli_path=str(self.claude_cli_path),
                        permission_mode="bypassPermissions",  # 全ツールを自動承認
                        max_turns=20,
                        env=self.env_vars,
                        cwd=str(agent_config.workspace),
                        system_prompt=agent_config.system_prompt,
                        resume=sdk_session_id,  # セッションを継続
                    ),
                ):
                    # ターミナルにログ表示
                    self._log_agent_message(agent_message)

                    # Discord表示用にメッセージを解析
                    msg_type = type(agent_message).__name__

                    # AssistantMessage - 思考とツール使用を含む
                    if msg_type == "AssistantMessage" and hasattr(
                        agent_message, "content"
                    ):
                        content = agent_message.content
                        if isinstance(content, list):
                            # まずツール使用があるかチェック
                            has_tool_use = any(
                                type(item).__name__ == "ToolUseBlock"
                                for item in content
                            )

                            for item in content:
                                item_type = type(item).__name__

                                # ThinkingBlock - 思考プロセス（-# プレフィックス）
                                # ツール使用がある場合のみ表示（最終結果との重複を避ける）
                                if item_type == "ThinkingBlock" and has_tool_use:
                                    thinking_text = getattr(item, "thinking", "")
                                    if (
                                        thinking_text
                                        and thinking_text not in seen_thinking
                                    ):
                                        seen_thinking.add(thinking_text)
                                        thinking_preview = thinking_text[:300]
                                        if len(thinking_text) > 300:
                                            thinking_preview += "..."
                                        # -# を各行の先頭に付ける
                                        thinking_lines = thinking_preview.split("\n")
                                        formatted_thinking = "\n".join(
                                            f"-# {line}" for line in thinking_lines
                                        )
                                        await thread.send(f"💭 {formatted_thinking}")

                                # TextBlock - テキスト
                                # ツール使用がある場合は思考として表示、ない場合は最終結果なのでスキップ
                                elif item_type == "TextBlock" and has_tool_use:
                                    text = getattr(item, "text", "")
                                    if (
                                        text
                                        and len(text) > 20
                                        and text not in seen_thinking
                                    ):
                                        seen_thinking.add(text)
                                        text_preview = text[:300]
                                        if len(text) > 300:
                                            text_preview += "..."
                                        # -# を各行の先頭に付ける
                                        text_lines = text_preview.split("\n")
                                        formatted_text = "\n".join(
                                            f"-# {line}" for line in text_lines
                                        )
                                        await thread.send(f"💭 {formatted_text}")

                                # ToolUseBlock - ツール使用
                                elif item_type == "ToolUseBlock":
                                    tool_name = getattr(item, "name", "unknown")
                                    tool_input = getattr(item, "input", {})
                                    current_tool = tool_name

                                    # パラメータを簡潔に表示
                                    params_summary = ""
                                    if isinstance(tool_input, dict):
                                        import json

                                        # 重要なパラメータのみ表示
                                        key_params = {}
                                        if "filePath" in tool_input:
                                            key_params["file"] = tool_input["filePath"]
                                        if "command" in tool_input:
                                            key_params["cmd"] = tool_input["command"][
                                                :50
                                            ]
                                        if "pattern" in tool_input:
                                            key_params["pattern"] = tool_input[
                                                "pattern"
                                            ]
                                        if "url" in tool_input:
                                            key_params["url"] = tool_input["url"]

                                        if key_params:
                                            params_summary = " → " + ", ".join(
                                                f"{k}: {v}"
                                                for k, v in key_params.items()
                                            )

                                        # DBログ用に完全なパラメータを保存
                                        params_str = json.dumps(
                                            tool_input, indent=2, ensure_ascii=False
                                        )
                                    else:
                                        params_str = str(tool_input)[:500]

                                    # ツールメッセージを送信（後で編集する）
                                    tool_msg = f"```\n🔧 {tool_name}{params_summary}\n⚙️ 実行中...\n```"
                                    current_tool_message = await thread.send(tool_msg)

                                    await status_msg.edit(
                                        content=f"⚙️ 実行中: {tool_name}..."
                                    )

                                    # DBにツールログ保存
                                    self.session_store.log_tool_use(
                                        thread_id=thread.id,
                                        tool_name=tool_name,
                                        tool_params=params_str
                                        if "params_str" in locals()
                                        else "",
                                    )

                    # UserMessage - ツール結果を含む
                    if msg_type == "UserMessage" and hasattr(agent_message, "content"):
                        content = agent_message.content
                        if isinstance(content, list):
                            for item in content:
                                item_type = type(item).__name__

                                # ToolResultBlock - ツール実行結果
                                if item_type == "ToolResultBlock":
                                    tool_result = getattr(item, "content", "")
                                    is_error = getattr(item, "is_error", False)
                                    result_str = str(tool_result)

                                    # ツールメッセージを編集して結果を表示
                                    if current_tool_message:
                                        if is_error:
                                            updated_msg = f"```\n🔧 {current_tool}\n❌ エラー: {result_str[:200]}\n```"
                                        else:
                                            # 結果が長い場合は行数を表示
                                            if len(result_str) > 200:
                                                line_count = result_str.count("\n") + 1
                                                updated_msg = f"```\n🔧 {current_tool}\n✓ 完了 ({len(result_str)} chars, {line_count} lines)\n```"
                                            else:
                                                updated_msg = f"```\n🔧 {current_tool}\n✓ 完了\n```"

                                        try:
                                            await current_tool_message.edit(
                                                content=updated_msg
                                            )
                                        except discord.HTTPException as e:
                                            logger.warning(
                                                f"Failed to edit tool message: {e}"
                                            )

                                        current_tool_message = None  # リセット

                    # ResultMessage - 最終結果
                    if msg_type == "ResultMessage":
                        if hasattr(agent_message, "result") and agent_message.result:
                            result_text = agent_message.result

                        # セッションIDを取得
                        if (
                            hasattr(agent_message, "session_id")
                            and agent_message.session_id
                        ):
                            new_session_id = agent_message.session_id
                            logger.info(f"Got session ID: {new_session_id}")

                        # エラーチェック
                        if (
                            hasattr(agent_message, "is_error")
                            and agent_message.is_error
                        ):
                            await thread.send(f"❌ **エラーが発生しました**")
                            await status_msg.delete()
                            return

                # セッションIDをDBに保存
                if new_session_id:
                    self.session_store.update_sdk_session_id(thread.id, new_session_id)

                # ステータスメッセージを削除
                await status_msg.delete()

                # 最終応答を送信
                if result_text:
                    await self.send_response_to_thread(thread, result_text)

                    # DBに保存
                    self.session_store.add_message(
                        thread_id=thread.id, role="assistant", content=result_text
                    )
                else:
                    await thread.send("⚠️ 応答がありませんでした。")

                # ターミナルログ出力終了
                print(f"\n{Colors.HEADER}{'=' * 80}{Colors.ENDC}", flush=True)
                print(
                    f"{Colors.BOLD}{Colors.GREEN}✅ Agent SDK 実行完了{Colors.ENDC}",
                    flush=True,
                )
                print(
                    f"{Colors.BLUE}📤 Response Length:{Colors.ENDC} {len(result_text)} chars",
                    flush=True,
                )
                print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n", flush=True)

        except Exception as e:
            logger.error(f"Agent実行エラー: {e}", exc_info=True)
            await status_msg.edit(content=f"❌ エラーが発生しました: {e}")

            # ターミナルにエラー出力
            print(f"\n{Colors.RED}❌ Agent実行エラー:{Colors.ENDC} {e}", flush=True)
            print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n", flush=True)

    async def send_response_to_thread(self, thread: discord.Thread, response: str):
        """
        スレッドに応答を送信（2000文字制限対応）

        Args:
            thread: Discord thread
            response: 応答テキスト
        """
        MAX_LENGTH = 1950

        if len(response) <= MAX_LENGTH:
            await thread.send(response)
            return

        # 長い応答は分割して送信
        parts = []
        current_part = ""

        for line in response.split("\n"):
            if len(line) > MAX_LENGTH:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                # 長い行を分割
                for i in range(0, len(line), MAX_LENGTH):
                    parts.append(line[i : i + MAX_LENGTH])
            elif len(current_part) + len(line) + 1 > MAX_LENGTH:
                parts.append(current_part)
                current_part = line
            else:
                if current_part:
                    current_part += "\n" + line
                else:
                    current_part = line

        if current_part:
            parts.append(current_part)

        # 分割して送信
        for i, part in enumerate(parts):
            if i == 0:
                await thread.send(part)
            else:
                if len(part) > 1950:
                    part = part[:1950] + "..."
                await thread.send(f"（続き）\n{part}")


def main():
    """メイン関数"""
    # .env ファイルを読み込み
    load_dotenv()

    # コマンドライン引数からエージェントディレクトリを取得
    import sys

    agents_dir = "./agents"
    if len(sys.argv) >= 2:
        agents_dir = sys.argv[1]

    agents_path = Path(agents_dir)

    if not agents_path.exists():
        print(f"エラー: エージェントディレクトリが見つかりません: {agents_path}")
        print(f"使用方法: python run.py [agents_directory]")
        print(f"例: python run.py ./agents")
        sys.exit(1)

    # Discord Bot Token 確認
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not bot_token:
        print("エラー: DISCORD_BOT_TOKEN が設定されていません")
        print(".env ファイルで設定してください")
        sys.exit(1)

    # Bot 起動 (multi-agent support)
    bot = DiscordAIBot(agents_dir=str(agents_path))

    try:
        logger.info(f"Bot起動中 (agents directory: {agents_path})")
        bot.run(bot_token)
    except KeyboardInterrupt:
        logger.info("Bot停止（KeyboardInterrupt）")
    except (discord.LoginFailure, discord.HTTPException, discord.GatewayNotFound) as e:
        logger.error(f"Bot実行エラー: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
