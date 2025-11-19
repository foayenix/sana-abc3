"""SendGrid email service."""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType
from typing import Optional, List
import base64
from app.core.config import settings


class EmailService:
    """Service for sending emails via SendGrid."""

    def __init__(self):
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        self.from_email = settings.FROM_EMAIL or "noreply@sana.health"
        self.from_name = "SANA Health"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[dict]] = None,
    ) -> bool:
        """Send a single email."""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content),
            )

            if text_content:
                message.add_content(Content("text/plain", text_content))

            if attachments:
                for att in attachments:
                    attachment = Attachment(
                        FileContent(base64.b64encode(att['content']).decode()),
                        FileName(att['filename']),
                        FileType(att.get('type', 'application/octet-stream')),
                    )
                    message.add_attachment(attachment)

            self.client.send(message)
            return True
        except Exception as e:
            print(f"Email send failed: {e}")
            return False

    async def send_template_email(
        self,
        to_email: str,
        template_id: str,
        dynamic_data: dict,
    ) -> bool:
        """Send email using SendGrid dynamic template."""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
            )
            message.template_id = template_id
            message.dynamic_template_data = dynamic_data

            self.client.send(message)
            return True
        except Exception as e:
            print(f"Template email send failed: {e}")
            return False

    # Pre-built email methods
    async def send_verification_email(self, to_email: str, token: str, name: str) -> bool:
        """Send email verification."""
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        html = f"""
        <h2>Welcome to SANA Health, {name}!</h2>
        <p>Please verify your email address by clicking the link below:</p>
        <a href="{verification_url}" style="background-color: #345519; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Verify Email</a>
        <p>This link will expire in 24 hours.</p>
        """
        return await self.send_email(to_email, "Verify Your Email - SANA Health", html)

    async def send_password_reset(self, to_email: str, token: str, name: str) -> bool:
        """Send password reset email."""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        html = f"""
        <h2>Password Reset Request</h2>
        <p>Hi {name},</p>
        <p>You requested to reset your password. Click the link below:</p>
        <a href="{reset_url}" style="background-color: #345519; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Reset Password</a>
        <p>This link will expire in 1 hour. If you didn't request this, please ignore this email.</p>
        """
        return await self.send_email(to_email, "Reset Your Password - SANA Health", html)

    async def send_booking_confirmation(
        self,
        to_email: str,
        client_name: str,
        practitioner_name: str,
        service_name: str,
        date_time: str,
        price: str,
    ) -> bool:
        """Send booking confirmation to client."""
        html = f"""
        <h2>Booking Confirmed!</h2>
        <p>Hi {client_name},</p>
        <p>Your session has been booked successfully.</p>
        <div style="background-color: #f5f5f5; padding: 16px; border-radius: 8px;">
            <p><strong>Practitioner:</strong> {practitioner_name}</p>
            <p><strong>Service:</strong> {service_name}</p>
            <p><strong>Date & Time:</strong> {date_time}</p>
            <p><strong>Price:</strong> {price}</p>
        </div>
        <p>We'll send you a reminder before your session.</p>
        """
        return await self.send_email(to_email, "Booking Confirmed - SANA Health", html)

    async def send_new_booking_notification(
        self,
        to_email: str,
        practitioner_name: str,
        client_name: str,
        service_name: str,
        date_time: str,
    ) -> bool:
        """Send new booking notification to practitioner."""
        html = f"""
        <h2>New Booking!</h2>
        <p>Hi {practitioner_name},</p>
        <p>You have a new booking.</p>
        <div style="background-color: #f5f5f5; padding: 16px; border-radius: 8px;">
            <p><strong>Client:</strong> {client_name}</p>
            <p><strong>Service:</strong> {service_name}</p>
            <p><strong>Date & Time:</strong> {date_time}</p>
        </div>
        """
        return await self.send_email(to_email, "New Booking - SANA Health", html)

    async def send_session_reminder(
        self,
        to_email: str,
        name: str,
        other_party: str,
        date_time: str,
        meeting_link: Optional[str] = None,
    ) -> bool:
        """Send session reminder."""
        link_html = f'<p><a href="{meeting_link}">Join Session</a></p>' if meeting_link else ''
        html = f"""
        <h2>Session Reminder</h2>
        <p>Hi {name},</p>
        <p>Your session with {other_party} is coming up.</p>
        <p><strong>Date & Time:</strong> {date_time}</p>
        {link_html}
        """
        return await self.send_email(to_email, "Session Reminder - SANA Health", html)


email_service = EmailService()
