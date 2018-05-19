"""add_graph_fork_table

Revision ID: bdce7c016932
Revises: bb9a45e2ee5e
Create Date: 2018-05-19 16:15:09.911000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bdce7c016932'
down_revision = 'bb9a45e2ee5e'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    op.drop_table('graph_fork')
