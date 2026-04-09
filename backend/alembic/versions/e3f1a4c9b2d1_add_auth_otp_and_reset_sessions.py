"""add_auth_otp_and_reset_sessions

Revision ID: e3f1a4c9b2d1
Revises: cae49faf5618
Create Date: 2026-04-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "e3f1a4c9b2d1"
down_revision: Union[str, Sequence[str], None] = "cae49faf5618"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    otp_purpose = postgresql.ENUM("SIGNUP_VERIFY", "PASSWORD_RESET", name="otppurpose", create_type=False)
    otp_status = postgresql.ENUM(
        "PENDING",
        "SENT",
        "VERIFIED",
        "CONSUMED",
        "EXPIRED",
        "LOCKED",
        "REVOKED",
        "FAILED_SEND",
        name="otpstatus",
        create_type=False,
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'otppurpose') THEN
                CREATE TYPE otppurpose AS ENUM ('SIGNUP_VERIFY', 'PASSWORD_RESET');
            END IF;
        END$$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'otpstatus') THEN
                CREATE TYPE otpstatus AS ENUM ('PENDING', 'SENT', 'VERIFIED', 'CONSUMED', 'EXPIRED', 'LOCKED', 'REVOKED', 'FAILED_SEND');
            END IF;
        END$$;
        """
    )

    op.add_column("users", sa.Column("email_verified_at", sa.TIMESTAMP(), nullable=True))
    op.add_column("users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))
    op.execute("UPDATE users SET token_version = 0 WHERE token_version IS NULL")
    op.alter_column("users", "token_version", server_default=None)

    op.create_table(
        "auth_otp_challenges",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("email_snapshot", sa.String(length=255), nullable=False),
        sa.Column("purpose", otp_purpose, nullable=False),
        sa.Column("status", otp_status, nullable=False),
        sa.Column("code_hash", sa.String(length=128), nullable=False),
        sa.Column("code_salt", sa.String(length=64), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("resend_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("issued_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("sent_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("verified_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("consumed_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("revoked_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("locked_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("last_attempt_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("resend_available_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("request_ip", sa.String(length=45), nullable=True),
        sa.Column("request_user_agent", sa.Text(), nullable=True),
        sa.Column("delivery_provider", sa.String(length=40), nullable=True),
        sa.Column("delivery_message_id", sa.String(length=255), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_auth_otp_challenges_user_id", "auth_otp_challenges", ["user_id"], unique=False)
    op.create_index("ix_auth_otp_challenges_email_snapshot", "auth_otp_challenges", ["email_snapshot"], unique=False)
    op.create_index("ix_auth_otp_challenges_purpose", "auth_otp_challenges", ["purpose"], unique=False)
    op.create_index("ix_auth_otp_challenges_status", "auth_otp_challenges", ["status"], unique=False)
    op.create_index("ix_auth_otp_challenges_expires_at", "auth_otp_challenges", ["expires_at"], unique=False)
    op.create_index(
        "ix_auth_otp_challenges_resend_available_at",
        "auth_otp_challenges",
        ["resend_available_at"],
        unique=False,
    )

    op.create_table(
        "password_reset_sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("otp_challenge_id", sa.UUID(), nullable=False),
        sa.Column("reset_token_hash", sa.String(length=128), nullable=False),
        sa.Column("issued_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("consumed_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("revoked_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("request_ip", sa.String(length=45), nullable=True),
        sa.Column("request_user_agent", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["otp_challenge_id"], ["auth_otp_challenges.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_password_reset_sessions_user_id", "password_reset_sessions", ["user_id"], unique=False)
    op.create_index("ix_password_reset_sessions_otp_challenge_id", "password_reset_sessions", ["otp_challenge_id"], unique=False)
    op.create_index(
        "ix_password_reset_sessions_reset_token_hash",
        "password_reset_sessions",
        ["reset_token_hash"],
        unique=True,
    )
    op.create_index("ix_password_reset_sessions_expires_at", "password_reset_sessions", ["expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_password_reset_sessions_expires_at", table_name="password_reset_sessions")
    op.drop_index("ix_password_reset_sessions_reset_token_hash", table_name="password_reset_sessions")
    op.drop_index("ix_password_reset_sessions_otp_challenge_id", table_name="password_reset_sessions")
    op.drop_index("ix_password_reset_sessions_user_id", table_name="password_reset_sessions")
    op.drop_table("password_reset_sessions")

    op.drop_index("ix_auth_otp_challenges_resend_available_at", table_name="auth_otp_challenges")
    op.drop_index("ix_auth_otp_challenges_expires_at", table_name="auth_otp_challenges")
    op.drop_index("ix_auth_otp_challenges_status", table_name="auth_otp_challenges")
    op.drop_index("ix_auth_otp_challenges_purpose", table_name="auth_otp_challenges")
    op.drop_index("ix_auth_otp_challenges_email_snapshot", table_name="auth_otp_challenges")
    op.drop_index("ix_auth_otp_challenges_user_id", table_name="auth_otp_challenges")
    op.drop_table("auth_otp_challenges")

    op.drop_column("users", "token_version")
    op.drop_column("users", "email_verified_at")

    sa.Enum(name="otpstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="otppurpose").drop(op.get_bind(), checkfirst=True)
