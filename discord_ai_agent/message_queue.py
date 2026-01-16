"""Message queue system for thread-based conversation processing"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, Optional
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class QueuedMessage:
    """Queued message with metadata"""

    message_id: int
    user_id: int
    content: str
    has_attachments: bool
    deleted: bool = False


class ThreadMessageQueue:
    """
    Manages message queues per thread to prevent race conditions

    Features:
    - One queue per thread
    - Process messages sequentially
    - Handle deleted messages before processing
    - Thread-safe with asyncio locks
    """

    def __init__(self):
        """Initialize the message queue system"""
        self._queues: Dict[int, deque] = {}  # thread_id -> deque of QueuedMessage
        self._locks: Dict[int, asyncio.Lock] = {}  # thread_id -> processing lock
        self._processing: Dict[int, bool] = {}  # thread_id -> is_processing flag

    def add_message(
        self,
        thread_id: int,
        message_id: int,
        user_id: int,
        content: str,
        has_attachments: bool = False,
    ) -> int:
        """
        Add a message to the thread queue

        Args:
            thread_id: Discord thread ID
            message_id: Discord message ID
            user_id: User ID
            content: Message content
            has_attachments: Whether message has attachments

        Returns:
            Queue position (0-indexed)
        """
        if thread_id not in self._queues:
            self._queues[thread_id] = deque()
            self._locks[thread_id] = asyncio.Lock()
            self._processing[thread_id] = False

        queued_msg = QueuedMessage(
            message_id=message_id,
            user_id=user_id,
            content=content,
            has_attachments=has_attachments,
        )

        self._queues[thread_id].append(queued_msg)
        queue_position = len(self._queues[thread_id]) - 1

        logger.info(
            f"Message queued: thread={thread_id}, msg={message_id}, "
            f"position={queue_position}, queue_size={len(self._queues[thread_id])}"
        )

        return queue_position

    def mark_deleted(self, thread_id: int, message_id: int) -> bool:
        """
        Mark a message as deleted in the queue

        Args:
            thread_id: Discord thread ID
            message_id: Discord message ID

        Returns:
            True if message was found and marked, False otherwise
        """
        if thread_id not in self._queues:
            return False

        for msg in self._queues[thread_id]:
            if msg.message_id == message_id:
                msg.deleted = True
                logger.info(
                    f"Message marked as deleted: thread={thread_id}, msg={message_id}"
                )
                return True

        return False

    def get_next_message(self, thread_id: int) -> Optional[QueuedMessage]:
        """
        Get the next non-deleted message from the queue

        Args:
            thread_id: Discord thread ID

        Returns:
            Next QueuedMessage or None if queue is empty
        """
        if thread_id not in self._queues:
            return None

        queue = self._queues[thread_id]

        # Skip deleted messages and remove them from queue
        while queue:
            msg = queue.popleft()
            if not msg.deleted:
                logger.info(
                    f"Dequeued message: thread={thread_id}, msg={msg.message_id}"
                )
                return msg
            else:
                logger.info(
                    f"Skipped deleted message: thread={thread_id}, msg={msg.message_id}"
                )

        return None

    def get_queue_size(self, thread_id: int) -> int:
        """
        Get the number of pending messages in the queue

        Args:
            thread_id: Discord thread ID

        Returns:
            Number of pending messages (excluding deleted)
        """
        if thread_id not in self._queues:
            return 0

        return sum(1 for msg in self._queues[thread_id] if not msg.deleted)

    def is_processing(self, thread_id: int) -> bool:
        """
        Check if a thread is currently processing a message

        Args:
            thread_id: Discord thread ID

        Returns:
            True if processing, False otherwise
        """
        return self._processing.get(thread_id, False)

    def get_lock(self, thread_id: int) -> asyncio.Lock:
        """
        Get the processing lock for a thread

        Args:
            thread_id: Discord thread ID

        Returns:
            asyncio.Lock for the thread
        """
        if thread_id not in self._locks:
            self._locks[thread_id] = asyncio.Lock()
        return self._locks[thread_id]

    def set_processing(self, thread_id: int, is_processing: bool):
        """
        Set the processing state for a thread

        Args:
            thread_id: Discord thread ID
            is_processing: Processing state
        """
        self._processing[thread_id] = is_processing
        logger.debug(f"Thread {thread_id} processing state: {is_processing}")

    def clear_thread_queue(self, thread_id: int):
        """
        Clear all messages from a thread's queue

        Args:
            thread_id: Discord thread ID
        """
        if thread_id in self._queues:
            size = len(self._queues[thread_id])
            self._queues[thread_id].clear()
            logger.info(
                f"Cleared queue for thread {thread_id}: {size} messages removed"
            )

    def get_stats(self) -> Dict[str, int]:
        """
        Get queue statistics

        Returns:
            Dictionary with statistics
        """
        total_threads = len(self._queues)
        total_messages = sum(len(q) for q in self._queues.values())
        processing_threads = sum(1 for p in self._processing.values() if p)

        return {
            "total_threads": total_threads,
            "total_queued_messages": total_messages,
            "processing_threads": processing_threads,
        }
