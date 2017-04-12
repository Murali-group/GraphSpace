"""update edges table - drop label column

Revision ID: bc1ca08a429b
Revises: cc4a2d0d0d8f
Create Date: 2017-02-14 12:04:47.809225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc1ca08a429b'
down_revision = 'cc4a2d0d0d8f'
branch_labels = None
depends_on = None

# This is not required any more


def upgrade():
	# Remove label column
	# op.drop_column('edge', 'head_node_label')
	# op.drop_column('edge', 'tail_node_label')
	op.execute('UPDATE edge SET head_node_label=n.label FROM "node" AS n WHERE n.id = edge.head_node_id;')
	op.execute('UPDATE edge SET tail_node_label=n.label FROM "node" AS n WHERE n.id = edge.tail_node_id;')
	pass


def downgrade():
	# # Remove label column
	# op.add_column('edge', sa.Column('head_node_label', sa.String))
	# op.add_column('edge', sa.Column('tail_node_label', sa.String))
	# op.execute('UPDATE edge SET head_node_label=n.label FROM "node" AS n WHERE n.id = edge.head_node_id;')
	# op.execute('UPDATE edge SET tail_node_label=n.label FROM "node" AS n WHERE n.id = edge.tail_node_id;')
	pass
