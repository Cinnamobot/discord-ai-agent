"""Session store for managing thread-based conversations with SQLite"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session

from .models import Base, ThreadSession, ConversationHistory, ToolLog

logger = logging.getLogger(__name__)


class SessionStore:
    """Manages persistent storage of thread sessions and conversation history"""

    def __init__(self, db_path: str = "sessions.db"):
        """
        Initialize the session store

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Create tables
        Base.metadata.create_all(self.engine)
        logger.info(f"Session store initialized: {self.db_path}")

    def _get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    # ========== Thread Session Management ==========

    def create_thread_session(
        self, thread_id: int, user_id: int, agent_name: str
    ) -> ThreadSession:
        """
        Create a new thread session

        Args:
            thread_id: Discord thread ID
            user_id: Discord user ID
            agent_name: Agent name

        Returns:
            Created ThreadSession
        """
        db = self._get_session()
        try:
            session = ThreadSession(
                thread_id=thread_id, user_id=user_id, agent_name=agent_name
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            logger.info(f"Created thread session: {thread_id} for user {user_id}")
            return session
        finally:
            db.close()

    def get_thread_session(self, thread_id: int) -> Optional[ThreadSession]:
        """
        Get thread session by thread ID

        Args:
            thread_id: Discord thread ID

        Returns:
            ThreadSession if exists, None otherwise
        """
        db = self._get_session()
        try:
            return (
                db.query(ThreadSession)
                .filter(ThreadSession.thread_id == thread_id)
                .first()
            )
        finally:
            db.close()

    def update_last_active(self, thread_id: int) -> None:
        """
        Update last active timestamp for a thread

        Args:
            thread_id: Discord thread ID
        """
        db = self._get_session()
        try:
            session = (
                db.query(ThreadSession)
                .filter(ThreadSession.thread_id == thread_id)
                .first()
            )
            if session:
                session.last_active_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()

    def set_thread_inactive(self, thread_id: int) -> None:
        """
        Mark a thread session as inactive

        Args:
            thread_id: Discord thread ID
        """
        db = self._get_session()
        try:
            session = (
                db.query(ThreadSession)
                .filter(ThreadSession.thread_id == thread_id)
                .first()
            )
            if session:
                session.is_active = False
                db.commit()
                logger.info(f"Thread session {thread_id} marked as inactive")
        finally:
            db.close()

    def get_user_sessions(
        self, user_id: int, active_only: bool = True
    ) -> List[ThreadSession]:
        """
        Get all sessions for a user

        Args:
            user_id: Discord user ID
            active_only: Only return active sessions

        Returns:
            List of ThreadSession objects
        """
        db = self._get_session()
        try:
            query = db.query(ThreadSession).filter(ThreadSession.user_id == user_id)
            if active_only:
                query = query.filter(ThreadSession.is_active == True)
            return query.order_by(desc(ThreadSession.last_active_at)).all()
        finally:
            db.close()

    # ========== Conversation History ==========

    def add_message(
        self, thread_id: int, role: str, content: str, message_id: Optional[int] = None
    ) -> ConversationHistory:
        """
        Add a message to conversation history

        Args:
            thread_id: Discord thread ID
            role: 'user' or 'assistant'
            content: Message content
            message_id: Discord message ID (optional)

        Returns:
            Created ConversationHistory
        """
        db = self._get_session()
        try:
            message = ConversationHistory(
                thread_id=thread_id, role=role, content=content, message_id=message_id
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            # Update last active
            self.update_last_active(thread_id)

            return message
        finally:
            db.close()

    def get_conversation_history(
        self, thread_id: int, limit: Optional[int] = None
    ) -> List[ConversationHistory]:
        """
        Get conversation history for a thread

        Args:
            thread_id: Discord thread ID
            limit: Maximum number of messages to retrieve (None = all)

        Returns:
            List of ConversationHistory objects, ordered by creation time
        """
        db = self._get_session()
        try:
            query = (
                db.query(ConversationHistory)
                .filter(ConversationHistory.thread_id == thread_id)
                .order_by(ConversationHistory.created_at)
            )

            if limit:
                query = query.limit(limit)

            return query.all()
        finally:
            db.close()

    def get_recent_messages(
        self, thread_id: int, count: int = 10
    ) -> List[ConversationHistory]:
        """
        Get recent messages from a thread

        Args:
            thread_id: Discord thread ID
            count: Number of recent messages to retrieve

        Returns:
            List of recent ConversationHistory objects
        """
        db = self._get_session()
        try:
            return (
                db.query(ConversationHistory)
                .filter(ConversationHistory.thread_id == thread_id)
                .order_by(desc(ConversationHistory.created_at))
                .limit(count)
                .all()
            )
        finally:
            db.close()

    # ========== Tool Logs ==========

    def log_tool_use(
        self,
        thread_id: int,
        tool_name: str,
        tool_params: Optional[str] = None,
        tool_result: Optional[str] = None,
    ) -> ToolLog:
        """
        Log a tool usage

        Args:
            thread_id: Discord thread ID
            tool_name: Name of the tool used
            tool_params: Tool parameters (JSON string)
            tool_result: Tool result

        Returns:
            Created ToolLog
        """
        db = self._get_session()
        try:
            log = ToolLog(
                thread_id=thread_id,
                tool_name=tool_name,
                tool_params=tool_params,
                tool_result=tool_result,
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            return log
        finally:
            db.close()

    def get_tool_logs(
        self, thread_id: int, limit: Optional[int] = None
    ) -> List[ToolLog]:
        """
        Get tool usage logs for a thread

        Args:
            thread_id: Discord thread ID
            limit: Maximum number of logs to retrieve

        Returns:
            List of ToolLog objects
        """
        db = self._get_session()
        try:
            query = (
                db.query(ToolLog)
                .filter(ToolLog.thread_id == thread_id)
                .order_by(ToolLog.created_at)
            )

            if limit:
                query = query.limit(limit)

            return query.all()
        finally:
            db.close()

    # ========== Statistics ==========

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            Dictionary with statistics
        """
        db = self._get_session()
        try:
            total_sessions = db.query(ThreadSession).count()
            active_sessions = (
                db.query(ThreadSession).filter(ThreadSession.is_active == True).count()
            )
            total_messages = db.query(ConversationHistory).count()
            total_tools = db.query(ToolLog).count()

            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "total_messages": total_messages,
                "total_tool_uses": total_tools,
            }
        finally:
            db.close()
