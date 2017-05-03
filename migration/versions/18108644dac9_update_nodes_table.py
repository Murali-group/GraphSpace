"""update nodes table

Revision ID: 18108644dac9
Revises: ed8a5d6d9b4a
Create Date: 2017-02-13 23:24:12.895694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18108644dac9'
down_revision = 'ed8a5d6d9b4a'
branch_labels = None
depends_on = None


def upgrade():

	# Remove index
	op.drop_index('node_idx_graph_id_user_id', 'node')
	op.drop_index('node_index_node_id_graph_id', 'node')
	op.drop_index('node_index_label_graph_id', 'node')
	op.drop_index('node_index_node_id', 'node')
	op.drop_index('node_index_label', 'node')

	# Drop OLD PKey
	op.drop_constraint('node_pkey', 'node', type_='primary')

	# Add id column
	op.execute('ALTER TABLE "node" ADD id SERIAL PRIMARY KEY UNIQUE;')

	# # Replacing graph_id, user_id. with graph id in node table
	op.alter_column('node', 'graph_id', new_column_name='old_graph_id')
	op.add_column('node', sa.Column('graph_id', sa.Integer))
	op.execute('UPDATE node SET graph_id=g.id FROM "graph" AS g WHERE g.name = node.old_graph_id AND g.owner_email = node.user_id;')
	op.drop_column('node', 'old_graph_id')
	op.drop_column('node', 'user_id')
	op.alter_column('node', 'graph_id', nullable=False)

	# Add date columns
	op.alter_column('node', 'modified', new_column_name='updated_at', server_default=sa.func.current_timestamp())
	op.add_column('node', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.execute('UPDATE "node" SET created_at=updated_at')

	# Rename name column
	op.alter_column('node', 'node_id', new_column_name='name')

	# Create New Index
	op.create_index('_node_uc_graph_id_name', 'node', ['graph_id', 'name'], unique=True)

	# Add new foreign key reference
	op.execute('ALTER TABLE node ADD CONSTRAINT node_graph_id_fkey FOREIGN KEY (graph_id) REFERENCES "graph" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')


def downgrade():

	# Remove new foreign key reference
	op.drop_constraint('node_graph_id_fkey', 'node', type_='foreignkey')

	# Drop New Index
	op.drop_index('_node_uc_graph_id_name', 'node')

	# Undo Rename name column
	op.alter_column('node', 'name', new_column_name='node_id')

	# Drop date columns
	op.alter_column('node', 'updated_at', new_column_name='modified', server_default=sa.func.current_timestamp())
	op.drop_column('node', 'created_at')

	# # Undo Replacing graph_id, user_id. with graph id in node table
	op.alter_column('node', 'graph_id', new_column_name='old_graph_id')
	op.add_column('node', sa.Column('graph_id', sa.String))
	op.add_column('node', sa.Column('user_id', sa.String))
	op.execute('UPDATE "node" SET graph_id=g.name FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.execute('UPDATE "node" SET user_id=g.owner_email FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.drop_column('node', 'old_graph_id')
	op.alter_column('node', 'graph_id', nullable=False)
	op.alter_column('node', 'user_id', nullable=False)

	# Remove id column
	op.drop_column('node', 'id')

	# Reinstate OLD PKey
	op.execute('ALTER TABLE "node" ADD PRIMARY KEY (node_id, user_id, graph_id);')

	pass
