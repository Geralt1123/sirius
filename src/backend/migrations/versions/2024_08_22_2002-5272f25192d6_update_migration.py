"""update_migration

Revision ID: 5272f25192d6
Revises: 4a2da12b421f
Create Date: 2024-08-22 20:02:14.258686

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5272f25192d6'
down_revision = '4a2da12b421f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('file_metadata', sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema='sirius')
    op.drop_column('file_metadata', 'dilatation_y', schema='sirius')
    op.drop_column('file_metadata', 'eroz_x', schema='sirius')
    op.drop_column('file_metadata', 'eroz_iteration', schema='sirius')
    op.drop_column('file_metadata', 'bilat_d', schema='sirius')
    op.drop_column('file_metadata', 'gaus_sigma_y', schema='sirius')
    op.drop_column('file_metadata', 'eroz_y', schema='sirius')
    op.drop_column('file_metadata', 'gaus_core_y', schema='sirius')
    op.drop_column('file_metadata', 'dilatation_x', schema='sirius')
    op.drop_column('file_metadata', 'gaus_core_x', schema='sirius')
    op.drop_column('file_metadata', 'bilat_color', schema='sirius')
    op.drop_column('file_metadata', 'bilat_coord', schema='sirius')
    op.drop_column('file_metadata', 'gaus_sigma_x', schema='sirius')
    op.drop_column('file_metadata', 'dilatation_iteration', schema='sirius')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('file_metadata', sa.Column('dilatation_iteration', sa.INTEGER(), autoincrement=False, nullable=True), schema='sirius')
    op.add_column('file_metadata', sa.Column('gaus_sigma_x', sa.INTEGER(), autoincrement=False, nullable=True), schema='sirius')
    op.add_column('file_metadata', sa.Column('bilat_coord', sa.INTEGER(), autoincrement=False, nullable=True), schema='sirius')
    op.add_column('file_metadata', sa.Column('bilat_color', sa.INTEGER(), autoincrement=False, nullable=True), schema='sirius')
    op.add_column('file_metadata', sa.Column('gaus_core_x', sa.INTEGER(), autoincrement=False, nullable=True), schema='sirius')
    op.add_column('file_metadata', sa.Column('dilatation_x', sa.INTEGER(), autoincrement=False, nullable=True), schema='sirius')
    op.add_column('file_metadata', sa.Column('gaus_core_y', sa.INTEGER(), autoincrement=False, nullable=True), schema='sirius')
    op.add_column('file_metadata', sa.Column('eroz_y', sa.INTEGER(), autoincrement=False, nullable=True), schema='sirius')
    op.add_column('file_metadata', sa.Column('gaus_sigma_y', sa.INTEGER(), autoincrement=False, nullable=True), schema='sirius')
    op.add_column('file_metadata', sa.Column('bilat_d', sa.INTEGER(), autoincrement=False, nullable=True), schema='sirius')
    op.add_column('file_metadata', sa.Column('eroz_iteration', sa.INTEGER(), autoincrement=False, nullable=True), schema='sirius')
    op.add_column('file_metadata', sa.Column('eroz_x', sa.INTEGER(), autoincrement=False, nullable=True), schema='sirius')
    op.add_column('file_metadata', sa.Column('dilatation_y', sa.INTEGER(), autoincrement=False, nullable=True), schema='sirius')
    op.drop_column('file_metadata', 'meta', schema='sirius')
    # ### end Alembic commands ###
