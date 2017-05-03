"""update group table

Revision ID: bb85d8864dfa
Revises: 3ab443000c7e
Create Date: 2017-02-13 16:06:39.683232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb85d8864dfa'
down_revision = '3ab443000c7e'
branch_labels = None
depends_on = None

# TODO: We are yet to drop the group_id column. This will be dropped after group_to_user and group_to_graph update

def upgrade():
	# Drop OLD PKey
	op.drop_constraint('group_pkey', 'group', type_='primary')

	# Add new ID Column
	op.execute('ALTER TABLE "group" ADD "id" SERIAL PRIMARY KEY UNIQUE;')

	# Add date columns
	op.add_column('group', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.add_column('group', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))

	# Rename email column
	op.alter_column('group', 'owner_id', new_column_name='owner_email')

	op.alter_column('group', 'description', nullable=True)

	# Create New Index
	op.create_index('_group_uc_name_owner_email', 'group', ['name', 'owner_email'], unique=True)

	# Add new foreign key reference
	op.execute('ALTER TABLE "group" ADD CONSTRAINT group_owner_email_fkey FOREIGN KEY ("owner_email") REFERENCES "user" (email) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')


def downgrade():

	# Remove new foreign key reference
	op.drop_constraint('group_owner_email_fkey', 'group', type_='foreignkey')

	# Drop New Index
	op.drop_index('_group_uc_name_owner_email', 'group')

	# Rename email column
	op.alter_column('group', 'owner_email', new_column_name='owner_id')

	# Drop date columns
	op.drop_column('group', 'created_at')
	op.drop_column('group', 'updated_at')

	# Drop new ID Column
	op.drop_column('group', 'id')

	# Reinstate OLD PKey
	op.create_primary_key("group_pkey", "group", ["group_id", "owner_id" ])

	pass


