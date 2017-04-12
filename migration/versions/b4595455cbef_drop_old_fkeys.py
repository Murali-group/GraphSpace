"""drop old fkeys

Revision ID: b4595455cbef
Revises: 9606b385e5a1
Create Date: 2017-02-13 15:45:45.189552

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4595455cbef'
down_revision = '9606b385e5a1'
branch_labels = None
depends_on = None


def upgrade():
	# password_reset
	op.drop_constraint('password_reset_user_id_fkey', 'password_reset', type_='foreignkey')

	# group
	op.drop_constraint('group_owner_id_fkey', 'group', type_='foreignkey')

	# graph
	op.drop_constraint('graph_user_id_fkey', 'graph', type_='foreignkey')

	# node
	op.drop_constraint('node_user_id_fkey', 'node', type_='foreignkey')
	op.drop_constraint('node_user_id_fkey1', 'node', type_='foreignkey')

	# edge
	op.drop_constraint('edge_user_id_fkey1', 'edge', type_='foreignkey')
	op.drop_constraint('edge_user_id_fkey2', 'edge', type_='foreignkey')
	op.drop_constraint('edge_user_id_fkey', 'edge', type_='foreignkey')

	# graph_to_tag
	op.drop_constraint('graph_to_tag_user_id_fkey', 'graph_to_tag', type_='foreignkey')
	op.drop_constraint('graph_to_tag_graph_id_fkey', 'graph_to_tag', type_='foreignkey')
	op.drop_constraint('graph_to_tag_tag_id_fkey', 'graph_to_tag', type_='foreignkey')

	# group_to_graph
	op.drop_constraint('group_to_graph_user_id_fkey', 'group_to_graph', type_='foreignkey')
	op.drop_constraint('group_to_graph_group_owner_fkey', 'group_to_graph', type_='foreignkey')
	op.drop_constraint('group_to_graph_group_id_fkey', 'group_to_graph', type_='foreignkey')
	op.drop_constraint('group_to_graph_graph_id_fkey', 'group_to_graph', type_='foreignkey')

	# group_to_user
	op.drop_constraint('group_to_user_user_id_fkey', 'group_to_user', type_='foreignkey')
	op.drop_constraint('group_to_user_group_owner_fkey', 'group_to_user', type_='foreignkey')
	op.drop_constraint('group_to_user_group_id_fkey', 'group_to_user', type_='foreignkey')

	# layout
	op.drop_constraint('layout_user_id_fkey', 'layout', type_='foreignkey')
	op.drop_constraint('layout_owner_id_fkey', 'layout', type_='foreignkey')
	op.drop_constraint('layout_graph_id_fkey', 'layout', type_='foreignkey')
	pass


def downgrade():
	# # password_reset
	# op.execute('ALTER TABLE "password_reset" ADD CONSTRAINT password_reset_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user" (user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	#
	# # group
	# op.execute('ALTER TABLE "group" ADD CONSTRAINT group_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES "user" (user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	#
	# # graph
	# op.execute('ALTER TABLE "graph" ADD CONSTRAINT graph_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user" (user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	#
	# # node
	# op.execute('ALTER TABLE "node" ADD CONSTRAINT node_graph_id_fkey FOREIGN KEY (graph_id, user_id) REFERENCES graph (graph_id, user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	#
	# # edge
	# op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_graph_id_fkey FOREIGN KEY (graph_id, user_id) REFERENCES graph (graph_id, user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_head_node_id_fkey FOREIGN KEY (graph_id, user_id, head_node_id) REFERENCES node (graph_id, user_id, node_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_tail_node_id_fkey FOREIGN KEY (graph_id, user_id, head_node_id) REFERENCES node (graph_id, user_id, node_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	#
	# # graph_to_tag
	# op.execute('ALTER TABLE "graph_to_tag" ADD CONSTRAINT graph_to_tag_graph_id_fkey FOREIGN KEY (graph_id, user_id) REFERENCES "graph" (graph_id, user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.execute('ALTER TABLE "graph_to_tag" ADD CONSTRAINT graph_to_tag_graph_id_fkey FOREIGN KEY (tag_id) REFERENCES "graph_tag" (tag_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	#
	# # group_to_graph
	# op.execute('ALTER TABLE "group_to_graph" ADD CONSTRAINT group_to_graph_graph_id_fkey FOREIGN KEY (graph_id, user_id) REFERENCES "graph" (graph_id, user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.execute('ALTER TABLE "group_to_graph" ADD CONSTRAINT group_to_graph_group_id_fkey FOREIGN KEY (group_id, group_owner) REFERENCES "group" (group_id, owner_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	#
	# # group_to_user
	# op.execute('ALTER TABLE "group_to_user" ADD CONSTRAINT group_to_user_group_id_fkey FOREIGN KEY (group_id, group_owner) REFERENCES "group" (group_id, owner_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.execute('ALTER TABLE "group_to_user" ADD CONSTRAINT group_to_user_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user" (user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	#
	# # layout
	# op.execute('ALTER TABLE "layout" ADD CONSTRAINT layout_graph_id_fkey FOREIGN KEY (graph_id, user_id) REFERENCES "graph" (graph_id, user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	# op.execute('ALTER TABLE "layout" ADD CONSTRAINT layout_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES "user" (user_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	pass


