"""update password reset table

Revision ID: 3ab443000c7e
Revises: 77a2637f243c
Create Date: 2017-02-13 16:05:47.096824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ab443000c7e'
down_revision = '77a2637f243c'
branch_labels = None
depends_on = None


def upgrade():
	# # password_reset_code
	op.rename_table('password_reset', 'password_reset_code')

	# Add date columns
	op.alter_column('password_reset_code', 'created', new_column_name='created_at', server_default=sa.func.current_timestamp())
	op.add_column('password_reset_code', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))

	# Rename email column
	op.alter_column('password_reset_code', 'user_id', new_column_name='email')

	# Create New Index
	op.create_index('ix_password_reset_code_email_code', 'password_reset_code', ['email', 'code'], unique=True)
	op.create_index('ix_password_reset_code_email', 'password_reset_code', ['email'])

	# Add new foreign key reference
	op.execute('ALTER TABLE "password_reset_code" ADD CONSTRAINT password_reset_code_email_fkey FOREIGN KEY (email) REFERENCES "user" (email) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')


def downgrade():

	op.drop_constraint('password_reset_code_email_fkey', 'password_reset_code', type_='foreignkey')

	# Drop New Index
	op.drop_index('ix_password_reset_code_email_code', 'password_reset_code')
	op.drop_index('ix_password_reset_code_email', 'password_reset_code')

	# Rename email column
	op.alter_column('password_reset_code', 'email', new_column_name='user_id', )

	# Drop date columns
	op.alter_column('password_reset_code', 'created_at', new_column_name='created', server_default=None)
	op.drop_column('password_reset_code', 'updated_at')

	op.rename_table('password_reset_code', 'password_reset')



