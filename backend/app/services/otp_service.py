"""OTP challenge lifecycle service for signup verification and password reset."""
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.database_models import OtpChallenge, OtpPurpose, OtpStatus, PasswordResetSession, User
from app.services.email_service import EmailService
from app.utils.security import SecurityUtils


ACTIVE_STATUSES = [OtpStatus.PENDING, OtpStatus.SENT]


class OTPService:
    """Encapsulates OTP issue, verify, resend and reset token lifecycle logic."""

    @staticmethod
    def issue_signup_otp(db: Session, user: User, request_ip: Optional[str], user_agent: Optional[str]) -> dict:
        return OTPService._issue_otp(
            db=db,
            user=user,
            purpose=OtpPurpose.SIGNUP_VERIFY,
            request_ip=request_ip,
            user_agent=user_agent,
        )

    @staticmethod
    def issue_password_reset_otp(db: Session, user: User, request_ip: Optional[str], user_agent: Optional[str]) -> dict:
        return OTPService._issue_otp(
            db=db,
            user=user,
            purpose=OtpPurpose.PASSWORD_RESET,
            request_ip=request_ip,
            user_agent=user_agent,
        )

    @staticmethod
    def _issue_otp(db: Session, user: User, purpose: OtpPurpose, request_ip: Optional[str], user_agent: Optional[str]) -> dict:
        now = datetime.utcnow()
        active = OTPService._get_active_challenge(db=db, user_id=user.id, purpose=purpose)

        if active and active.resend_available_at and now < active.resend_available_at:
            return {
                "success": False,
                "error": "cooldown_active",
                "retry_after_seconds": int((active.resend_available_at - now).total_seconds()),
            }

        if active:
            active.status = OtpStatus.REVOKED
            active.revoked_at = now

        code = SecurityUtils.generate_otp_code()
        salt = SecurityUtils.generate_salt(16)
        expires_at = now + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        resend_available_at = now + timedelta(seconds=settings.OTP_RESEND_COOLDOWN_SECONDS)

        challenge = OtpChallenge(
            user_id=user.id,
            email_snapshot=user.email,
            purpose=purpose,
            status=OtpStatus.PENDING,
            code_hash=SecurityUtils.hash_otp(code, salt),
            code_salt=salt,
            attempt_count=0,
            max_attempts=settings.OTP_MAX_ATTEMPTS,
            resend_count=(active.resend_count + 1) if active else 0,
            issued_at=now,
            expires_at=expires_at,
            resend_available_at=resend_available_at,
            request_ip=request_ip,
            request_user_agent=user_agent,
        )

        db.add(challenge)
        db.flush()

        delivery_result = (
            EmailService.send_signup_otp(user.email, code, settings.OTP_EXPIRE_MINUTES)
            if purpose == OtpPurpose.SIGNUP_VERIFY
            else EmailService.send_password_reset_otp(user.email, code, settings.OTP_EXPIRE_MINUTES)
        )

        challenge.sent_at = datetime.utcnow()
        challenge.delivery_provider = delivery_result.provider
        challenge.delivery_message_id = delivery_result.message_id
        challenge.status = OtpStatus.SENT if delivery_result.success else OtpStatus.FAILED_SEND

        db.commit()

        response = {
            "success": delivery_result.success,
            "challenge_id": str(challenge.id),
            "expires_in_seconds": settings.OTP_EXPIRE_MINUTES * 60,
            "cooldown_seconds": settings.OTP_RESEND_COOLDOWN_SECONDS,
            "attempts_remaining": max(challenge.max_attempts - challenge.attempt_count, 0),
        }
        if not delivery_result.success:
            response["error"] = "delivery_failed"
        return response

    @staticmethod
    def verify_otp(db: Session, user: User, purpose: OtpPurpose, otp: str, request_ip: Optional[str], user_agent: Optional[str]) -> dict:
        challenge = OTPService._get_active_challenge(db=db, user_id=user.id, purpose=purpose)
        now = datetime.utcnow()

        if not challenge:
            return {"success": False, "error": "challenge_not_found"}

        if challenge.expires_at <= now:
            challenge.status = OtpStatus.EXPIRED
            db.commit()
            return {"success": False, "error": "otp_expired"}

        if challenge.attempt_count >= challenge.max_attempts:
            challenge.status = OtpStatus.LOCKED
            challenge.locked_at = now
            db.commit()
            return {"success": False, "error": "otp_locked"}

        challenge.attempt_count += 1
        challenge.last_attempt_at = now

        if not SecurityUtils.verify_otp(otp, challenge.code_salt, challenge.code_hash):
            if challenge.attempt_count >= challenge.max_attempts:
                challenge.status = OtpStatus.LOCKED
                challenge.locked_at = now
            db.commit()
            return {
                "success": False,
                "error": "otp_invalid",
                "attempts_remaining": max(challenge.max_attempts - challenge.attempt_count, 0),
            }

        challenge.status = OtpStatus.CONSUMED
        challenge.verified_at = now
        challenge.consumed_at = now
        challenge.request_ip = request_ip or challenge.request_ip
        challenge.request_user_agent = user_agent or challenge.request_user_agent

        result = {
            "success": True,
            "attempts_remaining": max(challenge.max_attempts - challenge.attempt_count, 0),
            "challenge_id": str(challenge.id),
        }

        if purpose == OtpPurpose.PASSWORD_RESET:
            reset_token = SecurityUtils.generate_reset_token()
            reset_session = PasswordResetSession(
                user_id=user.id,
                otp_challenge_id=challenge.id,
                reset_token_hash=SecurityUtils.hash_reset_token(reset_token),
                issued_at=now,
                expires_at=now + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
                request_ip=request_ip,
                request_user_agent=user_agent,
            )
            db.add(reset_session)
            result["reset_token"] = reset_token
            result["reset_expires_in_seconds"] = settings.OTP_EXPIRE_MINUTES * 60

        db.commit()
        return result

    @staticmethod
    def complete_password_reset(db: Session, reset_token: str, new_password: str) -> dict:
        token_hash = SecurityUtils.hash_reset_token(reset_token)
        session = (
            db.query(PasswordResetSession)
            .filter(
                PasswordResetSession.reset_token_hash == token_hash,
                PasswordResetSession.consumed_at == None,
                PasswordResetSession.revoked_at == None,
            )
            .first()
        )

        if not session:
            return {"success": False, "error": "reset_session_not_found"}

        if session.expires_at <= datetime.utcnow():
            return {"success": False, "error": "reset_session_expired"}

        user = db.query(User).filter(User.id == session.user_id, User.deleted_at == None).first()
        if not user:
            return {"success": False, "error": "user_not_found"}

        user.set_password(new_password)
        user.token_version = (user.token_version or 0) + 1
        session.consumed_at = datetime.utcnow()

        db.query(PasswordResetSession).filter(
            PasswordResetSession.user_id == user.id,
            PasswordResetSession.consumed_at == None,
            PasswordResetSession.id != session.id,
        ).update({PasswordResetSession.revoked_at: datetime.utcnow()}, synchronize_session=False)

        db.query(OtpChallenge).filter(
            OtpChallenge.user_id == user.id,
            OtpChallenge.status.in_(ACTIVE_STATUSES),
        ).update(
            {
                OtpChallenge.status: OtpStatus.REVOKED,
                OtpChallenge.revoked_at: datetime.utcnow(),
            },
            synchronize_session=False,
        )

        db.commit()
        return {"success": True, "user_id": str(user.id)}

    @staticmethod
    def _get_active_challenge(db: Session, user_id, purpose: OtpPurpose) -> Optional[OtpChallenge]:
        return (
            db.query(OtpChallenge)
            .filter(
                OtpChallenge.user_id == user_id,
                OtpChallenge.purpose == purpose,
                OtpChallenge.status.in_(ACTIVE_STATUSES),
            )
            .order_by(OtpChallenge.issued_at.desc())
            .first()
        )
