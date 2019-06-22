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
	op.create_table(
		'graph_fork',
		sa.Column('id', sa.Integer, primary_key=True),
		sa.Column('graph_id', sa.Integer, nullable=False),
		sa.Column('parent_graph_id', sa.Integer, nullable=False),
	)
	op.add_column('graph_fork', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.add_column('graph_fork', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	# Create New Index
	op.create_index('graph2fork_idx_graph_id_parent_id', 'graph_fork', ['graph_id', 'parent_graph_id'], unique=True)
	# Add new foreign key reference
	op.execute('ALTER TABLE graph_fork ADD CONSTRAINT fork_graph_id_fkey FOREIGN KEY (graph_id) REFERENCES "graph" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')


def downgrade():
	op.drop_table('graph_fork')
