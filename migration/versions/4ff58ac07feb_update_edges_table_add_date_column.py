"""update edges table - add date column

Revision ID: 4ff58ac07feb
Revises: 5976898cbe4c
Create Date: 2017-02-14 12:03:06.646026

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ff58ac07feb'
down_revision = '5976898cbe4c'
branch_labels = None
depends_on = None


def upgrade():
    # Add date columns
	op.add_column('edge', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.add_column('edge', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))


def downgrade():
    # Drop date columns
	op.drop_column('edge', 'created_at')
	op.drop_column('edge', 'updated_at')
