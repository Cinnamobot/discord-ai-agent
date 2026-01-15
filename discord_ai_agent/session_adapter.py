"""Discordセッションアダプター - SDKセッションにDiscord固有の機能を追加"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any


@dataclass
class ConversationMessage:
    """会話メッセージ"""

    role: str  # 'user' or 'assistant'
    content: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class DiscordSession:
    """
    Discord固有のメタデータを持つセッション

    SDKセッションをラップし、Discord特有の機能を追加
    """

    session_id: str
    channel_id: int
    user_id: int
    agent_name: str
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    messages: List[ConversationMessage] = field(default_factory=list)
    bot_message_id: Optional[int] = None  # Botの最新メッセージID（返信用）

    # SDKセッションへの参照（SDK導入後に使用）
    sdk_session: Optional[Any] = None

    def add_message(self, role: str, content: str) -> None:
        """メッセージを追加"""
        self.messages.append(ConversationMessage(role=role, content=content))
        self.last_activity = time.time()

    def get_messages(self, max_length: Optional[int] = None) -> List[Dict[str, str]]:
        """
        メッセージ履歴を取得（最初のメッセージは保持）

        Args:
            max_length: 最大メッセージ数（Noneなら全て）

        Returns:
            メッセージのリスト
        """
        messages = self.messages

        # 最初のメッセージを保持したまま、最近のメッセージを取得
        if max_length is not None and len(messages) > max_length:
            # 最初のメッセージを保持
            first_message = messages[0]
            # 最近のmax_length-1件を取得
            recent = messages[-(max_length - 1) :]
            messages = [first_message] + recent

        return [{"role": msg.role, "content": msg.content} for msg in messages]

    def is_expired(self, ttl_minutes: int) -> bool:
        """セッションが期限切れかどうか"""
        elapsed = (time.time() - self.last_activity) / 60
        return elapsed > ttl_minutes


class DiscordSessionManager:
    """
    Discord固有のセッション管理クラス

    SDKセッションにDiscord特有の機能（TTL、bot_message_id追跡など）を追加
    """

    def __init__(self, ttl_minutes: int = 30, cleanup_interval: int = 300):
        """
        初期化

        Args:
            ttl_minutes: セッションの有効期限（分）
            cleanup_interval: クリーンアップ間隔（秒）
        """
        self.sessions: Dict[str, DiscordSession] = {}
        self.bot_message_map: Dict[
            int, str
        ] = {}  # bot_message_id -> session_id マッピング
        self.ttl_minutes = ttl_minutes
        self.cleanup_interval = cleanup_interval
        self._cleanup_task: Optional[asyncio.Task] = None

    def _generate_session_id(self, channel_id: int, user_id: int) -> str:
        """セッションIDを生成"""
        return f"{channel_id}-{user_id}"

    async def create_session(
        self,
        channel_id: int,
        user_id: int,
        agent_name: str,
        sdk_session: Optional[Any] = None,
    ) -> DiscordSession:
        """
        新しいセッションを作成

        Args:
            channel_id: DiscordチャンネルID
            user_id: DiscordユーザーID
            agent_name: エージェント名
            sdk_session: SDKセッションオブジェクト（オプション）

        Returns:
            作成されたセッション
        """
        session_id = self._generate_session_id(channel_id, user_id)

        session = DiscordSession(
            session_id=session_id,
            channel_id=channel_id,
            user_id=user_id,
            agent_name=agent_name,
            sdk_session=sdk_session,
        )

        self.sessions[session_id] = session
        return session

    async def get_session(
        self,
        channel_id: int,
        user_id: int,
    ) -> Optional[DiscordSession]:
        """
        セッションを取得

        Args:
            channel_id: DiscordチャンネルID
            user_id: DiscordユーザーID

        Returns:
            セッション（存在しない場合はNone）
        """
        session_id = self._generate_session_id(channel_id, user_id)
        session = self.sessions.get(session_id)

        if session and session.is_expired(self.ttl_minutes):
            # 期限切れの場合は削除
            del self.sessions[session_id]
            return None

        return session

    async def get_or_create_session(
        self,
        channel_id: int,
        user_id: int,
        agent_name: str,
        sdk_session_factory: Optional[callable] = None,
    ) -> DiscordSession:
        """
        セッションを取得または作成

        Args:
            channel_id: DiscordチャンネルID
            user_id: DiscordユーザーID
            agent_name: エージェント名
            sdk_session_factory: SDKセッションを作成する関数（新規作成時のみ呼ばれる）

        Returns:
            セッション
        """
        session = await self.get_session(channel_id, user_id)

        if session:
            session.last_activity = time.time()
            return session

        # 新しいSDKセッションを作成
        sdk_session = None
        if sdk_session_factory:
            session_id = self._generate_session_id(channel_id, user_id)
            sdk_session = sdk_session_factory(session_id)

        return await self.create_session(
            channel_id,
            user_id,
            agent_name,
            sdk_session,
        )

    async def get_session_by_bot_message(
        self,
        bot_message_id: int,
    ) -> Optional[DiscordSession]:
        """
        BotのメッセージIDからセッションを取得（返信によるセッション継続用）

        Args:
            bot_message_id: BotのメッセージID

        Returns:
            セッション（存在しない場合はNone）
        """
        # マッピングからsession_idを取得
        session_id = self.bot_message_map.get(bot_message_id)
        if not session_id:
            return None

        # セッションを取得
        session = self.sessions.get(session_id)
        if not session:
            # マッピングが古い場合は削除
            del self.bot_message_map[bot_message_id]
            return None

        # 期限切れチェック
        if session.is_expired(self.ttl_minutes):
            del self.sessions[session_id]
            del self.bot_message_map[bot_message_id]
            return None

        return session

    def register_bot_message(self, bot_message_id: int, session_id: str) -> None:
        """
        BotメッセージIDとセッションIDのマッピングを登録

        Args:
            bot_message_id: BotのメッセージID
            session_id: セッションID
        """
        self.bot_message_map[bot_message_id] = session_id

    async def update_session(
        self,
        channel_id: int,
        user_id: int,
        role: str,
        content: str,
    ) -> Optional[DiscordSession]:
        """
        セッションを更新（メッセージ追加）

        Args:
            channel_id: DiscordチャンネルID
            user_id: DiscordユーザーID
            role: 'user' or 'assistant'
            content: メッセージ内容

        Returns:
            更新されたセッション（存在しない場合はNone）
        """
        session = await self.get_session(channel_id, user_id)
        if session:
            session.add_message(role, content)
        return session

    def cleanup_expired(self) -> int:
        """
        期限切れのセッションをクリーンアップ

        Returns:
            削除されたセッション数
        """
        expired_keys = [
            session_id
            for session_id, session in self.sessions.items()
            if session.is_expired(self.ttl_minutes)
        ]

        for session_id in expired_keys:
            del self.sessions[session_id]

        return len(expired_keys)

    async def start_cleanup_task(self) -> None:
        """定期的なクリーンアップタスクを開始"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self) -> None:
        """クリーンアップループ"""
        while True:
            await asyncio.sleep(self.cleanup_interval)
            count = self.cleanup_expired()
            if count > 0:
                print(f"Cleaned up {count} expired sessions")

    def stop_cleanup_task(self) -> None:
        """クリーンアップタスクを停止"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
