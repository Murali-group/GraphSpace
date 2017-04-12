"""add gin indices on graph name

Revision ID: 1bce06cc4e3d
Revises: d1d125cdf285
Create Date: 2017-02-16 17:25:30.995664

Since we do ILIKE query on graph name. We need gin indices. Their performance in compariso to BTREE indices is shows here:
https://github.com/Murali-group/GraphSpace/wiki/Faster-ILIKE-queries

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1bce06cc4e3d'
down_revision = 'd1d125cdf285'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE INDEX graph_idx_name ON graph USING gin("name" gin_trgm_ops);')


def downgrade():
    op.drop_index('graph_idx_name', 'graph')