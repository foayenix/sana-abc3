"""WebSocket service for real-time messaging."""

import json
from typing import Dict, Set
from fastapi import WebSocket
import redis.asyncio as redis
from app.core.config import settings


class ConnectionManager:
    """Manages WebSocket connections for real-time messaging."""

    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.redis_client = None

    async def connect_redis(self):
        """Initialize Redis connection for pub/sub."""
        if not self.redis_client:
            self.redis_client = redis.from_url(settings.REDIS_URL)

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept WebSocket connection and register user."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user's connections."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

    async def broadcast_to_conversation(
        self, message: dict, participant_ids: list[int]
    ):
        """Broadcast message to all participants in a conversation."""
        for user_id in participant_ids:
            await self.send_personal_message(message, user_id)

    async def publish_message(self, channel: str, message: dict):
        """Publish message to Redis channel for distributed systems."""
        if self.redis_client:
            await self.redis_client.publish(channel, json.dumps(message))

    async def subscribe_to_user(self, user_id: int):
        """Subscribe to user's message channel."""
        if self.redis_client:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(f"user:{user_id}")
            return pubsub
        return None


manager = ConnectionManager()


# WebSocket endpoint handler
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """Handle WebSocket connection for user."""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()

            # Handle different message types
            msg_type = data.get("type")

            if msg_type == "message":
                # New chat message
                await manager.broadcast_to_conversation(
                    {
                        "type": "message",
                        "data": data.get("data"),
                        "sender_id": user_id,
                    },
                    data.get("participant_ids", []),
                )

            elif msg_type == "typing":
                # Typing indicator
                await manager.broadcast_to_conversation(
                    {
                        "type": "typing",
                        "user_id": user_id,
                        "conversation_id": data.get("conversation_id"),
                    },
                    data.get("participant_ids", []),
                )

            elif msg_type == "read":
                # Mark messages as read
                await manager.send_personal_message(
                    {
                        "type": "read",
                        "conversation_id": data.get("conversation_id"),
                        "reader_id": user_id,
                    },
                    data.get("recipient_id"),
                )

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except Exception:
        pass
    finally:
        manager.disconnect(websocket, user_id)
