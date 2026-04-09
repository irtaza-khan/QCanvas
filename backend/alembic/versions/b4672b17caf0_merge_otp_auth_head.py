"""merge otp auth head

Revision ID: b4672b17caf0
Revises: 96b49ea20d2a, e3f1a4c9b2d1
Create Date: 2026-04-09 22:27:11.166374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4672b17caf0'
down_revision: Union[str, Sequence[str], None] = ('96b49ea20d2a', 'e3f1a4c9b2d1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
