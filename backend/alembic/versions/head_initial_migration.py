"""empty message

Revision ID: head
Revises: 
Create Date: 2026-07-07 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'head'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    op.create_table('code_snippets',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('prompt', sa.Text(), nullable=True),
    sa.Column('storage_key', sa.Text(), nullable=False),
    sa.Column('language', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_code_snippets_user_id'), 'code_snippets', ['user_id'], unique=False)
    
    op.create_table('execution_logs',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('snippet_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('code_hash', sa.String(length=64), nullable=False),
    sa.Column('exit_code', sa.Integer(), nullable=True),
    sa.Column('output_excerpt', sa.Text(), nullable=True),
    sa.Column('duration_ms', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['snippet_id'], ['code_snippets.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_execution_logs_user_id'), 'execution_logs', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_execution_logs_user_id'), table_name='execution_logs')
    op.drop_table('execution_logs')
    op.drop_index(op.f('ix_code_snippets_user_id'), table_name='code_snippets')
    op.drop_table('code_snippets')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
