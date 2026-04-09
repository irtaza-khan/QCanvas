"""Email delivery helpers for authentication OTP flows."""
from dataclasses import dataclass
from typing import Optional
import httpx

from app.config.settings import settings


@dataclass
class EmailSendResult:
    success: bool
    provider: str
    message_id: Optional[str] = None
    error: Optional[str] = None


class EmailService:
    """Minimal provider wrapper for transactional OTP emails."""

    @staticmethod
    def _sender() -> str:
        return f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_ADDRESS}>"

    @staticmethod
    def send_signup_otp(email: str, otp: str, expires_minutes: int) -> EmailSendResult:
        subject = "Verify your QCanvas account"
        html = (
            "<p>Your QCanvas verification code is:</p>"
            f"<h2 style='letter-spacing:4px'>{otp}</h2>"
            f"<p>This code expires in {expires_minutes} minutes.</p>"
            "<p>If you did not create this account, you can ignore this email.</p>"
        )
        return EmailService._send_email(email=email, subject=subject, html=html)

    @staticmethod
    def send_password_reset_otp(email: str, otp: str, expires_minutes: int) -> EmailSendResult:
        subject = "Your QCanvas password reset code"
        html = (
            "<p>You requested a password reset for your QCanvas account.</p>"
            f"<h2 style='letter-spacing:4px'>{otp}</h2>"
            f"<p>This code expires in {expires_minutes} minutes.</p>"
            "<p>If you did not request this reset, ignore this email.</p>"
        )
        return EmailService._send_email(email=email, subject=subject, html=html)

    @staticmethod
    def _send_email(email: str, subject: str, html: str) -> EmailSendResult:
        provider = settings.EMAIL_PROVIDER.lower()

        if provider == "resend":
            return EmailService._send_via_resend(email=email, subject=subject, html=html)

        return EmailSendResult(success=False, provider=provider, error=f"Unsupported email provider: {provider}")

    @staticmethod
    def _send_via_resend(email: str, subject: str, html: str) -> EmailSendResult:
        if not settings.RESEND_API_KEY:
            # Keep local development friction low if key is not configured yet.
            print(f"[EmailService] RESEND_API_KEY missing, skipping delivery to {email}")
            return EmailSendResult(success=True, provider="resend", message_id="dev-noop")

        payload = {
            "from": EmailService._sender(),
            "to": [email],
            "subject": subject,
            "html": html,
        }
        headers = {
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(f"{settings.RESEND_API_BASE_URL}/emails", json=payload, headers=headers)

            if response.status_code >= 400:
                return EmailSendResult(
                    success=False,
                    provider="resend",
                    error=f"Resend returned {response.status_code}: {response.text}",
                )

            data = response.json()
            return EmailSendResult(
                success=True,
                provider="resend",
                message_id=data.get("id"),
            )
        except Exception as exc:
            return EmailSendResult(success=False, provider="resend", error=str(exc))
