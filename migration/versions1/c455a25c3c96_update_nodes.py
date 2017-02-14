"""update nodes

Revision ID: c455a25c3c96
Revises: 
Create Date: 2017-02-12 17:54:18.951849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c455a25c3c96'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
	# op.alter_column('user', 'admin', new_column_name='is_admin')
	# op.execute('UPDATE "user" SET is_admin=0 WHERE is_admin is NULL')
	# op.alter_column('user', 'is_admin', nullable=False)
	#
	# op.alter_column('user', 'user_id', new_column_name='email')
	# op.create_index('ix_user_email', 'user', ['email'], unique=True)
	#
	# # password_reset_code
	# op.rename_table('password_reset', 'password_reset_code')
	# op.alter_column('password_reset_code', 'user_id', new_column_name='email')
	# op.alter_column('password_reset_code', 'created', new_column_name='created_at', server_default=sa.func.current_timestamp())
	# op.add_column('password_reset_code', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	# op.execute('ALTER TABLE "password_reset_code" ADD CONSTRAINT password_reset_code_email_fkey FOREIGN KEY (email) REFERENCES "user" (email) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.create_index('ix_password_reset_code_email_code', 'password_reset_code', ['email', 'code'], unique=True)
	# op.create_index('ix_password_reset_code_email', 'password_reset_code', ['email'])
	#
	# # Add id column to graph table
	# op.add_column('group', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	# op.add_column('group', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	#
	# op.drop_constraint('group_to_graph_group_id_fkey', 'group_to_graph', type_='foreignkey')
	# op.drop_constraint('group_to_user_group_id_fkey', 'group_to_user', type_='foreignkey')
	# op.drop_constraint('group_pkey', 'group', type_='primary')
	# op.execute('ALTER TABLE "group" ADD id SERIAL PRIMARY KEY UNIQUE;')
	#
	# # Add id column to graph table
	# op.drop_constraint('group_to_graph_graph_id_fkey', 'group_to_graph', type_='foreignkey')
	# op.drop_constraint('node_user_id_fkey1', 'node', type_='foreignkey')
	# op.drop_constraint('graph_to_tag_graph_id_fkey', 'graph_to_tag', type_='foreignkey')
	# op.drop_constraint('layout_graph_id_fkey', 'layout', type_='foreignkey')
	# op.drop_constraint('graph_pkey', 'graph', type_='primary')
	# op.execute('ALTER TABLE "graph" ADD id SERIAL PRIMARY KEY UNIQUE;')
	#
	# # Update group_to_graph before replacing redundant columns (group_id, owner_id) with group id.
	#
	# # Replacing group_id, owner_id with group id.
	# op.alter_column('group_to_graph', 'group_id', new_column_name='old_group_id')
	# op.add_column('group_to_graph', sa.Column('group_id', sa.Integer))
	# op.execute('UPDATE group_to_graph SET group_id=g.id FROM "group" AS g WHERE g.group_id = old_group_id AND g.owner_id = group_owner;')
	# op.drop_column('group_to_graph', 'old_group_id')
	# op.drop_column('group_to_graph', 'group_owner')
	# op.alter_column('group_to_graph', 'group_id', nullable=False)
	#
	# # Replacing graph_id, user_id. with graph id in group_to_graph table
	# op.alter_column('group_to_graph', 'graph_id', new_column_name='old_graph_id')
	# op.add_column('group_to_graph', sa.Column('graph_id', sa.Integer))
	# op.execute('UPDATE group_to_graph g2g SET graph_id=g.id FROM "graph" AS g WHERE g.graph_id = g2g.old_graph_id AND g.user_id = g2g.user_id;')
	# op.drop_column('group_to_graph', 'old_graph_id')
	# op.drop_column('group_to_graph', 'user_id')
	# op.alter_column('group_to_graph', 'graph_id', nullable=False)
	#
	# # Update date columns in group_to_graph
	# op.alter_column('group_to_graph', 'modified', new_column_name='updated_at', server_default=sa.func.current_timestamp())
	# op.add_column('group_to_graph', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	# op.execute('UPDATE "group_to_graph" SET created_at=updated_at')
	#
	# # Update columns in graph table
	# # op.alter_column('graph', 'created', new_column_name='created_at', server_default=sa.func.current_timestamp())
	# # op.alter_column('graph', 'modified', new_column_name='updated_at', server_default=sa.func.current_timestamp())
	# op.alter_column('graph', 'graph_id', new_column_name='name')
	# op.alter_column('graph', 'user_id', new_column_name='owner_email')
	# op.execute('UPDATE "graph" SET public=0 WHERE public is NULL')
	# op.alter_column('graph', 'public', new_column_name='is_public', nullable=False)
	# op.drop_column('graph', 'shared_with_groups')
	#
	# # Update graph_tag table
	# # op.drop_constraint('graph_to_tag_tag_id_fkey', 'graph_to_tag', type_='foreignkey')
	# op.drop_constraint('graph_tag_pkey', 'graph_tag', type_='primary')
	# op.add_column('graph_tag', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	# op.add_column('graph_tag', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	# op.execute('ALTER TABLE "graph_tag" ADD id SERIAL PRIMARY KEY UNIQUE;')
	# op.alter_column('graph_tag', 'tag_id', new_column_name='name')
	#
	# # Replacing graph_id, user_id. with graph id in graph_to_tag table
	# op.alter_column('graph_to_tag', 'graph_id', new_column_name='old_graph_id')
	# op.add_column('graph_to_tag', sa.Column('graph_id', sa.Integer))
	# op.execute('UPDATE graph_to_tag SET graph_id=g.id FROM "graph" AS g WHERE g.name = graph_to_tag.old_graph_id AND g.owner_email = graph_to_tag.user_id;')
	# op.drop_column('graph_to_tag', 'old_graph_id')
	# op.drop_column('graph_to_tag', 'user_id')
	# op.alter_column('graph_to_tag', 'graph_id', nullable=False)
	#
	# # Replacing tag_id with tag id in graph_to_tag table
	# op.alter_column('graph_to_tag', 'tag_id', new_column_name='old_tag_id')
	# op.add_column('graph_to_tag', sa.Column('tag_id', sa.Integer))
	# op.execute('UPDATE graph_to_tag SET tag_id=graph_tag.id FROM graph_tag WHERE graph_tag.name = old_tag_id;')
	# op.drop_column('graph_to_tag', 'old_tag_id')
	# op.alter_column('graph_to_tag', 'tag_id', nullable=False)
	#
	# op.add_column('graph_to_tag', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	# op.add_column('graph_to_tag', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	#
	#
	# # Update group_to_user before replacing redundant columns (group_id, group_owner) with group id.
	# op.drop_constraint('group_to_user_pkey', 'group_to_user', type_='primary')
	# # Adding timestamp columns
	# op.add_column('group_to_user', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	# op.add_column('group_to_user', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	# # Replacing group id column
	# op.alter_column('group_to_user', 'group_id', new_column_name='old_group_id')
	# op.add_column('group_to_user', sa.Column('group_id', sa.Integer))
	# op.execute('UPDATE group_to_user SET group_id=g.id FROM "group" AS g WHERE g.group_id = group_to_user.old_group_id AND g.owner_id = group_to_user.group_owner;')
	# op.drop_column('group_to_user', 'old_group_id')
	# op.drop_column('group_to_user', 'group_owner')
	# op.alter_column('group_to_user', 'group_id', nullable=False)
	# # Replacing user id column
	# op.alter_column('group_to_user', 'user_id', new_column_name='old_user_id')
	# op.add_column('group_to_user', sa.Column('user_id', sa.Integer))
	# op.execute('UPDATE group_to_user SET user_id=u.id FROM "user" AS u WHERE u.email = group_to_user.old_user_id;')
	# op.drop_column('group_to_user', 'old_user_id')
	# op.alter_column('group_to_user', 'user_id', nullable=False)
	#
	# op.execute('ALTER TABLE "group_to_user" ADD PRIMARY KEY (user_id, group_id);')
	#
	# # Update group table
	# op.drop_column('group', 'group_id')
	# op.alter_column('group', 'owner_id', new_column_name='owner_email')
	#
	#
	#
	# # Update node table
	#
	# # op.drop_index('node_idx_graph_id_user_id', 'node')
	# # op.drop_index('node_index_node_id_graph_id', 'node')
	# # op.drop_index('node_index_label_graph_id', 'node')
	# # op.drop_index('node_index_node_id', 'node')
	# # op.drop_index('node_index_label', 'node')
	#
	# op.drop_constraint('edge_user_id_fkey1', 'edge', type_='foreignkey')
	# op.drop_constraint('edge_user_id_fkey2', 'edge', type_='foreignkey')
	# op.drop_constraint('node_pkey', 'node', type_='primary')
	# op.execute('ALTER TABLE "node" ADD id SERIAL PRIMARY KEY UNIQUE;')
	#
	# op.alter_column('node', 'modified', new_column_name='updated_at', server_default=sa.func.current_timestamp())
	# op.add_column('node', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	# op.execute('UPDATE "node" SET created_at=updated_at')
	#
	# op.alter_column('node', 'node_id', new_column_name='name')
	#
	# # # Replacing graph_id, user_id. with graph id in node table
	# op.alter_column('node', 'graph_id', new_column_name='old_graph_id')
	# op.add_column('node', sa.Column('graph_id', sa.Integer))
	# op.execute('UPDATE node SET graph_id=g.id FROM "graph" AS g WHERE g.name = node.old_graph_id AND g.owner_email = node.user_id;')
	# op.drop_column('node', 'old_graph_id')
	# op.drop_column('node', 'user_id')
	# op.alter_column('node', 'graph_id', nullable=False)
	#
	# # Add new foreign keys
	#
	# # Create new indices
	# # op.create_index('ix_graph_id', 'graph', ['id'], unique=True)
	# # op.create_index('_graph_uc_name_owner_email', 'graph', ['name', 'owner_email'], unique=True)

	pass



def downgrade():
	# Drop new indices
	# op.drop_index('ix_graph_id', 'graph')
	# op.drop_index('_graph_uc_name_owner_email', 'graph')

	# Remove new foreign keys

	# # Update node table
	# op.drop_column('node', 'id')
	# op.alter_column('node', 'updated_at', new_column_name='modified', server_default=sa.func.current_timestamp())
	# op.drop_column('node', 'created_at')
	# op.alter_column('node', 'name', new_column_name='node_id')
	#
	# # # Undo Replacing graph_id, user_id. with graph id in node table
	# op.alter_column('node', 'graph_id', new_column_name='old_graph_id')
	# op.add_column('node', sa.Column('graph_id', sa.String))
	# op.add_column('node', sa.Column('user_id', sa.String))
	# op.execute('UPDATE "node" SET graph_id=g.name FROM "graph" AS g WHERE g.id = old_graph_id;')
	# op.execute('UPDATE "node" SET user_id=g.owner_email FROM "graph" AS g WHERE g.id = old_graph_id;')
	# op.drop_column('node', 'old_graph_id')
	# op.alter_column('node', 'graph_id', nullable=False)
	# op.alter_column('node', 'user_id', nullable=False)
	#
	# op.execute('ALTER TABLE "node" ADD PRIMARY KEY (node_id, user_id, graph_id);')
	# op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_user_id_fkey1 FOREIGN KEY (user_id, graph_id, head_node_id) REFERENCES node (user_id, graph_id, node_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_user_id_fkey2 FOREIGN KEY (user_id, graph_id, tail_node_id) REFERENCES node (user_id, graph_id, node_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	#
	# # ReUpdate group table
	#
	# op.add_column('group', sa.Column('group_id', sa.String))
	# op.alter_column('group', 'owner_email', new_column_name='owner_id')
	# op.execute('UPDATE "group" SET group_id=name;')
	# op.alter_column('group', 'group_id', nullable=False)
	#
	# # Reupdate group_to_user table
	# # Removing timestamp columns
	# op.drop_column('group_to_user', 'created_at')
	# op.drop_column('group_to_user', 'updated_at')
	# # Replacing group id column
	# op.alter_column('group_to_user', 'group_id', new_column_name='old_group_id')
	# op.add_column('group_to_user', sa.Column('group_id', sa.String))
	# op.add_column('group_to_user', sa.Column('group_owner', sa.String))
	# op.execute('UPDATE "group_to_user" SET group_id=g.name FROM "group" AS g WHERE g.id = old_group_id;')
	# op.execute('UPDATE "group_to_user" SET group_owner=g.owner_id FROM "group" AS g WHERE g.id = old_group_id;')
	# op.drop_column('group_to_user', 'old_group_id')
	# op.alter_column('group_to_user', 'group_id', nullable=False)
	# op.alter_column('group_to_user', 'group_owner', nullable=False)
	# # Replacing user id column
	# op.alter_column('group_to_user', 'user_id', new_column_name='old_user_id')
	# op.add_column('group_to_user', sa.Column('user_id', sa.String))
	# op.execute('UPDATE "group_to_user" SET user_id=u.email FROM "user" AS u WHERE u.id = group_to_user.old_user_id;')
	# op.drop_column('group_to_user', 'old_user_id')
	# op.alter_column('group_to_user', 'user_id', nullable=False)
	#
	# op.execute('ALTER TABLE "group_to_user" ADD PRIMARY KEY (user_id, group_id, group_owner);')
	#
	#
	# # Replacing tag_id with tag name in graph_to_tag table
	# op.alter_column('graph_to_tag', 'tag_id', new_column_name='old_tag_id')
	# op.add_column('graph_to_tag', sa.Column('tag_id', sa.String))
	# op.execute('UPDATE graph_to_tag SET tag_id=graph_tag.name FROM graph_tag WHERE graph_tag.id = old_tag_id;')
	# op.drop_column('graph_to_tag', 'old_tag_id')
	# op.alter_column('graph_to_tag', 'tag_id', nullable=False)
	#
	# # Removing timestamp columns
	# op.drop_column('graph_to_tag', 'created_at')
	# op.drop_column('graph_to_tag', 'updated_at')
	#
	#
	#
	# # Reupdate graph_tag table
	# op.drop_column('graph_tag', 'created_at')
	# op.drop_column('graph_tag', 'updated_at')
	# op.drop_column('graph_tag', 'id')
	# op.alter_column('graph_tag', 'name', new_column_name='tag_id')
	# op.execute('ALTER TABLE "graph_tag" ADD PRIMARY KEY (tag_id);')
	#
	# op.alter_column('graph_to_tag', 'graph_id', new_column_name='old_graph_id')
	# op.add_column('graph_to_tag', sa.Column('graph_id', sa.String))
	# op.add_column('graph_to_tag', sa.Column('user_id', sa.String))
	# op.execute('UPDATE "graph_to_tag" SET graph_id=g.name FROM "graph" AS g WHERE g.id = old_graph_id;')
	# op.execute('UPDATE "graph_to_tag" SET user_id=g.owner_email FROM "graph" AS g WHERE g.id = old_graph_id;')
	# op.drop_column('graph_to_tag', 'old_graph_id')
	# op.alter_column('graph_to_tag', 'graph_id', nullable=False)
	# op.alter_column('graph_to_tag', 'user_id', nullable=False)
	#
	# # Reupdate columns in graph table
	# # op.alter_column('graph', 'created_at', new_column_name='created', server_default=sa.func.current_timestamp())
	# # op.alter_column('graph', 'updated_at', new_column_name='modified', server_default=sa.func.current_timestamp())
	# op.alter_column('graph', 'name', new_column_name='graph_id')
	# op.alter_column('graph', 'owner_email', new_column_name='user_id')
	# op.alter_column('graph', 'is_public', new_column_name='public', nullable=None)
	# op.add_column('graph', sa.Column('shared_with_groups', sa.Integer))
	#
	# # op.execute('ALTER TABLE "graph_to_tag" ADD CONSTRAINT graph_to_tag_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES "tag" (tag_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	#
	#
	# # ReUpdate date columns in group_to_graph
	# op.alter_column('group_to_graph', 'updated_at', new_column_name='modified', server_default=sa.func.current_timestamp())
	# op.drop_column('group_to_graph', 'created_at')
	#
	# # Replacing graph id with graph_id, user_id.
	# op.alter_column('group_to_graph', 'graph_id', new_column_name='old_graph_id')
	# op.add_column('group_to_graph', sa.Column('graph_id', sa.String))
	# op.add_column('group_to_graph', sa.Column('user_id', sa.String))
	# op.execute('UPDATE "group_to_graph" SET graph_id=g.graph_id FROM "graph" AS g WHERE g.id = old_graph_id;')
	# op.execute('UPDATE "group_to_graph" SET user_id=g.user_id FROM "graph" AS g WHERE g.id = old_graph_id;')
	# op.drop_column('group_to_graph', 'old_graph_id')
	# op.alter_column('group_to_graph', 'graph_id', nullable=False)
	# op.alter_column('group_to_graph', 'user_id', nullable=False)
	#
	# # Replacing group id with group_id, owner_id .
	# op.alter_column('group_to_graph', 'group_id', new_column_name='old_group_id')
	# op.add_column('group_to_graph', sa.Column('group_id', sa.String))
	# op.add_column('group_to_graph', sa.Column('group_owner', sa.String))
	# op.execute('UPDATE "group_to_graph" SET group_id=g.group_id FROM "group" AS g WHERE g.id = old_group_id;')
	# op.execute('UPDATE "group_to_graph" SET group_owner=g.owner_id FROM "group" AS g WHERE g.id = old_group_id;')
	# op.drop_column('group_to_graph', 'old_group_id')
	# op.alter_column('group_to_graph', 'group_id', nullable=False)
	# op.alter_column('group_to_graph', 'group_owner', nullable=False)
	#
	# op.execute('ALTER TABLE "group_to_graph" ADD PRIMARY KEY (graph_id, user_id, group_id, group_owner);')
	#
	# op.drop_column('graph', 'id')
	# op.execute('ALTER TABLE "graph" ADD PRIMARY KEY (graph_id, user_id);')
	# op.execute('ALTER TABLE "group_to_graph" ADD CONSTRAINT group_to_graph_graph_id_fkey FOREIGN KEY (graph_id, user_id) REFERENCES "graph" (graph_id, user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.execute('ALTER TABLE "node" ADD CONSTRAINT node_user_id_fkey1 FOREIGN KEY (graph_id, user_id) REFERENCES "graph" (graph_id, user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.execute('ALTER TABLE "graph_to_tag" ADD CONSTRAINT graph_to_tag_graph_id_fkey FOREIGN KEY (graph_id, user_id) REFERENCES "graph" (graph_id, user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.execute('ALTER TABLE "layout" ADD CONSTRAINT layout_graph_id_fkey FOREIGN KEY (graph_id, user_id) REFERENCES "graph" (graph_id, user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	#
	# # ReUpdate group table
	#
	# op.drop_column('group', 'created_at')
	# op.drop_column('group', 'updated_at')
	# op.drop_column('group', 'id')
	#
	# op.execute('ALTER TABLE "group" ADD PRIMARY KEY (group_id, owner_id);')
	# op.execute('ALTER TABLE "group_to_graph" ADD CONSTRAINT group_to_graph_group_id_fkey FOREIGN KEY (group_id, group_owner) REFERENCES "group" (group_id, owner_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.execute('ALTER TABLE "group_to_user" ADD CONSTRAINT group_to_user_group_id_fkey FOREIGN KEY (group_id, group_owner) REFERENCES "group" (group_id, owner_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	#
	# op.rename_table('password_reset_code', 'password_reset')
	# op.alter_column('password_reset', 'email', new_column_name='user_id', )
	# op.alter_column('password_reset', 'created_at', new_column_name='created', server_default=None)
	# op.drop_column('password_reset', 'updated_at')
	# op.drop_constraint('password_reset_code_email_fkey', 'password_reset', type_='foreignkey')
	# op.drop_index('ix_password_reset_code_email_code', 'password_reset')
	# op.drop_index('ix_password_reset_code_email', 'password_reset')
	#
	# op.alter_column('user', 'is_admin', new_column_name='admin')
	# op.alter_column('user', 'email', new_column_name='user_id')
	# op.drop_index('ix_user_email', 'user')
	pass