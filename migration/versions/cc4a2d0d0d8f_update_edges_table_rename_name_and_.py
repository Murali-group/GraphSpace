"""update edges table - rename name and directed column

Revision ID: cc4a2d0d0d8f
Revises: 4ff58ac07feb
Create Date: 2017-02-14 12:03:37.498551

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc4a2d0d0d8f'
down_revision = '4ff58ac07feb'
branch_labels = None
depends_on = None


def upgrade():
	# Rename name column
	op.alter_column('edge', 'edge_id', new_column_name='name')

	# Rename directed column
	op.alter_column('edge', 'directed', new_column_name='is_directed', nullable=False)



def downgrade():
	# Rename directed column
	op.alter_column('edge', 'is_directed', new_column_name='directed')

	# Undo Rename name column
	op.alter_column('edge', 'name', new_column_name='edge_id')
