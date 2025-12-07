"""Add complete schema

Revision ID: 4a1b2c3d4e5f
Revises: 2b6207bf1c6e
Create Date: 2025-12-03 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4a1b2c3d4e5f'
down_revision: Union[str, Sequence[str], None] = '2b6207bf1c6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create Enums
    # Note: We use sa.Enum with name argument to create the type in Postgres
    
    # Create conversions table
    op.create_table('conversions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('source_framework', sa.Enum('CIRQ', 'QISKIT', 'PENNYLANE', name='quantumframework'), nullable=False),
        sa.Column('target_framework', sa.Enum('CIRQ', 'QISKIT', 'PENNYLANE', name='quantumframework'), nullable=False),
        sa.Column('source_code', sa.Text(), nullable=False),
        sa.Column('target_code', sa.Text(), nullable=True),
        sa.Column('qasm_code', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('SUCCESS', 'FAILED', 'PENDING', 'RUNNING', name='executionstatus'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create conversion_stats table
    op.create_table('conversion_stats',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conversion_id', sa.UUID(), nullable=False),
        sa.Column('num_qubits', sa.Integer(), nullable=False),
        sa.Column('num_gates', sa.Integer(), nullable=False),
        sa.Column('circuit_depth', sa.Integer(), nullable=False),
        sa.Column('optimization_level', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['conversion_id'], ['conversions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('conversion_id')
    )
    
    # Create simulations table
    op.create_table('simulations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('qasm_code', sa.Text(), nullable=False),
        sa.Column('backend', sa.Enum('STATEVECTOR', 'DENSITY_MATRIX', 'STABILIZER', name='simulationbackend'), nullable=False),
        sa.Column('shots', sa.Integer(), nullable=False),
        sa.Column('results_json', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('SUCCESS', 'FAILED', 'PENDING', 'RUNNING', name='executionstatus'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create sessions table
    op.create_table('sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('session_type', sa.Enum('WEBSOCKET', 'API', 'WEB', name='sessiontype'), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token')
    )
    
    # Create api_activity table
    op.create_table('api_activity',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=False),
        sa.Column('request_body_hash', sa.String(length=64), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('api_activity')
    op.drop_table('sessions')
    op.drop_table('simulations')
    op.drop_table('conversion_stats')
    op.drop_table('conversions')
    
    # Drop Enums
    sa.Enum(name='quantumframework').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='simulationbackend').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='executionstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='sessiontype').drop(op.get_bind(), checkfirst=True)
