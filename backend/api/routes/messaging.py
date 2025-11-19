"""
Messaging API routes for SANA Platform.

Endpoints for in-app messaging between clients and practitioners.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.messaging.chat import MessagingService, MessageType

router = APIRouter()

# Initialize service
messaging_service = MessagingService()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class StartConversationRequest(BaseModel):
    """Start or get a conversation."""
    participant_ids: List[UUID]
    booking_id: Optional[UUID] = None


class SendMessageRequest(BaseModel):
    """Send a message."""
    sender_id: UUID
    content: str
    message_type: str = "text"
    attachment_url: Optional[str] = None
    attachment_name: Optional[str] = None


class EditMessageRequest(BaseModel):
    """Edit a message."""
    new_content: str


# ============================================================================
# CONVERSATION ENDPOINTS
# ============================================================================

@router.post("/conversations")
async def start_conversation(request: StartConversationRequest):
    """Start a new conversation or get existing one."""
    conversation = messaging_service.get_or_create_conversation(
        request.participant_ids,
        request.booking_id
    )

    return {
        "id": str(conversation.id),
        "participant_ids": [str(p) for p in conversation.participant_ids],
        "booking_id": str(conversation.booking_id) if conversation.booking_id else None,
        "status": conversation.status.value,
        "created_at": conversation.created_at.isoformat()
    }


@router.get("/conversations/{user_id}")
async def get_user_conversations(user_id: UUID, include_archived: bool = False):
    """Get all conversations for a user."""
    conversations = messaging_service.get_user_conversations(
        user_id,
        include_archived
    )

    return {
        "count": len(conversations),
        "conversations": [
            {
                "id": str(c["conversation"].id),
                "other_participant_ids": [str(p) for p in c["other_participant_ids"]],
                "last_message": c["conversation"].last_message_preview,
                "last_message_at": c["conversation"].last_message_at.isoformat() if c["conversation"].last_message_at else None,
                "unread_count": c["unread_count"],
                "status": c["conversation"].status.value
            }
            for c in conversations
        ]
    }


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: UUID,
    user_id: UUID,
    before: Optional[datetime] = None,
    limit: int = 50
):
    """Get messages in a conversation."""
    try:
        messages = messaging_service.get_conversation_messages(
            conversation_id,
            user_id,
            before,
            limit
        )

        return {
            "count": len(messages),
            "messages": [
                {
                    "id": str(m.id),
                    "sender_id": str(m.sender_id),
                    "message_type": m.message_type.value,
                    "content": m.content,
                    "attachment_url": m.attachment_url,
                    "attachment_name": m.attachment_name,
                    "is_read": m.is_read,
                    "created_at": m.created_at.isoformat(),
                    "edited_at": m.edited_at.isoformat() if m.edited_at else None
                }
                for m in messages
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/conversations/{conversation_id}/archive")
async def archive_conversation(conversation_id: UUID, user_id: UUID):
    """Archive a conversation."""
    success = messaging_service.archive_conversation(conversation_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation archived"}


# ============================================================================
# MESSAGE ENDPOINTS
# ============================================================================

@router.post("/conversations/{conversation_id}/messages")
async def send_message(conversation_id: UUID, request: SendMessageRequest):
    """Send a message in a conversation."""
    try:
        message_type = MessageType(request.message_type)
    except ValueError:
        message_type = MessageType.TEXT

    try:
        message = messaging_service.send_message(
            conversation_id=conversation_id,
            sender_id=request.sender_id,
            content=request.content,
            message_type=message_type,
            attachment_url=request.attachment_url,
            attachment_name=request.attachment_name
        )

        return {
            "id": str(message.id),
            "conversation_id": str(message.conversation_id),
            "sender_id": str(message.sender_id),
            "content": message.content,
            "message_type": message.message_type.value,
            "created_at": message.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/conversations/{conversation_id}/read")
async def mark_as_read(conversation_id: UUID, user_id: UUID):
    """Mark all messages in conversation as read."""
    try:
        count = messaging_service.mark_as_read(conversation_id, user_id)
        return {"messages_marked": count}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/messages/{message_id}")
async def edit_message(message_id: UUID, user_id: UUID, request: EditMessageRequest):
    """Edit a message."""
    message = messaging_service.edit_message(
        message_id,
        user_id,
        request.new_content
    )

    if not message:
        raise HTTPException(status_code=404, detail="Message not found or not authorized")

    return {
        "id": str(message.id),
        "content": message.content,
        "edited_at": message.edited_at.isoformat()
    }


@router.delete("/messages/{message_id}")
async def delete_message(message_id: UUID, user_id: UUID):
    """Delete a message."""
    success = messaging_service.delete_message(message_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Message not found or not authorized")

    return {"message": "Message deleted"}


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/unread/{user_id}")
async def get_unread_count(user_id: UUID):
    """Get total unread message count for user."""
    count = messaging_service.get_unread_count(user_id)
    return {"unread_count": count}


@router.get("/search/{user_id}")
async def search_messages(user_id: UUID, query: str, limit: int = 20):
    """Search messages across user's conversations."""
    messages = messaging_service.search_messages(user_id, query, limit)

    return {
        "count": len(messages),
        "messages": [
            {
                "id": str(m.id),
                "conversation_id": str(m.conversation_id),
                "content": m.content,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]
    }


# ============================================================================
# TEST ENDPOINTS
# ============================================================================

@router.get("/test-setup")
async def test_messaging():
    """Set up test data for messaging."""
    from uuid import uuid4

    # Create test users
    client_id = uuid4()
    practitioner_id = uuid4()

    # Create conversation
    conversation = messaging_service.get_or_create_conversation(
        [client_id, practitioner_id]
    )

    # Send some messages
    msg1 = messaging_service.send_message(
        conversation.id,
        client_id,
        "Hi, I'd like to book an appointment for next week."
    )

    msg2 = messaging_service.send_message(
        conversation.id,
        practitioner_id,
        "Hello! I have availability on Tuesday at 2pm and Thursday at 10am. Which works better for you?"
    )

    msg3 = messaging_service.send_message(
        conversation.id,
        client_id,
        "Tuesday at 2pm would be perfect!"
    )

    return {
        "client_id": str(client_id),
        "practitioner_id": str(practitioner_id),
        "conversation_id": str(conversation.id),
        "messages_sent": 3,
        "message": "Test conversation created"
    }
