"""update edges table - create index

Revision ID: 3125de4a065f
Revises: bc1ca08a429b
Create Date: 2017-02-14 12:11:42.425671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3125de4a065f'
down_revision = 'bc1ca08a429b'
branch_labels = None
depends_on = None

# 'EXPLAIN ANALYZE delete from edge where exists (select 1 from edge t2 where t2.graph_id = edge.graph_id and t2.head_node_id = edge.head_node_id and t2.tail_node_id = edge.tail_node_id and t2.ctid > edge.ctid);'

def upgrade():
	# Create New Index
	# It seems there are duplicate edges for same 'graph_id', 'head_node_id', 'tail_node_id'. Coz there was no unique constraint on the columns.
	# Solution: Drop one of the duplicate entries.
	op.execute('delete from edge where exists (select 1 from edge t2 where t2.graph_id = edge.graph_id and t2.head_node_id = edge.head_node_id and t2.tail_node_id = edge.tail_node_id and t2.ctid > edge.ctid);')
	op.create_index('_edge_uc_graph_id_head_node_id_tail_node_id', 'edge', ['graph_id', 'head_node_id', 'tail_node_id'], unique=True)
	op.create_index('_edge_uc_graph_id_name', 'edge', ['graph_id', 'name'], unique=True)



def downgrade():
	# Drop New Index
	op.drop_index('_edge_uc_graph_id_head_node_id_tail_node_id', 'edge')
	op.drop_index('_edge_uc_graph_id_name', 'edge')
