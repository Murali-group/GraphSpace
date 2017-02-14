"""update edges table - add fkey

Revision ID: 7714db49dc7d
Revises: 3125de4a065f
Create Date: 2017-02-14 12:28:37.919935

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7714db49dc7d'
down_revision = '3125de4a065f'
branch_labels = None
depends_on = None


def upgrade():
	# Add new foreign key reference
	op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_head_node_id_fkey FOREIGN KEY (head_node_id) REFERENCES node (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_tail_node_id_fkey FOREIGN KEY (tail_node_id) REFERENCES node (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')
	op.execute('ALTER TABLE "edge" ADD CONSTRAINT edge_graph_id_fkey FOREIGN KEY (graph_id) REFERENCES graph (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')



def downgrade():
	# Remove new foreign key reference
	op.drop_constraint('edge_head_node_id_fkey', 'edge', type_='foreignkey')
	op.drop_constraint('edge_tail_node_id_fkey', 'edge', type_='foreignkey')
	op.drop_constraint('edge_graph_id_fkey', 'edge', type_='foreignkey')

