"""update graph to tag table

Revision ID: 5ce0f29c368b
Revises: 636c6db82f8f
Create Date: 2017-02-13 22:36:11.914839

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ce0f29c368b'
down_revision = '636c6db82f8f'
branch_labels = None
depends_on = None


def upgrade():
	# Drop OLD PKey
	op.drop_constraint('graph_to_tag_pkey', 'graph_to_tag', type_='primary')

	# Replacing graph_id, user_id. with graph id in graph_to_tag table
	op.alter_column('graph_to_tag', 'graph_id', new_column_name='old_graph_id')
	op.add_column('graph_to_tag', sa.Column('graph_id', sa.Integer))
	op.execute('UPDATE graph_to_tag SET graph_id=g.id FROM "graph" AS g WHERE g.name = graph_to_tag.old_graph_id AND g.owner_email = graph_to_tag.user_id;')
	op.drop_column('graph_to_tag', 'old_graph_id')
	op.drop_column('graph_to_tag', 'user_id')
	op.alter_column('graph_to_tag', 'graph_id', nullable=False)

	# Replacing tag_id with tag id in graph_to_tag table
	op.alter_column('graph_to_tag', 'tag_id', new_column_name='old_tag_id')
	op.add_column('graph_to_tag', sa.Column('tag_id', sa.Integer))
	op.execute('UPDATE graph_to_tag SET tag_id=graph_tag.id FROM graph_tag WHERE graph_tag.name = old_tag_id;')
	op.drop_column('graph_to_tag', 'old_tag_id')
	op.alter_column('graph_to_tag', 'tag_id', nullable=False)


	# Add date columns
	op.add_column('graph_to_tag', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.add_column('graph_to_tag', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))

	# Add new pkey
	op.execute('ALTER TABLE "graph_to_tag" ADD PRIMARY KEY (graph_id, tag_id);')

	# Create New Index
	op.create_index('graph2tag_idx_graph_id_tag_id', 'graph_to_tag', ['graph_id', 'tag_id'], unique=True)

	# Add new foreign key reference
	op.execute('ALTER TABLE graph_to_tag ADD CONSTRAINT graph_to_tag_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES "graph_tag" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')
	op.execute('ALTER TABLE graph_to_tag ADD CONSTRAINT graph_to_tag_graph_id_fkey FOREIGN KEY (graph_id) REFERENCES "graph" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')



def downgrade():

	# Remove new foreign key reference
	op.drop_constraint('graph_to_tag_tag_id_fkey', 'graph_to_tag', type_='foreignkey')
	op.drop_constraint('graph_to_tag_graph_id_fkey', 'graph_to_tag', type_='foreignkey')

	# Drop New Index
	op.drop_index('graph2tag_idx_graph_id_tag_id', 'graph_to_tag')

	# Drop date columns
	op.drop_column('graph_to_tag', 'created_at')
	op.drop_column('graph_to_tag', 'updated_at')

	# Replacing tag_id with tag name in graph_to_tag table
	op.alter_column('graph_to_tag', 'tag_id', new_column_name='old_tag_id')
	op.add_column('graph_to_tag', sa.Column('tag_id', sa.String))
	op.execute('UPDATE graph_to_tag SET tag_id=graph_tag.name FROM graph_tag WHERE graph_tag.id = old_tag_id;')
	op.drop_column('graph_to_tag', 'old_tag_id')
	op.alter_column('graph_to_tag', 'tag_id', nullable=False)

	# Replacing graph id with graph_id, user_id .
	op.alter_column('graph_to_tag', 'graph_id', new_column_name='old_graph_id')
	op.add_column('graph_to_tag', sa.Column('graph_id', sa.String))
	op.add_column('graph_to_tag', sa.Column('user_id', sa.String))
	op.execute('UPDATE "graph_to_tag" SET graph_id=g.name FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.execute('UPDATE "graph_to_tag" SET user_id=g.owner_email FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.drop_column('graph_to_tag', 'old_graph_id')
	op.alter_column('graph_to_tag', 'graph_id', nullable=False)
	op.alter_column('graph_to_tag', 'user_id', nullable=False)

	# Reinstate OLD PKey
	op.execute('ALTER TABLE "graph_to_tag" ADD PRIMARY KEY (graph_id, user_id, tag_id);')

	pass
