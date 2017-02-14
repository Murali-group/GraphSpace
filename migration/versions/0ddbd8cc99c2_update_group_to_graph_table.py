"""update group to graph table

Revision ID: 0ddbd8cc99c2
Revises: 5b84b3dba2ac
Create Date: 2017-02-13 21:41:17.123279

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ddbd8cc99c2'
down_revision = '5b84b3dba2ac'
branch_labels = None
depends_on = None


def upgrade():
	# Drop OLD PKey
	op.drop_constraint('group_to_graph_pkey', 'group_to_graph', type_='primary')


	# Replacing group_id, owner_id with group id.
	op.alter_column('group_to_graph', 'group_id', new_column_name='old_group_id')
	op.add_column('group_to_graph', sa.Column('group_id', sa.Integer))
	op.execute('UPDATE group_to_graph SET group_id=g.id FROM "group" AS g WHERE g.group_id = old_group_id AND g.owner_email = group_owner;')
	op.drop_column('group_to_graph', 'old_group_id')
	op.drop_column('group_to_graph', 'group_owner')
	op.alter_column('group_to_graph', 'group_id', nullable=False)

	# Replacing graph_id, user_id. with graph id in group_to_graph table
	op.alter_column('group_to_graph', 'graph_id', new_column_name='old_graph_id')
	op.add_column('group_to_graph', sa.Column('graph_id', sa.Integer))
	op.execute('UPDATE group_to_graph SET graph_id=g.id FROM "graph" AS g WHERE g.name = group_to_graph.old_graph_id AND g.owner_email = group_to_graph.user_id;')
	op.drop_column('group_to_graph', 'old_graph_id')
	op.drop_column('group_to_graph', 'user_id')
	op.alter_column('group_to_graph', 'graph_id', nullable=False)


	# Add date columns
	op.alter_column('group_to_graph', 'modified', new_column_name='updated_at', server_default=sa.func.current_timestamp())
	op.add_column('group_to_graph', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.execute('UPDATE "group_to_graph" SET created_at=updated_at')

	# Add new pkey
	op.execute('ALTER TABLE "group_to_graph" ADD PRIMARY KEY (graph_id, group_id);')

	# Create New Index
	op.create_index('group2graph_idx_graph_id_group_id', 'group_to_graph', ['graph_id', 'group_id'], unique=True)

	# Add new foreign key reference

	op.execute('ALTER TABLE group_to_graph ADD CONSTRAINT group_to_graph_group_id_fkey FOREIGN KEY (group_id) REFERENCES "group" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')
	op.execute('ALTER TABLE group_to_graph ADD CONSTRAINT group_to_graph_graph_id_fkey FOREIGN KEY (graph_id) REFERENCES "graph" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')


def downgrade():

	# Remove new foreign key reference
	op.drop_constraint('group_to_graph_group_id_fkey', 'group_to_graph', type_='foreignkey')
	op.drop_constraint('group_to_graph_graph_id_fkey', 'group_to_graph', type_='foreignkey')

	# Drop New Index
	op.drop_index('group2graph_idx_graph_id_group_id', 'group_to_graph')

	# Drop date columns
	op.alter_column('group_to_graph', 'updated_at', new_column_name='modified', server_default=sa.func.current_timestamp())
	op.drop_column('group_to_graph', 'created_at')

	# Replacing graph id with graph_id, user_id.
	op.alter_column('group_to_graph', 'graph_id', new_column_name='old_graph_id')
	op.add_column('group_to_graph', sa.Column('graph_id', sa.String))
	op.add_column('group_to_graph', sa.Column('user_id', sa.String))
	op.execute('UPDATE "group_to_graph" SET graph_id=g.name FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.execute('UPDATE "group_to_graph" SET user_id=g.owner_email FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.drop_column('group_to_graph', 'old_graph_id')
	op.alter_column('group_to_graph', 'graph_id', nullable=False)
	op.alter_column('group_to_graph', 'user_id', nullable=False)

	# Replacing group id with group_id, owner_id .
	op.alter_column('group_to_graph', 'group_id', new_column_name='old_group_id')
	op.add_column('group_to_graph', sa.Column('group_id', sa.String))
	op.add_column('group_to_graph', sa.Column('group_owner', sa.String))
	op.execute('UPDATE "group_to_graph" SET group_id=g.group_id FROM "group" AS g WHERE g.id = old_group_id;')
	op.execute('UPDATE "group_to_graph" SET group_owner=g.owner_email FROM "group" AS g WHERE g.id = old_group_id;')
	op.drop_column('group_to_graph', 'old_group_id')
	op.alter_column('group_to_graph', 'group_id', nullable=False)
	op.alter_column('group_to_graph', 'group_owner', nullable=False)

	# Reinstate OLD PKey
	op.execute('ALTER TABLE "group_to_graph" ADD PRIMARY KEY (group_id, group_owner, graph_id, user_id);')


	pass