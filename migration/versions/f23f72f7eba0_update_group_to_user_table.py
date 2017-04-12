"""update group to user table

Revision ID: f23f72f7eba0
Revises: bb85d8864dfa
Create Date: 2017-02-13 16:26:20.648610

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f23f72f7eba0'
down_revision = 'bb85d8864dfa'
branch_labels = None
depends_on = None


def upgrade():
	# Drop OLD PKey
	op.drop_constraint('group_to_user_pkey', 'group_to_user', type_='primary')

	# Replacing group id column
	op.alter_column('group_to_user', 'group_id', new_column_name='old_group_id')
	op.add_column('group_to_user', sa.Column('group_id', sa.Integer))
	op.execute('UPDATE group_to_user SET group_id=g.id FROM "group" AS g WHERE g.group_id = group_to_user.old_group_id AND g.owner_email = group_to_user.group_owner;')
	op.drop_column('group_to_user', 'old_group_id')
	op.drop_column('group_to_user', 'group_owner')
	op.alter_column('group_to_user', 'group_id', nullable=False)

	# Replacing user id column
	op.alter_column('group_to_user', 'user_id', new_column_name='old_user_id')
	op.add_column('group_to_user', sa.Column('user_id', sa.Integer))
	op.execute('UPDATE group_to_user SET user_id=u.id FROM "user" AS u WHERE u.email = group_to_user.old_user_id;')
	op.drop_column('group_to_user', 'old_user_id')
	op.alter_column('group_to_user', 'user_id', nullable=False)

	# Add date columns
	op.add_column('group_to_user', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.add_column('group_to_user', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))

	# Add new pkey
	op.execute('ALTER TABLE "group_to_user" ADD PRIMARY KEY (user_id, group_id);')

	# Create New Index
	op.create_index('group2user_idx_user_id_group_id', 'group_to_user', ['user_id', 'group_id'], unique=True)

	# Add new foreign key reference

	op.execute('ALTER TABLE group_to_user ADD CONSTRAINT group_to_user_group_id_fkey FOREIGN KEY (group_id) REFERENCES "group" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')
	op.execute('ALTER TABLE group_to_user ADD CONSTRAINT group_to_user_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')


def downgrade():

	# Remove new foreign key reference
	op.drop_constraint('group_to_user_user_id_fkey', 'group_to_user', type_='foreignkey')
	op.drop_constraint('group_to_user_group_id_fkey', 'group_to_user', type_='foreignkey')

	# Drop New Index
	op.drop_index('group2user_idx_user_id_group_id', 'group')

	# Drop date columns
	op.drop_column('group_to_user', 'created_at')
	op.drop_column('group_to_user', 'updated_at')

	# Replacing user id column
	op.alter_column('group_to_user', 'user_id', new_column_name='old_user_id')
	op.add_column('group_to_user', sa.Column('user_id', sa.String))
	op.execute('UPDATE "group_to_user" SET user_id=u.email FROM "user" AS u WHERE u.id = group_to_user.old_user_id;')
	op.drop_column('group_to_user', 'old_user_id')
	op.alter_column('group_to_user', 'user_id', nullable=False)

	# Replacing group id column
	op.alter_column('group_to_user', 'group_id', new_column_name='old_group_id')
	op.add_column('group_to_user', sa.Column('group_id', sa.String))
	op.add_column('group_to_user', sa.Column('group_owner', sa.String))
	op.execute('UPDATE "group_to_user" SET group_id=g.group_id FROM "group" AS g WHERE g.id = old_group_id;')
	op.execute('UPDATE "group_to_user" SET group_owner=g.owner_email FROM "group" AS g WHERE g.id = old_group_id;')
	op.drop_column('group_to_user', 'old_group_id')
	op.alter_column('group_to_user', 'group_id', nullable=False)
	op.alter_column('group_to_user', 'group_owner', nullable=False)

	# Reinstate OLD PKey
	op.execute('ALTER TABLE "group_to_user" ADD PRIMARY KEY (user_id, group_id, group_owner);')


	pass