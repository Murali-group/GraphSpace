"""update layout table

Revision ID: ed8a5d6d9b4a
Revises: 5ce0f29c368b
Create Date: 2017-02-13 22:50:30.224661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed8a5d6d9b4a'
down_revision = '5ce0f29c368b'
branch_labels = None
depends_on = None


def upgrade():
	# Rename layout_id column
	op.alter_column('layout', 'layout_id', new_column_name='id')

	# Rename layout name column
	op.alter_column('layout', 'layout_name', new_column_name='name')

	# Rename email column
	op.alter_column('layout', 'owner_id', new_column_name='owner_email')

	# Rename shared_with_groups column
	op.execute('UPDATE layout SET shared_with_groups=0  WHERE shared_with_groups IS NULL;')
	op.alter_column('layout', 'shared_with_groups', new_column_name='is_shared', nullable=False)

	# Drop times_modified and public column
	op.drop_column('layout', 'times_modified')
	op.drop_column('layout', 'public')

	# Add date columns
	op.add_column('layout', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.add_column('layout', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))

	# Replacing graph_id, user_id. with graph id in layout table
	op.alter_column('layout', 'graph_id', new_column_name='old_graph_id')
	op.add_column('layout', sa.Column('graph_id', sa.Integer))
	op.execute('UPDATE layout SET graph_id=g.id FROM "graph" AS g WHERE g.name = layout.old_graph_id AND g.owner_email = layout.user_id;')
	op.drop_column('layout', 'old_graph_id')
	op.drop_column('layout', 'user_id')
	op.alter_column('layout', 'graph_id', nullable=False)

	# Create New Index
	# It seems there are duplicate layout names for same owner and graph_id. Coz there was no unique constraint on the columns.
	# Solution: Drop one of the duplicate entries.

	op.execute('DELETE FROM layout WHERE ctid NOT IN (SELECT MAX(ctid) FROM layout GROUP BY name, graph_id, owner_email);')
	op.create_index('_layout_uc_name_graph_id_owner_email', 'layout', ['name', 'graph_id', 'owner_email'], unique=True)

	# Add new foreign key reference
	op.execute('ALTER TABLE "layout" ADD CONSTRAINT layout_graph_id_fkey FOREIGN KEY (graph_id) REFERENCES graph (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')


def downgrade():
	# Remove new foreign key reference
	op.drop_constraint('layout_graph_id_fkey', 'layout', type_='foreignkey')

	# Drop New Index
	op.drop_index('_layout_uc_name_graph_id_owner_email', 'layout')

	# # Undo Replacing graph_id, user_id. with graph id in layout table
	op.alter_column('layout', 'graph_id', new_column_name='old_graph_id')
	op.add_column('layout', sa.Column('graph_id', sa.String))
	op.add_column('layout', sa.Column('user_id', sa.String))
	op.execute('UPDATE "layout" SET graph_id=g.name FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.execute('UPDATE "layout" SET user_id=g.owner_email FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.drop_column('layout', 'old_graph_id')
	op.alter_column('layout', 'graph_id', nullable=False)
	op.alter_column('layout', 'user_id', nullable=False)

	# Drop date columns
	op.drop_column('layout', 'created_at')
	op.drop_column('layout', 'updated_at')

	# Undo Drop times_modified and public column
	op.execute('ALTER TABLE layout ADD times_modified INTEGER NOT NULL DEFAULT 0;')
	op.execute('ALTER TABLE layout ADD public INTEGER NOT NULL DEFAULT 0;')

	# Rename shared_with_groups column
	op.alter_column('layout', 'is_shared', new_column_name='shared_with_groups')

	# Rename email column
	op.alter_column('layout', 'owner_email', new_column_name='owner_id')

	# Rename layout name column
	op.alter_column('layout', 'name', new_column_name='layout_name')

	# Rename layout_id column
	op.alter_column('layout', 'id', new_column_name='layout_id')



