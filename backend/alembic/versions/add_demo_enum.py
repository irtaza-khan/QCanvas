"""Manually add DEMO to user role enum

Revision ID: add_demo_role
Revises: (check latest)
Create Date: 2025-12-02

"""
from alembic import op

# revision identifiers
revision = 'add_demo_role'
down_revision = None  # Will be set by user

def upgrade():
    # Add 'demo' to the userrole enum
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'demo'")

def downgrade():
    # PostgreSQL doesn't support removing enum values easily
    pass
