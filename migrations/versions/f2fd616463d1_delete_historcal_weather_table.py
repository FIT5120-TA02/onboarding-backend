"""delete historcal weather table

Revision ID: f2fd616463d1
Revises: fcaa17fd0e72
Create Date: 2025-03-14 22:05:21.539896

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f2fd616463d1'
down_revision = 'fcaa17fd0e72'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('historical_weather')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_column('users', 'mobile_number')
    op.drop_column('users', 'email')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('mobile_number', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_table('historical_weather',
    sa.Column('latitude', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('longitude', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('temperature', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('dt', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('humidity', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('pressure', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('wind_speed', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('weather_main', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('weather_description', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('location_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], name='historical_weather_location_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='historical_weather_pkey')
    )
    # ### end Alembic commands ###