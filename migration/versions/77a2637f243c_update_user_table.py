"""update user table

Revision ID: 77a2637f243c
Revises: b4595455cbef
Create Date: 2017-02-13 15:57:40.637890

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77a2637f243c'
down_revision = 'b4595455cbef'
branch_labels = None
depends_on = None


def upgrade():
	# Drop OLD PKey
	op.drop_constraint('user_pkey', 'user', type_='primary')

	# Add new ID Column
	op.execute('ALTER TABLE "user" ADD "id" SERIAL PRIMARY KEY UNIQUE;')

	# Add date columns
	op.add_column('user', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.add_column('user', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))

	# Rename admin column
	op.alter_column('user', 'admin', new_column_name='is_admin')
	op.execute('UPDATE "user" SET is_admin=0 WHERE is_admin is NULL')
	op.alter_column('user', 'is_admin', nullable=False)

	# Rename email column
	op.alter_column('user', 'user_id', new_column_name='email')

	# Create New Index
	op.create_index('ix_user_email', 'user', ['email'], unique=True)


def downgrade():
	# Drop New Index
	op.drop_index('ix_user_email', 'user')

	# Rename email column
	op.alter_column('user', 'email', new_column_name='user_id')

	# Rename admin column
	op.alter_column('user', 'is_admin', new_column_name='admin')

	# Drop date columns
	op.drop_column('user', 'created_at')
	op.drop_column('user', 'updated_at')

	# Drop new ID Column
	op.drop_column('user', 'id')

	# Reinstate OLD PKey
	op.create_primary_key("user_pkey", "user", ["user_id", ])


