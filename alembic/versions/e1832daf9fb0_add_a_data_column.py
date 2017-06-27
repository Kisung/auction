"""Add a data column

Revision ID: e1832daf9fb0
Revises: 
Create Date: 2017-06-27 14:05:42.026970

"""
from alembic import op
import sqlalchemy as sa

from auction.models import JSONType


# revision identifiers, used by Alembic.
revision = 'e1832daf9fb0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('auction', sa.Column('data', JSONType))


def downgrade():
    op.drop_column('auction', 'data')
