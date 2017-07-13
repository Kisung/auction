"""Add social_id field to User

Revision ID: 644f0e8a8310
Revises: 7c3b92463467
Create Date: 2017-07-09 22:48:01.770833

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '644f0e8a8310'
down_revision = '7c3b92463467'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('social_id', sa.String(), nullable=True))
    op.alter_column(
        'users', 'organization', existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column(
        'users', 'family_name', existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column(
        'users', 'given_name', existing_type=sa.VARCHAR(), nullable=True)
    op.create_index(
        op.f('ix_users_social_id'), 'users', ['social_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_users_social_id'), table_name='users')
    op.alter_column(
        'users', 'given_name', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column(
        'users', 'family_name', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column(
        'users', 'organization', existing_type=sa.VARCHAR(), nullable=False)
    op.drop_column('users', 'social_id')
