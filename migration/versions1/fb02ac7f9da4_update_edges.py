"""update edges

Revision ID: fb02ac7f9da4
Revises: c455a25c3c96
Create Date: 2017-02-12 18:39:15.856509

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb02ac7f9da4'
down_revision = 'c455a25c3c96'
branch_labels = None
depends_on = None


def upgrade():
	# op.drop_index('edge_idx_head_label_tail_label', 'edge')
	# op.drop_index('edge_idx_head_id_tail_id', 'edge')
	# op.add_column('edge', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	# op.add_column('edge', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	#
	# # # Replacing graph_id, user_id. with graph id in edge table
	# op.alter_column('edge', 'graph_id', new_column_name='old_graph_id')
	# op.add_column('edge', sa.Column('graph_id', sa.Integer))
	# op.execute('UPDATE edge SET graph_id=g.id FROM "graph" AS g WHERE g.name = edge.old_graph_id AND g.owner_email = edge.user_id;')
	# op.drop_column('edge', 'old_graph_id')
	# op.drop_column('edge', 'user_id')
	# op.alter_column('edge', 'graph_id', nullable=False)

	# op.create_index('_node_uc_graph_id_name', 'node', ['graph_id', 'name'], unique=True)
	# op.create_index('ix_node_id', 'node', ['id'], unique=True)
	#
	# op.alter_column('edge', 'edge_id', new_column_name='name')
	# op.alter_column('edge', 'directed', new_column_name='is_directed', nullable=False)
	#
	# # # Replacing head_node_id with node id in edge table
	# op.alter_column('edge', 'head_node_id', new_column_name='old_head_node_id')
	# op.add_column('edge', sa.Column('head_node_id', sa.Integer))
	# op.execute('UPDATE edge SET head_node_id=n.id FROM "node" AS n WHERE n.name = edge.old_head_node_id AND n.graph_id = edge.graph_id;')
	# op.drop_column('edge', 'old_head_node_id')
	# op.alter_column('edge', 'head_node_id', nullable=False)
	#
	# # # Replacing head_node_id with node id in edge table
	# op.alter_column('edge', 'tail_node_id', new_column_name='old_tail_node_id')
	# op.add_column('edge', sa.Column('tail_node_id', sa.Integer))
	# op.execute('UPDATE edge SET tail_node_id=n.id FROM "node" AS n WHERE n.name = edge.old_tail_node_id AND n.graph_id = edge.graph_id;')
	# op.drop_column('edge', 'old_tail_node_id')
	# op.alter_column('edge', 'tail_node_id', nullable=False)
	#
	# op.drop_column('edge', 'head_node_label')
	# op.drop_column('edge', 'tail_node_label')
	#
	# op.drop_constraint('edge_pkey', 'edge', type_='primary')
	#
	# op.execute('ALTER TABLE "edge" ADD PRIMARY KEY (id);')
	# op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_head_node_id_fkey FOREIGN KEY (head_node_id) REFERENCES node (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_tail_node_id_fkey FOREIGN KEY (tail_node_id) REFERENCES node (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_graph_id_fkey FOREIGN KEY (graph_id) REFERENCES graph (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')

	pass


def downgrade():
	# op.drop_column('edge', 'created_at')
	# op.drop_column('edge', 'updated_at')
	#
	# # # Undo Replacing graph_id, user_id. with graph id in edge table
	# op.alter_column('edge', 'graph_id', new_column_name='old_graph_id')
	# op.add_column('edge', sa.Column('graph_id', sa.String))
	# op.add_column('edge', sa.Column('user_id', sa.String))
	# op.execute('UPDATE "edge" SET graph_id=g.name FROM "graph" AS g WHERE g.id = old_graph_id;')
	# op.execute('UPDATE "edge" SET user_id=g.owner_email FROM "graph" AS g WHERE g.id = old_graph_id;')
	# op.drop_column('edge', 'old_graph_id')
	# op.alter_column('edge', 'graph_id', nullable=False)
	# op.alter_column('edge', 'user_id', nullable=False)

	# op.alter_column('edge', 'name', new_column_name='edge_id')
	# op.alter_column('edge', 'is_directed', new_column_name='directed')
	#
	# op.add_column('edge', sa.Column('head_node_label', sa.String))
	# op.add_column('edge', sa.Column('tail_node_label', sa.String))
	# op.execute('UPDATE edge SET head_node_label=n.label FROM "node" AS n WHERE n.id = edge.head_node_id;')
	# op.execute('UPDATE edge SET tail_node_label=n.label FROM "node" AS n WHERE n.id = edge.tail_node_id;')
	#
	# # # undo Replacing head_node_id with node id in edge table
	# op.alter_column('edge', 'head_node_id', new_column_name='old_head_node_id')
	# op.add_column('edge', sa.Column('head_node_id', sa.String))
	# op.execute('UPDATE edge SET head_node_id=n.name FROM "node" AS n WHERE n.id = edge.old_head_node_id;')
	# op.drop_column('edge', 'old_head_node_id')
	# op.alter_column('edge', 'head_node_id', nullable=False)
	#
	# # # undo Replacing head_node_id with node id in edge table
	# op.alter_column('edge', 'tail_node_id', new_column_name='old_tail_node_id')
	# op.add_column('edge', sa.Column('tail_node_id', sa.String))
	# op.execute('UPDATE edge SET tail_node_id=n.name FROM "node" AS n WHERE n.id = edge.old_tail_node_id;')
	# op.drop_column('edge', 'old_tail_node_id')
	# op.alter_column('edge', 'tail_node_id', nullable=False)
	#
	# op.drop_constraint('edge_head_node_id_fkey', 'edge', type_='foreignkey')
	# op.drop_constraint('edge_tail_node_id_fkey', 'edge', type_='foreignkey')
	# op.drop_constraint('edge_graph_id_fkey', 'edge', type_='foreignkey')
	#
	# op.drop_index('_node_uc_graph_id_name', 'node')
	# op.drop_index('ix_node_id', 'node')

	pass
