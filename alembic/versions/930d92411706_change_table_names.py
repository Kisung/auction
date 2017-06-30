"""Change table names

Revision ID: 930d92411706
Revises: e1832daf9fb0
Create Date: 2017-06-30 14:53:29.391441

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '930d92411706'
down_revision = 'e1832daf9fb0'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('auction', 'auctions')
    op.rename_table('bid', 'bids')


def downgrade():
    op.rename_table('auctions', 'auction')
    op.rename_table('bids', 'bid')
