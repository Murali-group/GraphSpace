"""update_graph_table_migrate_json_to_graph_version

Revision ID: 840db85c5bce
Revises: f8f6ba9712df
Create Date: 2018-06-23 02:27:29.434000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '840db85c5bce'
down_revision = 'f8f6ba9712df'
branch_labels = None
depends_on = None


def upgrade():

	# Drop columns which have been migrated to graph_version table
	op.drop_column('graph', 'style_json')
	op.drop_column('graph', 'graph_json')

	# Add new column for default_graph_version_id
	op.add_column('graph', sa.Column('default_version_id', sa.Integer))

	# Add new foreign key reference
	op.execute('ALTER TABLE graph ADD CONSTRAINT graph_default_version_id_fkey FOREIGN KEY (default_version_id) REFERENCES "graph_version" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')

def downgrade():

	# Add columns which have been migrated to graph_version table
	op.add_column('graph', sa.Column('style_json', sa.String))
	op.add_column('graph', sa.Column('graph_json', sa.String))

	# Remove foreign key reference
	op.drop_constraint('graph_default_version_id_fkey', 'graph', type_='foreignkey')

	# Drop column for default_graph_version_id
	op.drop_column('graph', 'default_version_id')
