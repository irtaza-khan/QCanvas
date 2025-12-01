"""Add DEMO role to enum

Revision ID: 330e27ffebcd
Revises: 83149d586e8a
Create Date: 2025-12-02 01:19:47.864437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '330e27ffebcd'
down_revision: Union[str, Sequence[str], None] = '83149d586e8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
