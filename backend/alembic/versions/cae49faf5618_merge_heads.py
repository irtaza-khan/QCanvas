"""merge_heads

Revision ID: cae49faf5618
Revises: 82f94e6c24fb, b2c3d4e5f6a7
Create Date: 2026-03-10 15:11:52.418332

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cae49faf5618'
down_revision: Union[str, Sequence[str], None] = ('82f94e6c24fb', 'b2c3d4e5f6a7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
