"""update edges table

Revision ID: ffca8cad2f7c
Revises: 18108644dac9
Create Date: 2017-02-13 23:36:09.438258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffca8cad2f7c'
down_revision = '18108644dac9'
branch_labels = None
depends_on = None


def upgrade():

	# Remove index
	op.drop_index('edge_idx_head_label_tail_label', 'edge')
	op.drop_index('edge_idx_head_id_tail_id', 'edge')

	# # Replacing graph_id, user_id. with graph id in edge table
	op.alter_column('edge', 'graph_id', new_column_name='old_graph_id')
	op.add_column('edge', sa.Column('graph_id', sa.Integer))
	op.execute('UPDATE edge SET graph_id=g.id FROM "graph" AS g WHERE g.name = edge.old_graph_id AND g.owner_email = edge.user_id;')
	op.drop_column('edge', 'old_graph_id')
	op.drop_column('edge', 'user_id')
	op.alter_column('edge', 'graph_id', nullable=False)

	# # Replacing head_node_id with node id in edge table
	op.alter_column('edge', 'head_node_id', new_column_name='old_head_node_id')
	op.add_column('edge', sa.Column('head_node_id', sa.Integer))
	op.execute('UPDATE edge SET head_node_id=n.id FROM "node" AS n WHERE n.name = edge.old_head_node_id AND n.graph_id = edge.graph_id;')
	op.drop_column('edge', 'old_head_node_id')
	op.alter_column('edge', 'head_node_id', nullable=False)

	# # Replacing head_node_id with node id in edge table
	op.alter_column('edge', 'tail_node_id', new_column_name='old_tail_node_id')
	op.add_column('edge', sa.Column('tail_node_id', sa.Integer))
	op.execute('UPDATE edge SET tail_node_id=n.id FROM "node" AS n WHERE n.name = edge.old_tail_node_id AND n.graph_id = edge.graph_id;')
	op.drop_column('edge', 'old_tail_node_id')
	op.alter_column('edge', 'tail_node_id', nullable=False)

	# Add date columns
	op.add_column('edge', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.add_column('edge', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))

	# Rename name column
	op.alter_column('edge', 'edge_id', new_column_name='name')

	# Rename directed column
	op.alter_column('edge', 'directed', new_column_name='is_directed', nullable=False)

	# Remove label column
	op.drop_column('edge', 'head_node_label')
	op.drop_column('edge', 'tail_node_label')

	# Create New Index
	# It seems there are duplicate edges for same 'graph_id', 'head_node_id', 'tail_node_id'. Coz there was no unique constraint on the columns.
	# Solution: Drop one of the duplicate entries.
	op.execute('DELETE FROM edge WHERE ctid NOT IN (SELECT MAX(ctid) FROM edge GROUP BY graph_id, head_node_id, tail_node_id);')
	op.create_index('_edge_uc_graph_id_head_node_id_tail_node_id', 'edge', ['graph_id', 'head_node_id', 'tail_node_id'], unique=True)
	op.create_index('_edge_uc_graph_id_name', 'edge', ['graph_id', 'name'], unique=True)

	# Add new foreign key reference
	op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_head_node_id_fkey FOREIGN KEY (head_node_id) REFERENCES node (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_tail_node_id_fkey FOREIGN KEY (tail_node_id) REFERENCES node (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_graph_id_fkey FOREIGN KEY (graph_id) REFERENCES graph (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')


def downgrade():

	# Remove new foreign key reference
	op.drop_constraint('edge_head_node_id_fkey', 'edge', type_='foreignkey')
	op.drop_constraint('edge_tail_node_id_fkey', 'edge', type_='foreignkey')
	op.drop_constraint('edge_graph_id_fkey', 'edge', type_='foreignkey')

	# Drop New Index
	op.drop_index('_edge_uc_graph_id_head_node_id_tail_node_id', 'edge')
	op.drop_index('_edge_uc_graph_id_name', 'edge')

	# Remove label column
	op.add_column('edge', sa.Column('head_node_label', sa.String))
	op.add_column('edge', sa.Column('tail_node_label', sa.String))
	op.execute('UPDATE edge SET head_node_label=n.label FROM "node" AS n WHERE n.id = edge.head_node_id;')
	op.execute('UPDATE edge SET tail_node_label=n.label FROM "node" AS n WHERE n.id = edge.tail_node_id;')

	# Rename directed column
	op.alter_column('edge', 'is_directed', new_column_name='directed')

	# Undo Rename name column
	op.alter_column('edge', 'name', new_column_name='edge_id')

	# Drop date columns
	op.drop_column('edge', 'created_at')
	op.drop_column('edge', 'updated_at')

	# # undo Replacing head_node_id with node id in edge table
	op.alter_column('edge', 'head_node_id', new_column_name='old_head_node_id')
	op.add_column('edge', sa.Column('head_node_id', sa.String))
	op.execute('UPDATE edge SET head_node_id=n.name FROM "node" AS n WHERE n.id = edge.old_head_node_id;')
	op.drop_column('edge', 'old_head_node_id')
	op.alter_column('edge', 'head_node_id', nullable=False)

	# # undo Replacing head_node_id with node id in edge table
	op.alter_column('edge', 'tail_node_id', new_column_name='old_tail_node_id')
	op.add_column('edge', sa.Column('tail_node_id', sa.String))
	op.execute('UPDATE edge SET tail_node_id=n.name FROM "node" AS n WHERE n.id = edge.old_tail_node_id;')
	op.drop_column('edge', 'old_tail_node_id')
	op.alter_column('edge', 'tail_node_id', nullable=False)

	# # Undo Replacing graph_id, user_id. with graph id in edge table
	op.alter_column('edge', 'graph_id', new_column_name='old_graph_id')
	op.add_column('edge', sa.Column('graph_id', sa.String))
	op.add_column('edge', sa.Column('user_id', sa.String))
	op.execute('UPDATE "edge" SET graph_id=g.name FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.execute('UPDATE "edge" SET user_id=g.owner_email FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.drop_column('edge', 'old_graph_id')
	op.alter_column('edge', 'graph_id', nullable=False)
	op.alter_column('edge', 'user_id', nullable=False)

	op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_user_id_fkey1 FOREIGN KEY (user_id, graph_id, head_node_id) REFERENCES node (user_id, graph_id, node_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_user_id_fkey2 FOREIGN KEY (user_id, graph_id, tail_node_id) REFERENCES node (user_id, graph_id, node_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')

	pass
