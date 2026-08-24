"""init

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'manufacturers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('name_en', sa.String(), nullable=True),
        sa.Column('name_cn', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('website', sa.String(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('data_source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_mfr_name', 'manufacturers', ['name'])
    op.create_index('idx_mfr_verified', 'manufacturers', ['is_verified'])

    op.create_table(
        'lens_catalog',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manufacturer_id', sa.Integer(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('sku', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('focal_length_mm', sa.Float(), nullable=True),
        sa.Column('focal_length_min', sa.Float(), nullable=True),
        sa.Column('focal_length_max', sa.Float(), nullable=True),
        sa.Column('max_aperture', sa.Float(), nullable=True),
        sa.Column('min_aperture', sa.Float(), nullable=True),
        sa.Column('image_circle_mm', sa.Float(), nullable=True),
        sa.Column('min_working_distance_mm', sa.Float(), nullable=True),
        sa.Column('max_working_distance_mm', sa.Float(), nullable=True),
        sa.Column('nominal_wd_mm', sa.Float(), nullable=True),
        sa.Column('mount_type', sa.String(), nullable=True),
        sa.Column('mount_flange_mm', sa.Float(), nullable=True),
        sa.Column('outer_diameter_mm', sa.Float(), nullable=True),
        sa.Column('length_mm', sa.Float(), nullable=True),
        sa.Column('weight_g', sa.Float(), nullable=True),
        sa.Column('mtf50_lpmm', sa.Float(), nullable=True),
        sa.Column('distortion_percent', sa.Float(), nullable=True),
        sa.Column('telecentricity_deg', sa.Float(), nullable=True),
        sa.Column('na', sa.Float(), nullable=True),
        sa.Column('working_f_number', sa.Float(), nullable=True),
        sa.Column('wavelength_min_nm', sa.Integer(), nullable=True),
        sa.Column('wavelength_max_nm', sa.Integer(), nullable=True),
        sa.Column('coating_type', sa.String(), nullable=True),
        sa.Column('price_usd', sa.Float(), nullable=True),
        sa.Column('datasheet_url', sa.String(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('data_source', sa.String(), nullable=True),
        sa.Column('data_quality_score', sa.Float(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['manufacturer_id'], ['manufacturers.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('manufacturer_id', 'model')
    )
    op.create_index('idx_lens_category', 'lens_catalog', ['category'])
    op.create_index('idx_lens_focal', 'lens_catalog', ['focal_length_mm'])
    op.create_index('idx_lens_mount', 'lens_catalog', ['mount_type'])
    op.create_index('idx_lens_image_circle', 'lens_catalog', ['image_circle_mm'])
    op.create_index(
        'idx_lens_wd', 'lens_catalog',
        ['min_working_distance_mm', 'max_working_distance_mm']
    )
    op.create_index(
        'idx_lens_composite', 'lens_catalog',
        ['category', 'mount_type', 'focal_length_mm']
    )

    op.create_table(
        'detector_catalog',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manufacturer_id', sa.Integer(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('sensor_format_inch', sa.String(), nullable=True),
        sa.Column('sensor_w_mm', sa.Float(), nullable=True),
        sa.Column('sensor_h_mm', sa.Float(), nullable=True),
        sa.Column('sensor_diag_mm', sa.Float(), nullable=True),
        sa.Column('resolution_w', sa.Integer(), nullable=True),
        sa.Column('resolution_h', sa.Integer(), nullable=True),
        sa.Column('pixel_size_um', sa.Float(), nullable=True),
        sa.Column('quantum_efficiency_peak', sa.Float(), nullable=True),
        sa.Column('read_noise_e', sa.Float(), nullable=True),
        sa.Column('dark_current_e_s', sa.Float(), nullable=True),
        sa.Column('full_well_e', sa.Float(), nullable=True),
        sa.Column('dynamic_range_db', sa.Float(), nullable=True),
        sa.Column('netd_mk', sa.Float(), nullable=True),
        sa.Column('spectral_range_min_um', sa.Float(), nullable=True),
        sa.Column('spectral_range_max_um', sa.Float(), nullable=True),
        sa.Column('mount_type', sa.String(), nullable=True),
        sa.Column('data_interface', sa.String(), nullable=True),
        sa.Column('max_fps_full', sa.Float(), nullable=True),
        sa.Column('price_usd', sa.Float(), nullable=True),
        sa.Column('datasheet_url', sa.String(), nullable=True),
        sa.Column('data_source', sa.String(), nullable=True),
        sa.Column('data_quality_score', sa.Float(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['manufacturer_id'], ['manufacturers.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('manufacturer_id', 'model')
    )
    op.create_index('idx_det_category', 'detector_catalog', ['category'])
    op.create_index('idx_det_sensor_size', 'detector_catalog', ['sensor_diag_mm'])
    op.create_index('idx_det_pixel_size', 'detector_catalog', ['pixel_size_um'])
    op.create_index('idx_det_mount', 'detector_catalog', ['mount_type'])
    op.create_index(
        'idx_det_composite', 'detector_catalog',
        ['category', 'mount_type', 'sensor_diag_mm']
    )

    op.create_table(
        'compatibility_cache',
        sa.Column('cache_key', sa.String(), nullable=False),
        sa.Column('lens_id', sa.Integer(), nullable=False),
        sa.Column('detector_id', sa.Integer(), nullable=False),
        sa.Column('adapter_id', sa.Integer(), nullable=True),
        sa.Column('result_json', sa.Text(), nullable=False),
        sa.Column('is_compatible', sa.Boolean(), nullable=True),
        sa.Column('compatibility_score', sa.Float(), nullable=True),
        sa.Column('coverage_ratio', sa.Float(), nullable=True),
        sa.Column('nyquist_ratio', sa.Float(), nullable=True),
        sa.Column('vignetting_risk', sa.Boolean(), nullable=True),
        sa.Column('algorithm_version', sa.String(), nullable=False),
        sa.Column('computed_at', sa.DateTime(), nullable=True),
        sa.Column('access_count', sa.Integer(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('cache_key')
    )
    op.create_index(
        'idx_compat_cache_lookup', 'compatibility_cache',
        ['lens_id', 'detector_id', 'adapter_id']
    )
    op.create_index('idx_compat_cache_lru', 'compatibility_cache', ['last_accessed'])
    op.create_index('idx_compat_cache_score', 'compatibility_cache', ['compatibility_score'])

    op.create_table(
        'user_projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('domain', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('modified_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'project_setups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('lens_id', sa.Integer(), nullable=True),
        sa.Column('detector_id', sa.Integer(), nullable=True),
        sa.Column('adapter_id', sa.Integer(), nullable=True),
        sa.Column('lens_snapshot', sa.Text(), nullable=True),
        sa.Column('detector_snapshot', sa.Text(), nullable=True),
        sa.Column('adapter_snapshot', sa.Text(), nullable=True),
        sa.Column('snapshot_version', sa.Integer(), nullable=True),
        sa.Column('snapshot_date', sa.DateTime(), nullable=True),
        sa.Column('drift_detected', sa.Boolean(), nullable=True),
        sa.Column('drift_details', sa.Text(), nullable=True),
        sa.Column('custom_lens_params', sa.Text(), nullable=True),
        sa.Column('custom_detector_params', sa.Text(), nullable=True),
        sa.Column('calculated_params', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['user_projects.id']),
        sa.ForeignKeyConstraint(['lens_id'], ['lens_catalog.id']),
        sa.ForeignKeyConstraint(['detector_id'], ['detector_catalog.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('project_setups')
    op.drop_table('user_projects')
    op.drop_table('compatibility_cache')
    op.drop_table('detector_catalog')
    op.drop_table('lens_catalog')
    op.drop_table('manufacturers')
