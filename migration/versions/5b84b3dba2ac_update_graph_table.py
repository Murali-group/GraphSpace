"""update graph table

Revision ID: 5b84b3dba2ac
Revises: f23f72f7eba0
Create Date: 2017-02-13 21:18:31.034482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b84b3dba2ac'
down_revision = 'f23f72f7eba0'
branch_labels = None
depends_on = None


def upgrade():
	# Drop OLD PKey
	op.drop_constraint('graph_pkey', 'graph', type_='primary')

	# Add new ID Column
	op.execute('ALTER TABLE "graph" ADD "id" SERIAL PRIMARY KEY UNIQUE;')

	# Add date columns
	op.alter_column('graph', 'created', new_column_name='created_at', server_default=sa.func.current_timestamp())
	op.alter_column('graph', 'modified', new_column_name='updated_at', server_default=sa.func.current_timestamp())

	# Rename public column
	op.execute('UPDATE "graph" SET public=0 WHERE public is NULL')
	op.alter_column('graph', 'public', new_column_name='is_public', nullable=False)

	# drop shared_with_groups column
	op.drop_column('graph', 'shared_with_groups')

	# Rename graph_id column
	op.alter_column('graph', 'graph_id', new_column_name='name')

	# Rename email column
	op.alter_column('graph', 'user_id', new_column_name='owner_email')

	# Create New Index
	op.create_index('_graph_uc_name_owner_email', 'graph', ['name', 'owner_email'], unique=True)

	# Add new foreign key reference
	op.execute('ALTER TABLE "graph" ADD CONSTRAINT graph_owner_email_fkey FOREIGN KEY ("owner_email") REFERENCES "user" (email) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')


def downgrade():

	# Remove new foreign key reference
	op.drop_constraint('graph_owner_email_fkey', 'graph', type_='foreignkey')

	# Drop New Index
	op.drop_index('_graph_uc_name_owner_email', 'graph')

	# Rename email column
	op.alter_column('graph', 'owner_email', new_column_name='user_id')

	# Rename graph_id column
	op.alter_column('graph', 'name', new_column_name='graph_id')

	# Undrop shared_with_groups column
	op.add_column('graph', sa.Column('shared_with_groups', sa.Integer))

	# Rename public column
	op.alter_column('graph', 'is_public', new_column_name='public', nullable=None)

	# Drop date columns
	op.alter_column('graph', 'created_at', new_column_name='created', server_default=sa.func.current_timestamp())
	op.alter_column('graph', 'updated_at', new_column_name='modified', server_default=sa.func.current_timestamp())

	# Drop new ID Column
	op.drop_column('graph', 'id')

	# Reinstate OLD PKey
	op.create_primary_key("graph_pkey", "graph", ["graph_id", "user_id" ])

	pass