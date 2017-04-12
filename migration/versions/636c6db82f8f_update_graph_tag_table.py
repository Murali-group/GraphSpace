"""update graph tag table

Revision ID: 636c6db82f8f
Revises: 0ddbd8cc99c2
Create Date: 2017-02-13 22:30:49.933548

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '636c6db82f8f'
down_revision = '0ddbd8cc99c2'
branch_labels = None
depends_on = None



def upgrade():
	# Update graph_tag table

	# Drop OLD PKey
	op.drop_constraint('graph_tag_pkey', 'graph_tag', type_='primary')

	# Add new ID Column
	op.execute('ALTER TABLE "graph_tag" ADD "id" SERIAL PRIMARY KEY UNIQUE;')

	# Add date columns
	op.add_column('graph_tag', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.add_column('graph_tag', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))

	# Rename tag column
	op.alter_column('graph_tag', 'tag_id', new_column_name='name')

	# Create New Index
	op.create_index('graph_tag_name_key', 'graph_tag', ['name',], unique=True)


def downgrade():

	# Drop New Index
	op.drop_index('graph_tag_name_key', 'graph_tag')

	# Rename tag column
	op.alter_column('graph_tag', 'name', new_column_name='tag_id')

	# Drop date columns
	op.drop_column('graph_tag', 'created_at')
	op.drop_column('graph_tag', 'updated_at')

	# Drop new ID Column
	op.drop_column('graph_tag', 'id')

	# Reinstate OLD PKey
	op.execute('ALTER TABLE "graph_tag" ADD PRIMARY KEY (tag_id);')

	pass