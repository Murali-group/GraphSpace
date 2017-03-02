"""add invite code column to group table

Revision ID: 9aecafcc7ca3
Revises: 1bce06cc4e3d
Create Date: 2017-02-23 22:29:51.634625

"""
from alembic import op
import sqlalchemy as sa
import string

from django.utils.crypto import random


# revision identifiers, used by Alembic.
def generate_uid(size=20, chars=string.ascii_uppercase + string.digits):
	"""
		Generates an unique alphanumeric ID of specific size.

		:param size: Size of random string
		:param chars: Subset of characters to generate random string of
		:return string: Random string that adhere to the parameter properties
	"""
	return ''.join(random.choice(chars) for _ in range(size))


revision = '9aecafcc7ca3'
down_revision = '1bce06cc4e3d'
branch_labels = None
depends_on = None


grouphelper = sa.Table(
	'group',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
	sa.Column('invite_code', sa.String),
)


def upgrade():
	# we build a quick link for the current connection of alembic
	connection = op.get_bind()

	op.add_column('group', sa.Column('invite_code', sa.String))

	for group in connection.execute(grouphelper.select()):
		invite_code = generate_uid(size=10)
		connection.execute(
			grouphelper.update().where(
				grouphelper.c.id == group.id
			).values(
				invite_code=invite_code
			)
		)

	op.alter_column('group', 'invite_code', nullable=False)


def downgrade():
	op.drop_column('group', 'invite_code')
