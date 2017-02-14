"""update layouts

Revision ID: 827d5908fd78
Revises: fb02ac7f9da4
Create Date: 2017-02-13 13:20:45.610808

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '827d5908fd78'
down_revision = 'fb02ac7f9da4'
branch_labels = None
depends_on = None


def upgrade():
	op.alter_column('layout', 'layout_id', new_column_name='id')
	op.alter_column('layout', 'layout_name', new_column_name='name')
	op.alter_column('layout', 'owner_id', new_column_name='owner_email')
	op.execute('UPDATE layout SET shared_with_groups=0  WHERE shared_with_groups IS NULL;')
	op.alter_column('layout', 'shared_with_groups', new_column_name='is_shared', nullable=False)
	op.drop_column('layout', 'times_modified')
	op.drop_column('layout', 'public')
	op.add_column('layout', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.add_column('layout', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))

	# # # Replacing graph_id, user_id. with graph id in layout table
	op.alter_column('layout', 'graph_id', new_column_name='old_graph_id')
	op.add_column('layout', sa.Column('graph_id', sa.Integer))
	op.execute('UPDATE layout SET graph_id=g.id FROM "graph" AS g WHERE g.name = layout.old_graph_id AND g.owner_email = layout.user_id;')
	op.drop_column('layout', 'old_graph_id')
	op.drop_column('layout', 'user_id')
	op.alter_column('layout', 'graph_id', nullable=False)

	op.execute('ALTER TABLE "layout" ADD CONSTRAINT layout_graph_id_fkey FOREIGN KEY (graph_id) REFERENCES graph (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')


def downgrade():
	op.drop_constraint('layout_graph_id_fkey', 'layout', type_='foreignkey')


	# # Undo Replacing graph_id, user_id. with graph id in layout table
	op.alter_column('layout', 'graph_id', new_column_name='old_graph_id')
	op.add_column('layout', sa.Column('graph_id', sa.String))
	op.add_column('layout', sa.Column('user_id', sa.String))
	op.execute('UPDATE "layout" SET graph_id=g.name FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.execute('UPDATE "layout" SET user_id=g.owner_email FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.drop_column('layout', 'old_graph_id')
	op.alter_column('layout', 'graph_id', nullable=False)
	op.alter_column('layout', 'user_id', nullable=False)

	op.drop_column('layout', 'created_at')
	op.drop_column('layout', 'updated_at')

	op.execute('ALTER TABLE layout ADD times_modified INTEGER NOT NULL DEFAULT 0;')
	op.execute('ALTER TABLE layout ADD public INTEGER NOT NULL DEFAULT 0;')
	op.alter_column('layout', 'is_shared', new_column_name='shared_with_groups')
	op.alter_column('layout', 'owner_email', new_column_name='owner_id')
	op.alter_column('layout', 'name', new_column_name='layout_name')
	op.alter_column('layout', 'id', new_column_name='layout_id')
