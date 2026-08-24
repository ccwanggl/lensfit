"""add_data_source_and_manufacturer_indexes

Revision ID: 0ac6c641b5d7
Revises: 003
Create Date: 2026-06-15 00:25:29.168130

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '0ac6c641b5d7'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index('ix_lens_data_source', 'lens_catalog', ['data_source'], unique=False)
    op.create_index('ix_lens_manufacturer_id', 'lens_catalog', ['manufacturer_id'], unique=False)
    op.create_index('ix_detector_data_source', 'detector_catalog', ['data_source'], unique=False)
    op.create_index(
        'ix_detector_manufacturer_id', 'detector_catalog', ['manufacturer_id'], unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_lens_data_source', table_name='lens_catalog')
    op.drop_index('ix_lens_manufacturer_id', table_name='lens_catalog')
    op.drop_index('ix_detector_data_source', table_name='detector_catalog')
    op.drop_index('ix_detector_manufacturer_id', table_name='detector_catalog')
