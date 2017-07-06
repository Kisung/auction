"""Add users table

Revision ID: 7c3b92463467
Revises: 930d92411706
Create Date: 2017-07-06 13:57:22.833619

"""
from alembic import op
import sqlalchemy as sa

from auction.models import JSONType


# revision identifiers, used by Alembic.
revision = '7c3b92463467'
down_revision = '930d92411706'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column('registered_at', sa.DateTime(timezone=False),
                  nullable=False),
        sa.Column('family_name', sa.String(), nullable=False),
        sa.Column('given_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('organization', sa.String(), nullable=False),
        sa.Column('data', JSONType, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column(
        'auctions', sa.Column('seller_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key(None, 'auctions', 'users', ['seller_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'auctions', type_='foreignkey')
    op.drop_column('auctions', 'seller_id')
    op.drop_table('users')
