"""update edges table - change head node column

Revision ID: 2b2cd5989452
Revises: 88903cfee955
Create Date: 2017-02-14 11:59:35.827366

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b2cd5989452'
down_revision = '88903cfee955'
branch_labels = None
depends_on = None


def upgrade():
	# # Replacing head_node_id with node id in edge table
	op.alter_column('edge', 'head_node_id', new_column_name='head_node_name')
	op.add_column('edge', sa.Column('head_node_id', sa.Integer))
	op.execute('UPDATE edge SET head_node_id=n.id FROM "node" AS n WHERE n.name = edge.head_node_name AND n.graph_id = edge.graph_id;')
	# op.drop_column('edge', 'head_node_name')
	op.alter_column('edge', 'head_node_id', nullable=False)


def downgrade():
	# # undo Replacing head_node_id with node id in edge table
	op.alter_column('edge', 'head_node_id', new_column_name='old_head_node_id')
	op.add_column('edge', sa.Column('head_node_id', sa.String))
	op.execute('UPDATE edge SET head_node_id=n.name FROM "node" AS n WHERE n.id = edge.old_head_node_id;')
	op.drop_column('edge', 'old_head_node_id')
	op.drop_column('edge', 'head_node_name')
	op.alter_column('edge', 'head_node_id', nullable=False)
