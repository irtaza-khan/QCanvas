"""merge folders head

Revision ID: 96b49ea20d2a
Revises: 4e5782bb92d6, 9b3a7a1f0d2c
Create Date: 2026-03-31 16:47:28.971138

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96b49ea20d2a'
down_revision: Union[str, Sequence[str], None] = ('4e5782bb92d6', '9b3a7a1f0d2c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
