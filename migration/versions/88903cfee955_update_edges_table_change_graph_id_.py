"""update edges table - change graph_id column

Revision ID: 88903cfee955
Revises: 53786aa794b4
Create Date: 2017-02-14 11:48:00.812729

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88903cfee955'
down_revision = '53786aa794b4'
branch_labels = None
depends_on = None


def upgrade():
	# # Replacing graph_id, user_id. with graph id in edge table
	op.alter_column('edge', 'graph_id', new_column_name='old_graph_id')
	op.add_column('edge', sa.Column('graph_id', sa.Integer))
	op.execute('UPDATE edge SET graph_id=g.id FROM "graph" AS g WHERE g.name = edge.old_graph_id AND g.owner_email = edge.user_id;')
	op.drop_column('edge', 'old_graph_id')
	op.drop_column('edge', 'user_id')
	op.alter_column('edge', 'graph_id', nullable=False)


def downgrade():
	# # Undo Replacing graph_id, user_id. with graph id in edge table
	op.alter_column('edge', 'graph_id', new_column_name='old_graph_id')
	op.add_column('edge', sa.Column('graph_id', sa.String))
	op.add_column('edge', sa.Column('user_id', sa.String))
	op.execute('UPDATE "edge" SET graph_id=g.name FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.execute('UPDATE "edge" SET user_id=g.owner_email FROM "graph" AS g WHERE g.id = old_graph_id;')
	op.drop_column('edge', 'old_graph_id')
	op.alter_column('edge', 'graph_id', nullable=False)
	op.alter_column('edge', 'user_id', nullable=False)
