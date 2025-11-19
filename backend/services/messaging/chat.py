"""
Chat messaging service for client-practitioner communication.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of messages."""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"


class ConversationStatus(str, Enum):
    """Conversation status."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    BLOCKED = "blocked"


class Message(BaseModel):
    """A chat message."""
    id: UUID
    conversation_id: UUID
    sender_id: UUID

    # Content
    message_type: MessageType = MessageType.TEXT
    content: str
    attachment_url: Optional[str] = None
    attachment_name: Optional[str] = None

    # Status
    is_read: bool = False
    read_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime
    edited_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class Conversation(BaseModel):
    """A conversation between two users."""
    id: UUID
    participant_ids: List[UUID]

    # Context
    booking_id: Optional[UUID] = None

    # Status
    status: ConversationStatus = ConversationStatus.ACTIVE

    # Metadata
    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None

    # Unread counts per participant
    unread_counts: Dict[str, int] = {}

    created_at: datetime
    updated_at: datetime


class MessagingService:
    """
    Handles in-app messaging between users.

    Features:
    - Text and file messages
    - Read receipts
    - Conversation management
    - Notifications
    """

    def __init__(self):
        self.messages: Dict[UUID, Message] = {}
        self.conversations: Dict[UUID, Conversation] = {}
        logger.info("MessagingService initialized")

    def get_or_create_conversation(
        self,
        participant_ids: List[UUID],
        booking_id: Optional[UUID] = None
    ) -> Conversation:
        """
        Get existing conversation or create new one.

        Args:
            participant_ids: List of participant user IDs
            booking_id: Optional booking context

        Returns:
            Conversation
        """
        # Sort IDs for consistent lookup
        sorted_ids = sorted(str(p) for p in participant_ids)

        # Look for existing conversation
        for conv in self.conversations.values():
            conv_ids = sorted(str(p) for p in conv.participant_ids)
            if conv_ids == sorted_ids and conv.status == ConversationStatus.ACTIVE:
                return conv

        # Create new conversation
        now = datetime.utcnow()
        conversation = Conversation(
            id=uuid4(),
            participant_ids=participant_ids,
            booking_id=booking_id,
            unread_counts={str(p): 0 for p in participant_ids},
            created_at=now,
            updated_at=now
        )

        self.conversations[conversation.id] = conversation

        logger.info(f"Created conversation {conversation.id}")

        return conversation

    def send_message(
        self,
        conversation_id: UUID,
        sender_id: UUID,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        attachment_url: Optional[str] = None,
        attachment_name: Optional[str] = None
    ) -> Message:
        """
        Send a message in a conversation.

        Args:
            conversation_id: Conversation ID
            sender_id: Sender user ID
            content: Message content
            message_type: Type of message
            attachment_url: Optional attachment URL
            attachment_name: Optional attachment name

        Returns:
            Created message
        """
        if conversation_id not in self.conversations:
            raise ValueError("Conversation not found")

        conversation = self.conversations[conversation_id]

        # Verify sender is participant
        if sender_id not in conversation.participant_ids:
            raise ValueError("User is not a participant in this conversation")

        now = datetime.utcnow()

        message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            sender_id=sender_id,
            message_type=message_type,
            content=content,
            attachment_url=attachment_url,
            attachment_name=attachment_name,
            created_at=now
        )

        self.messages[message.id] = message

        # Update conversation
        conversation.last_message_at = now
        conversation.last_message_preview = content[:50] + "..." if len(content) > 50 else content
        conversation.updated_at = now

        # Increment unread counts for other participants
        for participant_id in conversation.participant_ids:
            if participant_id != sender_id:
                key = str(participant_id)
                conversation.unread_counts[key] = conversation.unread_counts.get(key, 0) + 1

        logger.info(f"Message {message.id} sent in conversation {conversation_id}")

        return message

    def get_conversation_messages(
        self,
        conversation_id: UUID,
        user_id: UUID,
        before: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Message]:
        """
        Get messages in a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: Requesting user ID
            before: Get messages before this time
            limit: Max messages to return

        Returns:
            List of messages
        """
        if conversation_id not in self.conversations:
            raise ValueError("Conversation not found")

        conversation = self.conversations[conversation_id]

        # Verify access
        if user_id not in conversation.participant_ids:
            raise ValueError("User is not a participant")

        # Get messages
        messages = [
            m for m in self.messages.values()
            if m.conversation_id == conversation_id
            and m.deleted_at is None
        ]

        if before:
            messages = [m for m in messages if m.created_at < before]

        # Sort by time (newest first)
        messages.sort(key=lambda x: x.created_at, reverse=True)

        return messages[:limit]

    def mark_as_read(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> int:
        """
        Mark all messages in conversation as read.

        Returns number of messages marked.
        """
        if conversation_id not in self.conversations:
            raise ValueError("Conversation not found")

        conversation = self.conversations[conversation_id]

        if user_id not in conversation.participant_ids:
            raise ValueError("User is not a participant")

        now = datetime.utcnow()
        marked = 0

        for message in self.messages.values():
            if (message.conversation_id == conversation_id
                and message.sender_id != user_id
                and not message.is_read):
                message.is_read = True
                message.read_at = now
                marked += 1

        # Reset unread count
        conversation.unread_counts[str(user_id)] = 0

        return marked

    def get_user_conversations(
        self,
        user_id: UUID,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user.

        Returns conversations with other participant info.
        """
        conversations = [
            conv for conv in self.conversations.values()
            if user_id in conv.participant_ids
            and (include_archived or conv.status == ConversationStatus.ACTIVE)
        ]

        # Sort by last message
        conversations.sort(
            key=lambda x: x.last_message_at or x.created_at,
            reverse=True
        )

        result = []
        for conv in conversations:
            # Get other participant
            other_ids = [p for p in conv.participant_ids if p != user_id]

            result.append({
                "conversation": conv,
                "other_participant_ids": other_ids,
                "unread_count": conv.unread_counts.get(str(user_id), 0)
            })

        return result

    def get_unread_count(self, user_id: UUID) -> int:
        """Get total unread message count for a user."""
        total = 0

        for conv in self.conversations.values():
            if user_id in conv.participant_ids:
                total += conv.unread_counts.get(str(user_id), 0)

        return total

    def archive_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID
    ) -> bool:
        """Archive a conversation for a user."""
        if conversation_id not in self.conversations:
            return False

        conversation = self.conversations[conversation_id]

        if user_id not in conversation.participant_ids:
            return False

        conversation.status = ConversationStatus.ARCHIVED
        conversation.updated_at = datetime.utcnow()

        return True

    def delete_message(
        self,
        message_id: UUID,
        user_id: UUID
    ) -> bool:
        """Soft delete a message (only sender can delete)."""
        if message_id not in self.messages:
            return False

        message = self.messages[message_id]

        if message.sender_id != user_id:
            return False

        message.deleted_at = datetime.utcnow()
        message.content = "[Message deleted]"

        return True

    def edit_message(
        self,
        message_id: UUID,
        user_id: UUID,
        new_content: str
    ) -> Optional[Message]:
        """Edit a message (only sender can edit)."""
        if message_id not in self.messages:
            return None

        message = self.messages[message_id]

        if message.sender_id != user_id:
            return None

        message.content = new_content
        message.edited_at = datetime.utcnow()

        return message

    def send_system_message(
        self,
        conversation_id: UUID,
        content: str
    ) -> Message:
        """Send a system message (e.g., booking confirmed)."""
        system_id = UUID('00000000-0000-0000-0000-000000000000')

        message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            sender_id=system_id,
            message_type=MessageType.SYSTEM,
            content=content,
            created_at=datetime.utcnow()
        )

        self.messages[message.id] = message

        # Update conversation
        if conversation_id in self.conversations:
            conv = self.conversations[conversation_id]
            conv.last_message_at = message.created_at
            conv.last_message_preview = content[:50]

        return message

    def search_messages(
        self,
        user_id: UUID,
        query: str,
        limit: int = 20
    ) -> List[Message]:
        """Search messages across all user's conversations."""
        # Get user's conversations
        user_convs = {
            conv.id for conv in self.conversations.values()
            if user_id in conv.participant_ids
        }

        # Search messages
        query_lower = query.lower()
        results = [
            m for m in self.messages.values()
            if m.conversation_id in user_convs
            and query_lower in m.content.lower()
            and m.deleted_at is None
        ]

        # Sort by relevance (exact match first, then by date)
        results.sort(key=lambda x: x.created_at, reverse=True)

        return results[:limit]
