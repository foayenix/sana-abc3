"""Firebase service for push notifications."""

import firebase_admin
from firebase_admin import credentials, messaging
from typing import Optional, List
from app.core.config import settings


class FirebaseService:
    """Service for handling Firebase push notifications."""

    def __init__(self):
        self._initialized = False

    def initialize(self):
        """Initialize Firebase Admin SDK."""
        if not self._initialized and settings.FIREBASE_CREDENTIALS:
            try:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
                firebase_admin.initialize_app(cred)
                self._initialized = True
            except Exception as e:
                print(f"Firebase initialization failed: {e}")

    async def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        image_url: Optional[str] = None,
    ) -> bool:
        """Send push notification to a single device."""
        if not self._initialized:
            return False

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url,
                ),
                data=data or {},
                token=token,
            )
            messaging.send(message)
            return True
        except Exception as e:
            print(f"Failed to send notification: {e}")
            return False

    async def send_multicast(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[dict] = None,
    ) -> dict:
        """Send push notification to multiple devices."""
        if not self._initialized:
            return {"success": 0, "failure": len(tokens)}

        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=tokens,
            )
            response = messaging.send_multicast(message)
            return {
                "success": response.success_count,
                "failure": response.failure_count,
            }
        except Exception as e:
            print(f"Failed to send multicast: {e}")
            return {"success": 0, "failure": len(tokens)}

    async def send_topic_notification(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
    ) -> bool:
        """Send notification to all subscribers of a topic."""
        if not self._initialized:
            return False

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                topic=topic,
            )
            messaging.send(message)
            return True
        except Exception as e:
            print(f"Failed to send topic notification: {e}")
            return False

    async def subscribe_to_topic(self, tokens: List[str], topic: str) -> bool:
        """Subscribe devices to a topic."""
        if not self._initialized:
            return False

        try:
            messaging.subscribe_to_topic(tokens, topic)
            return True
        except Exception:
            return False

    async def unsubscribe_from_topic(self, tokens: List[str], topic: str) -> bool:
        """Unsubscribe devices from a topic."""
        if not self._initialized:
            return False

        try:
            messaging.unsubscribe_from_topic(tokens, topic)
            return True
        except Exception:
            return False


# Notification templates
class NotificationTemplates:
    """Pre-defined notification templates."""

    @staticmethod
    def session_reminder(practitioner_name: str, time: str) -> dict:
        return {
            "title": "Session Reminder",
            "body": f"Your session with {practitioner_name} is in {time}",
        }

    @staticmethod
    def session_booked(client_name: str, time: str) -> dict:
        return {
            "title": "New Booking",
            "body": f"{client_name} booked a session for {time}",
        }

    @staticmethod
    def session_cancelled(name: str) -> dict:
        return {
            "title": "Session Cancelled",
            "body": f"Your session with {name} has been cancelled",
        }

    @staticmethod
    def new_message(sender_name: str) -> dict:
        return {
            "title": "New Message",
            "body": f"You have a new message from {sender_name}",
        }

    @staticmethod
    def payment_received(amount: str) -> dict:
        return {
            "title": "Payment Received",
            "body": f"You received a payment of {amount}",
        }

    @staticmethod
    def verification_approved() -> dict:
        return {
            "title": "Verification Approved",
            "body": "Congratulations! Your practitioner profile has been verified.",
        }


firebase_service = FirebaseService()
