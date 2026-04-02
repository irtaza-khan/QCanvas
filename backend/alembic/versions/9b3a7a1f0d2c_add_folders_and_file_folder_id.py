"""Add folders and file.folder_id

Revision ID: 9b3a7a1f0d2c
Revises: cae49faf5618
Create Date: 2026-03-31 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "9b3a7a1f0d2c"
down_revision: Union[str, Sequence[str], None] = "cae49faf5618"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "folders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["folders.id"]),
    )

    op.create_index("ix_folders_user_id", "folders", ["user_id"])
    op.create_index("ix_folders_project_id", "folders", ["project_id"])
    op.create_index("ix_folders_parent_id", "folders", ["parent_id"])

    op.add_column("files", sa.Column("folder_id", sa.Integer(), nullable=True))
    op.create_index("ix_files_folder_id", "files", ["folder_id"])
    op.create_foreign_key("fk_files_folder_id_folders", "files", "folders", ["folder_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_files_folder_id_folders", "files", type_="foreignkey")
    op.drop_index("ix_files_folder_id", table_name="files")
    op.drop_column("files", "folder_id")

    op.drop_index("ix_folders_parent_id", table_name="folders")
    op.drop_index("ix_folders_project_id", table_name="folders")
    op.drop_index("ix_folders_user_id", table_name="folders")
    op.drop_table("folders")

