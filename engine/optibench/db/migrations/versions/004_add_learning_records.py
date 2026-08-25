"""add learning_records table

Revision ID: 004
Revises: 0ac6c641b5d7
Create Date: 2026-08-24 00:00:00.000000

Learning-first 阶段 2：学习者状态单表（概念已读、实验/面包板完成、测验成绩）。
"""
import sqlalchemy as sa
from alembic import op

revision = '004'
down_revision = '0ac6c641b5d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'learning_records',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('learner_id', sa.String(), nullable=False, server_default='default'),
        sa.Column('item_kind', sa.String(), nullable=False),
        sa.Column('item_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('learner_id', 'item_kind', 'item_id', name='uq_learning_item'),
    )
    op.create_index(
        'ix_learning_learner_kind', 'learning_records', ['learner_id', 'item_kind']
    )


def downgrade() -> None:
    op.drop_index('ix_learning_learner_kind', table_name='learning_records')
    op.drop_table('learning_records')
