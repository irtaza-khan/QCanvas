"""Decouple files from projects

Revision ID: 6f7e8d9c0b1a
Revises: 4a1b2c3d4e5f
Create Date: 2026-01-23 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6f7e8d9c0b1a'
down_revision: Union[str, Sequence[str], None] = '4a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user_id to files
    op.add_column('files', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Backfill files.user_id using the owning project
    op.execute("UPDATE files SET user_id = projects.user_id FROM projects WHERE files.project_id = projects.id")
    
    # Enforce files.user_id NOT NULL after backfill
    op.alter_column('files', 'user_id', nullable=False)
    
    # Create a named foreign key constraint
    op.create_foreign_key(
        'fk_files_user_id_users', 'files', 'users', ['user_id'], ['id'], ondelete='CASCADE'
    )

    # Add is_shared to files
    op.add_column(
        'files', 
        sa.Column('is_shared', sa.Boolean(), server_default='false', nullable=False)
    )

    # Make project_id nullable
    op.alter_column('files', 'project_id',
               existing_type=sa.INTEGER(),
               nullable=True)


def downgrade() -> None:
    # Delete orphaned files where project_id IS NULL
    op.execute("DELETE FROM files WHERE project_id IS NULL")

    # Restore project_id NOT NULL
    op.alter_column('files', 'project_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # Drop is_shared
    op.drop_column('files', 'is_shared')

    # Drop the named foreign key
    op.drop_constraint('fk_files_user_id_users', 'files', type_='foreignkey')

    # Drop user_id
    op.drop_column('files', 'user_id')
