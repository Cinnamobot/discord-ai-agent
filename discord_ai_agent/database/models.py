"""SQLAlchemy models for session and conversation storage"""

from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ThreadSession(Base):
    """Discord thread session tracking"""

    __tablename__ = "thread_sessions"

    thread_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    agent_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    conversations = relationship(
        "ConversationHistory", back_populates="session", cascade="all, delete-orphan"
    )
    tool_logs = relationship(
        "ToolLog", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ThreadSession(thread_id={self.thread_id}, user_id={self.user_id}, agent={self.agent_name})>"


class ConversationHistory(Base):
    """Conversation message history"""

    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(
        Integer,
        ForeignKey("thread_sessions.thread_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    message_id = Column(Integer, nullable=True)  # Discord message ID
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("ThreadSession", back_populates="conversations")

    def __repr__(self):
        return f"<ConversationHistory(id={self.id}, thread_id={self.thread_id}, role={self.role})>"


class ToolLog(Base):
    """Tool usage logs for analysis and debugging"""

    __tablename__ = "tool_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(
        Integer,
        ForeignKey("thread_sessions.thread_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tool_name = Column(String(100), nullable=False)
    tool_params = Column(Text, nullable=True)
    tool_result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("ThreadSession", back_populates="tool_logs")

    def __repr__(self):
        return f"<ToolLog(id={self.id}, thread_id={self.thread_id}, tool={self.tool_name})>"
