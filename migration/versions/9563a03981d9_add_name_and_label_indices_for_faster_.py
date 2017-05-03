"""add name and label indices for faster edge search

Revision ID: 9563a03981d9
Revises: a2d96d82553f
Create Date: 2017-02-15 18:07:50.996957

We have added these columns so that we dont have to do the joins on tables. JOIN on tables takes a lot of time.
We need to add separate indices on name and label columns for faster ILIKE search queries. An example is explained here:
https://github.com/Murali-group/GraphSpace/wiki/Faster-ILIKE-queries

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9563a03981d9'
down_revision = 'a2d96d82553f'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE INDEX edge_idx_head_label_tail_label  ON edge USING gin("head_node_label", "tail_node_label" gin_trgm_ops);')
    op.execute('CREATE INDEX edge_idx_head_name_tail_name  ON edge USING gin("head_node_name", "tail_node_name" gin_trgm_ops);')
    op.execute('CREATE INDEX edge_idx_head_id_tail_id  ON edge ("head_node_id", "tail_node_id");')


def downgrade():
    op.drop_index('edge_idx_head_label_tail_label', 'edge')
    op.drop_index('edge_idx_head_name_tail_name', 'edge')
    op.drop_index('edge_idx_head_id_tail_id', 'edge')
