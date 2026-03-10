"""merge_heads_2

Revision ID: 4e5782bb92d6
Revises: 4ada97e0e3b4, cae49faf5618
Create Date: 2026-03-10 15:43:09.825011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e5782bb92d6'
down_revision: Union[str, Sequence[str], None] = ('4ada97e0e3b4', 'cae49faf5618')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
