"""update edges table - change tail node column

Revision ID: 5976898cbe4c
Revises: 2b2cd5989452
Create Date: 2017-02-14 12:00:46.311808

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5976898cbe4c'
down_revision = '2b2cd5989452'
branch_labels = None
depends_on = None


def upgrade():
	# # Replacing tail_node_id with node id in edge table
	op.alter_column('edge', 'tail_node_id', new_column_name='tail_node_name')
	op.add_column('edge', sa.Column('tail_node_id', sa.Integer))
	op.execute('UPDATE edge SET tail_node_id=n.id FROM "node" AS n WHERE n.name = edge.tail_node_name AND n.graph_id = edge.graph_id;')
	# op.drop_column('edge', 'tail_node_name')
	op.alter_column('edge', 'tail_node_id', nullable=False)


def downgrade():
	# # undo Replacing tail_node_id with node id in edge table
	op.alter_column('edge', 'tail_node_id', new_column_name='old_tail_node_id')
	op.add_column('edge', sa.Column('tail_node_id', sa.String))
	op.execute('UPDATE edge SET tail_node_id=n.name FROM "node" AS n WHERE n.id = edge.old_tail_node_id;')
	op.drop_column('edge', 'old_tail_node_id')
	op.drop_column('edge', 'tail_node_name')
	op.alter_column('edge', 'tail_node_id', nullable=False)
