"""add gin indices on node table

Revision ID: d1d125cdf285
Revises: 9563a03981d9
Create Date: 2017-02-16 17:21:06.549672

We need to add separate indices on name and label columns for faster ILIKE search queries. An example is explained here:
https://github.com/Murali-group/GraphSpace/wiki/Faster-ILIKE-queries
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1d125cdf285'
down_revision = '9563a03981d9'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE INDEX node_idx_name  ON node USING gin("name" gin_trgm_ops);')
    op.execute('CREATE INDEX node_idx_label  ON node USING gin("label" gin_trgm_ops);')


def downgrade():
    op.drop_index('node_idx_name', 'node')
    op.drop_index('node_idx_label', 'node')
