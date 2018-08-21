"""create_graph_versions_table

Revision ID: f8f6ba9712df
Revises: bb9a45e2ee5e
Create Date: 2018-06-22 23:08:39.459000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8f6ba9712df'
down_revision = 'bb9a45e2ee5e'
branch_labels = None
depends_on = None


def upgrade():
	op.create_table(
		'graph_version',
		sa.Column('id', sa.Integer, primary_key=True),
		sa.Column('name', sa.String, nullable=False, unique=True),
		sa.Column('graph_id', sa.Integer, nullable=False),
		sa.Column('owner_email', sa.String, nullable=False),
		sa.Column('graph_json', sa.String, nullable=False),
		sa.Column('style_json', sa.String, nullable=False),
		sa.Column('description', sa.String, nullable=False),
	)
	op.add_column('graph_version', sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	op.add_column('graph_version', sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()))
	# Create New Index
	op.create_index('graph_version_idx_name', 'graph_version', ['name'], unique=True)
	# Add new foreign key reference
	op.execute('ALTER TABLE graph_version ADD CONSTRAINT graph_version_graph_id_fkey FOREIGN KEY (graph_id) REFERENCES "graph" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')
	op.execute('ALTER TABLE graph_version ADD CONSTRAINT graph_version_owner_email_fkey FOREIGN KEY (owner_email) REFERENCES "user" (email) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')




def downgrade():
	op.drop_table('graph_version')
