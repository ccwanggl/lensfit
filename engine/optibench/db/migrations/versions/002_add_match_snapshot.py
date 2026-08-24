"""add match_result_snapshot to project_setups

Revision ID: 002
Revises: 001
Create Date: 2026-05-28 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('project_setups', sa.Column('match_result_snapshot', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('project_setups', 'match_result_snapshot')
