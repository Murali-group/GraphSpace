"""add_table_layout_to_graph_version

Revision ID: 09f74ae3229b
Revises: bb9a45e2ee5e
Create Date: 2018-06-24 17:30:43.566000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09f74ae3229b'
down_revision = 'bb9a45e2ee5e'
branch_labels = None
depends_on = None


def upgrade():
	op.create_table(
		'layout_to_graph_version',
		sa.Column('id', sa.Integer, primary_key=True),
		sa.Column('layout_id', sa.String, nullable=False, unique=True),
		sa.Column('graph_version_id', sa.Integer, nullable=False),
		sa.Column('status', sa.String, nullable=True),
	)
	# Add date columns
	op.add_column('layout_to_graph_version', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.add_column('layout_to_graph_version', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))

	# Add Foreign Keys
	op.execute('ALTER TABLE layout_to_graph_version ADD CONSTRAINT layout_to_graph_version_layout_id_fkey FOREIGN KEY (layout_id) REFERENCES "layout" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')
	op.execute('ALTER TABLE layout_to_graph_version ADD CONSTRAINT layout_to_graph_version_graph_version_id_fkey FOREIGN KEY (graph_version_id) REFERENCES "graph_version" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')


def downgrade():
	op.drop_table('layout_to_graph_version')
